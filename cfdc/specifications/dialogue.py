from __future__ import annotations

import ast
import math
import re
from typing import Any

from cfdc.models import (
    SpecificationAssessment,
    SpecificationDerivation,
    SpecificationDerivationInput,
    SpecificationFact,
    SpecificationQuestion,
    SpecificationTemplate,
    SystemDescription,
)
from cfdc.specifications.units import (
    normalize_scalar_unit,
    resolve_unit,
    unit_family,
    unit_is_actuator_per_input,
    unit_is_compatible_with_examples,
)

_NUMBER = r"[-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][-+]?\d+)?"


class UnitCompatibilityError(ValueError):
    pass


def _dynamic_output_names(description: SystemDescription) -> list[str]:
    discrete_markers = (
        " state",
        "state ",
        "status",
        "switch",
        "relay",
        "command",
        "状态",
        "开关",
        "继电器",
        "命令",
    )
    dynamic = [
        name
        for name in description.observed_outputs
        if not any(marker in f" {name.casefold()} " for marker in discrete_markers)
    ]
    return dynamic or description.observed_outputs


def _render_question(
    field,
    description: SystemDescription,
) -> SpecificationQuestion:
    input_name = "、".join(description.actuators) or "执行器输入"
    output_name = "、".join(_dynamic_output_names(description)) or "测量输出"
    substitutions = {"input": input_name, "output": output_name}
    return SpecificationQuestion(
        question_id=f"spec_{field.fact_id}",
        requested_fact_ids=[field.fact_id],
        prompt=field.prompt_template.format(**substitutions),
        why_needed=field.why_needed.format(**substitutions),
        where_to_find=field.where_to_find.format(**substitutions),
        answer_kind=field.answer_kind,
        unit_hint=(
            "请填写实际单位；例如 "
            + " / ".join(field.accepted_units)
            + "。设备自定义命令或传感器单位也可以填写，但相关数值必须使用一致单位。"
            if field.unit_policy == "open"
            else "请填写单位；例如 " + " / ".join(field.accepted_units)
        ),
        example=field.example_template.format(**substitutions),
    )


def _fact_map(facts: list[SpecificationFact]) -> dict[str, SpecificationFact]:
    return {item.fact_id: item for item in facts}


def _fact_signature(facts: list[SpecificationFact]) -> dict[str, tuple[Any, str]]:
    return {item.fact_id: (item.value, item.unit) for item in facts}


def _with_submission_diagnostics(
    assessment: SpecificationAssessment,
    previous: SpecificationAssessment | None,
    *,
    rejected_facts: list[str] | None = None,
) -> SpecificationAssessment:
    rejected = list(rejected_facts or [])
    no_progress = bool(
        previous is not None
        and previous.status == assessment.status == "need_more"
        and _fact_signature(previous.facts) == _fact_signature(assessment.facts)
        and previous.missing_fact_ids == assessment.missing_fact_ids
    )
    rationale = assessment.rationale
    if no_progress:
        rationale = (
            "本次提交未增加可验证规格；系统保留已确认事实，并仅报告仍存在的缺口。"
        )
    return assessment.model_copy(
        update={
            "rejected_facts": rejected,
            "no_progress": no_progress,
            "rationale": rationale,
        }
    )


def _normalize_fact_for_field(fact: SpecificationFact, field) -> SpecificationFact:
    resolution = resolve_unit(fact.unit)
    if field.unit_policy == "dimensioned" and not unit_is_compatible_with_examples(
        fact.unit, field.accepted_units
    ):
        raise UnitCompatibilityError(
            f"unit '{fact.unit}' is dimensionally incompatible with specification "
            f"fact '{fact.fact_id}'; expected examples include "
            + ", ".join(field.accepted_units)
            + "."
        )
    if field.unit_policy == "actuator_per_input" and not unit_is_actuator_per_input(
        fact.unit
    ):
        raise UnitCompatibilityError(
            f"unit '{fact.unit}' for '{fact.fact_id}' must describe force or torque "
            "per explicit actuator-command unit."
        )
    if field.unit_policy == "motion_acceleration" and not (
        resolution.dimension in {"linear_acceleration", "angular_acceleration"}
        or resolution.dimension.startswith("second_derivative:")
    ):
        raise UnitCompatibilityError(
            f"unit '{fact.unit}' for '{fact.fact_id}' must describe position or angle "
            "change per second squared."
        )
    if field.unit_policy == "structured" and resolution.canonical_unit not in {
        resolve_unit(item).canonical_unit for item in field.accepted_units
    }:
        raise UnitCompatibilityError(
            f"unit '{fact.unit}' is incompatible with structured fact '{fact.fact_id}'."
        )

    updates: dict[str, Any] = {"unit": resolution.canonical_unit}
    if isinstance(fact.value, float):
        value, canonical = normalize_scalar_unit(fact.value, fact.unit)
        updates.update({"value": value, "unit": canonical})
        if fact.lower_bound is not None:
            updates["lower_bound"] = fact.lower_bound * resolution.scale
        if fact.upper_bound is not None:
            updates["upper_bound"] = fact.upper_bound * resolution.scale
    return fact.model_copy(update=updates)


def _cross_fact_unit_conflicts(facts: list[SpecificationFact]) -> list[str]:
    known = _fact_map(facts)
    groups = [
        ("input", ["input_change", "input_min", "input_max"]),
        (
            "output",
            [
                "steady_output_change",
                "inverse_peak_change",
                "output_min",
                "output_max",
            ],
        ),
    ]
    conflicts: list[str] = []
    for label, fact_ids in groups:
        supplied = [known[fact_id] for fact_id in fact_ids if fact_id in known]
        if len(supplied) < 2:
            continue
        families = {unit_family(item.unit) for item in supplied}
        if len(families) > 1:
            rendered = ", ".join(f"{item.fact_id}={item.unit}" for item in supplied)
            conflicts.append(
                f"The declared {label} specifications use incompatible units: {rendered}. "
                "Use one unit consistently or provide the conversion relationship."
            )
    return conflicts


def _bound_order_conflicts(facts: list[SpecificationFact]) -> list[str]:
    known = _fact_map(facts)
    conflicts: list[str] = []
    for lower_id, upper_id in (
        ("input_min", "input_max"),
        ("output_min", "output_max"),
        ("thrust_min_n", "thrust_max_n"),
    ):
        if lower_id not in known or upper_id not in known:
            continue
        lower = known[lower_id].value
        upper = known[upper_id].value
        if isinstance(lower, float) and isinstance(upper, float) and lower >= upper:
            conflicts.append(f"'{lower_id}' must be smaller than '{upper_id}'.")
    return conflicts


def _motion_dimension_conflicts(
    template: SpecificationTemplate,
    facts: list[SpecificationFact],
) -> list[str]:
    if template.compiler_id not in {"double_integrator", "second_order"}:
        return []
    known = _fact_map(facts)
    acceleration = known.get("acceleration_change")
    if acceleration is None:
        return []
    acceleration_dimension = unit_family(acceleration.unit)
    expected_position_dimension = {
        "linear_acceleration": "length",
        "angular_acceleration": "angle",
    }.get(acceleration_dimension)
    if acceleration_dimension.startswith("second_derivative:"):
        expected_position_dimension = acceleration_dimension.removeprefix(
            "second_derivative:"
        )
    if expected_position_dimension is None:
        return []
    output_facts = [
        known[fact_id] for fact_id in ("output_min", "output_max") if fact_id in known
    ]
    output_dimensions = {unit_family(item.unit) for item in output_facts}
    if output_dimensions and output_dimensions != {expected_position_dimension}:
        rendered = ", ".join(f"{item.fact_id}={item.unit}" for item in output_facts)
        suffix = (
            " Provide the conversion relationship between the physical motion and "
            "the declared sensor unit."
            if any(item.startswith("opaque:") for item in output_dimensions)
            else ""
        )
        return [
            (
                "The declared acceleration and position units describe different motion "
                f"dimensions: acceleration_change={acceleration.unit}; {rendered}.{suffix}"
            )
        ]
    return []


def _physical_motion_conflicts(
    template: SpecificationTemplate,
    facts: list[SpecificationFact],
) -> list[str]:
    if template.compiler_id not in {"double_integrator", "second_order"}:
        return []
    known = _fact_map(facts)
    mass = known.get("mass_kg")
    actuator = known.get("actuator_force_per_input")
    if mass is None or actuator is None:
        return []
    mass_dimension = unit_family(mass.unit)
    actuator_dimension = unit_family(actuator.unit)
    if mass_dimension == "mass":
        expected_actuator_prefix = "force_per_"
        expected_output = "length"
        expected_stiffness = "stiffness"
        expected_damping = "viscous_damping"
    elif mass_dimension == "rotational_inertia":
        expected_actuator_prefix = "torque_per_"
        expected_output = "angle"
        expected_stiffness = "rotational_stiffness"
        expected_damping = "rotational_damping"
    else:
        return []
    conflicts: list[str] = []
    if not actuator_dimension.startswith(expected_actuator_prefix):
        actual_actuation = (
            "torque" if actuator_dimension.startswith("torque_per_") else "force"
        )
        conflicts.append(
            "The declared mass/inertia and actuator units belong to different motion "
            f"domains: mass_kg={mass.unit}, actuator_force_per_input={actuator.unit} "
            f"({actual_actuation})."
        )
    output_dimensions = {
        unit_family(known[fact_id].unit)
        for fact_id in ("output_min", "output_max")
        if fact_id in known
    }
    if output_dimensions and output_dimensions != {expected_output}:
        conflicts.append(
            "The physical mass/inertia path requires output bounds in the matching "
            "translation or rotation unit, or an explicit sensor conversion relationship."
        )
    for fact_id, expected in (
        ("stiffness_n_m", expected_stiffness),
        ("damping_n_s_m", expected_damping),
    ):
        if fact_id in known and unit_family(known[fact_id].unit) != expected:
            conflicts.append(
                f"'{fact_id}' is inconsistent with the declared mass/inertia domain."
            )
    return conflicts


def _best_completion_path(
    template: SpecificationTemplate,
    facts: list[SpecificationFact],
):
    known = set(_fact_map(facts))
    return min(
        template.completion_paths,
        key=lambda path: (
            len(set(path.required_fact_ids) - known),
            template.completion_paths.index(path),
        ),
    )


def build_initial_specification_assessment(
    description: SystemDescription,
    template: SpecificationTemplate,
    *,
    facts: list[SpecificationFact] | None = None,
    conflicts: list[str] | None = None,
) -> SpecificationAssessment:
    facts = list(facts or [])
    conflicts = list(conflicts or [])
    conflicts.extend(
        item for item in _cross_fact_unit_conflicts(facts) if item not in conflicts
    )
    conflicts.extend(
        item for item in _bound_order_conflicts(facts) if item not in conflicts
    )
    conflicts.extend(
        item
        for item in _motion_dimension_conflicts(template, facts)
        if item not in conflicts
    )
    conflicts.extend(
        item
        for item in _physical_motion_conflicts(template, facts)
        if item not in conflicts
    )
    path = _best_completion_path(template, facts)
    known = set(_fact_map(facts))
    missing = [item for item in path.required_fact_ids if item not in known]
    fields = {item.fact_id: item for item in template.fields}
    questions = [
        _render_question(fields[fact_id], description) for fact_id in missing[:4]
    ]
    status = "conflict" if conflicts else "ready" if not missing else "need_more"
    return SpecificationAssessment(
        status=status,
        template_id=template.template_id,
        facts=facts,
        missing_fact_ids=missing,
        conflicts=conflicts,
        questions=questions,
        rationale=(
            "All facts required by the selected specification path are explicit."
            if status == "ready"
            else "Conflicting specification values require user correction."
            if status == "conflict"
            else template.user_summary
        ),
    )


def _parse_matrix_fact(
    text: str,
    field,
    source_type: str,
) -> SpecificationFact | None:
    pattern = re.compile(
        rf"\b{re.escape(field.fact_id)}\s*=\s*(\[\s*\[.*?\]\s*\])(?:\s+([^;]+?))?(?:;|$)",
        flags=re.IGNORECASE,
    )
    match = pattern.search(text)
    if match is None:
        return None
    try:
        value = ast.literal_eval(match.group(1))
    except (SyntaxError, ValueError):
        return None
    if not match.group(2):
        return None
    try:
        return _normalize_fact_for_field(
            SpecificationFact(
                fact_id=field.fact_id,
                value=value,
                unit=match.group(2).strip(),
                source_type=source_type,
                source_text=match.group(0).strip(" ;"),
            ),
            field,
        )
    except UnitCompatibilityError:
        return None


def extract_explicit_specification_facts(
    text: str,
    template: SpecificationTemplate,
) -> list[SpecificationFact]:
    """Parse only explicit ``fact_id=value unit`` statements; never quantify adjectives."""

    normalized_text = text.replace("−", "-")
    source_type = (
        "manufacturer_document"
        if any(
            token in normalized_text.lower()
            for token in ("manual", "datasheet", "铭牌", "手册")
        )
        else "user_known_behavior"
    )
    facts: list[SpecificationFact] = []
    for field in template.fields:
        if field.answer_kind == "structured_model":
            continue
        if field.answer_kind == "matrix":
            fact = _parse_matrix_fact(normalized_text, field, source_type)
            if fact is not None:
                facts.append(fact)
            continue
        pattern = re.compile(
            rf"\b{re.escape(field.fact_id)}\s*=\s*({_NUMBER})(?:\s+([^;\s]+))?",
            flags=re.IGNORECASE,
        )
        match = pattern.search(normalized_text)
        if match is None:
            continue
        if not match.group(2):
            continue
        unit = match.group(2).strip()
        unit = unit.rstrip(".")
        try:
            fact = _normalize_fact_for_field(
                SpecificationFact(
                    fact_id=field.fact_id,
                    value=float(match.group(1)),
                    unit=unit,
                    source_type=source_type,
                    source_text=match.group(0).strip(),
                ),
                field,
            )
        except UnitCompatibilityError:
            continue
        facts.append(fact)
    return facts


def _extract_number_and_source_after_label(
    text: str,
    labels: list[str],
    unit_pattern: str,
) -> tuple[float, str] | None:
    label_pattern = "|".join(labels)
    match = re.search(
        rf"(?:{label_pattern})\s*(?:[a-z_]+\s*=\s*)?({_NUMBER})\s*{unit_pattern}",
        text,
        flags=re.IGNORECASE,
    )
    return (
        (float(match.group(1)), match.group(0).strip()) if match is not None else None
    )


def derive_thermostat_specification_facts(
    description: SystemDescription,
    template: SpecificationTemplate,
    text: str,
) -> list[SpecificationFact]:
    """Derive a complete first-order thermal plant from explicit physical values.

    The derivation is intentionally narrow: all five physical quantities and their
    units must be present. No default value is introduced.
    """

    if template.compiler_id not in {"first_order", "first_order_delay"}:
        return []
    combined = f"{description.text}\n{text}"
    thermal_context = any(
        token in combined.lower()
        for token in ("thermostat", "heater", "furnace", "恒温器", "加热", "炉子")
    )
    binary_context = any(
        token in combined.lower()
        for token in ("binary", "on/off", "heater state", "二值", "开关", "炉子开启")
    )
    if not thermal_context or not binary_context:
        return []

    degf = r"(?:degf|°f)"
    heat_capacity_match = _extract_number_and_source_after_label(
        text,
        [r"等效热容\s*(?:c\s*=\s*)?", r"heat\s+capacity\s*(?:c\s*=\s*)?"],
        rf"btu\s*/\s*{degf}",
    )
    heat_transfer_match = _extract_number_and_source_after_label(
        text,
        [
            r"传热系数\s*(?:h\s*=\s*)?",
            r"heat\s+(?:transfer|loss)\s+coefficient\s*(?:h\s*=\s*)?",
        ],
        rf"btu\s*/\s*\(\s*h\s*(?:\*|\s)\s*{degf}\s*\)",
    )
    furnace_rate_match = _extract_number_and_source_after_label(
        text,
        [
            r"炉子供热率\s*(?:q_h\s*=\s*)?",
            r"furnace\s+(?:heating\s+)?rate\s*(?:q_h\s*=\s*)?",
        ],
        r"btu\s*/\s*h",
    )
    setpoint_match = _extract_number_and_source_after_label(
        text,
        [r"(?:白天)?设定值", r"setpoint"],
        degf,
    )
    hysteresis_half_width_match = _extract_number_and_source_after_label(
        text,
        [r"滞环半宽", r"hysteresis\s+half[- ]width"],
        degf,
    )
    values = (
        heat_capacity_match,
        heat_transfer_match,
        furnace_rate_match,
        setpoint_match,
        hysteresis_half_width_match,
    )
    if any(value is None for value in values):
        return []
    assert heat_capacity_match is not None
    assert heat_transfer_match is not None
    assert furnace_rate_match is not None
    assert setpoint_match is not None
    assert hysteresis_half_width_match is not None
    heat_capacity, heat_capacity_source = heat_capacity_match
    heat_transfer, heat_transfer_source = heat_transfer_match
    furnace_rate, furnace_rate_source = furnace_rate_match
    setpoint, setpoint_source = setpoint_match
    hysteresis_half_width, hysteresis_source = hysteresis_half_width_match
    if min(heat_capacity, heat_transfer, furnace_rate, hysteresis_half_width) <= 0.0:
        return []

    field_map = {field.fact_id: field for field in template.fields}
    binary_source = next(
        (
            name
            for name in [*description.actuators, *description.observed_outputs]
            if any(
                token in name.casefold()
                for token in ("binary", "on/off", "二值", "开关")
            )
        ),
        None,
    )
    if binary_source is None:
        binary_match = re.search(
            r"binary|on/off|二值|开关", combined, flags=re.IGNORECASE
        )
        if binary_match is None:
            return []
        binary_source = binary_match.group(0)

    input_change_derivation = SpecificationDerivation(
        rule_id="binary_command_domain",
        expression="binary command domain {0, 1}",
        source_excerpts=[binary_source],
    )
    thermal_time_derivation = SpecificationDerivation(
        rule_id="thermal_time_constant_c_over_h",
        expression="3600 * heat_capacity / heat_transfer_coefficient",
        inputs=[
            SpecificationDerivationInput(
                name="heat_capacity",
                value=heat_capacity,
                unit="Btu/degF",
                source_text=heat_capacity_source,
            ),
            SpecificationDerivationInput(
                name="heat_transfer_coefficient",
                value=heat_transfer,
                unit="Btu/(h degF)",
                source_text=heat_transfer_source,
            ),
        ],
        source_excerpts=[heat_capacity_source, heat_transfer_source],
    )
    steady_rise_derivation = SpecificationDerivation(
        rule_id="thermal_steady_rise_q_over_h",
        expression="furnace_rate / heat_transfer_coefficient",
        inputs=[
            SpecificationDerivationInput(
                name="furnace_rate",
                value=furnace_rate,
                unit="Btu/h",
                source_text=furnace_rate_source,
            ),
            SpecificationDerivationInput(
                name="heat_transfer_coefficient",
                value=heat_transfer,
                unit="Btu/(h degF)",
                source_text=heat_transfer_source,
            ),
        ],
        source_excerpts=[furnace_rate_source, heat_transfer_source],
    )
    thermostat_band_derivation = SpecificationDerivation(
        rule_id="thermostat_band_setpoint_plus_minus_half_width",
        expression="setpoint +/- hysteresis_half_width",
        inputs=[
            SpecificationDerivationInput(
                name="setpoint",
                value=setpoint,
                unit="degF",
                source_text=setpoint_source,
            ),
            SpecificationDerivationInput(
                name="hysteresis_half_width",
                value=hysteresis_half_width,
                unit="degF",
                source_text=hysteresis_source,
            ),
        ],
        source_excerpts=[setpoint_source, hysteresis_source],
    )
    derived = {
        "input_change": (1.0, "binary_command", input_change_derivation),
        "steady_output_change": (
            furnace_rate / heat_transfer,
            "degF",
            steady_rise_derivation,
        ),
        "response_time_s": (
            3600.0 * heat_capacity / heat_transfer,
            "s",
            thermal_time_derivation,
        ),
        "input_min": (0.0, "binary_command", input_change_derivation),
        "input_max": (1.0, "binary_command", input_change_derivation),
        "output_min": (
            setpoint - hysteresis_half_width,
            "degF",
            thermostat_band_derivation,
        ),
        "output_max": (
            setpoint + hysteresis_half_width,
            "degF",
            thermostat_band_derivation,
        ),
    }
    facts: list[SpecificationFact] = []
    for fact_id, (value, unit, derivation) in derived.items():
        field = field_map.get(fact_id)
        if field is None:
            continue
        facts.append(
            _normalize_fact_for_field(
                SpecificationFact(
                    fact_id=fact_id,
                    value=value,
                    unit=unit,
                    source_type="derived_from_declared_physics",
                    source_text=f"Verified by {derivation.rule_id}: {derivation.expression}",
                    derivation=derivation,
                ),
                field,
            )
        )
    return facts


def _extract_answers_in_question_order(
    text: str,
    template: SpecificationTemplate,
    assessment: SpecificationAssessment,
) -> list[SpecificationFact]:
    """Fallback form parser: one numeric answer per currently visible question."""

    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if not lines or len(lines) > len(assessment.questions):
        return []
    facts: list[SpecificationFact] = []
    for line, question in zip(lines, assessment.questions):
        if len(question.requested_fact_ids) != 1:
            continue
        fact_id = question.requested_fact_ids[0]
        parsed = extract_explicit_specification_facts(
            f"{fact_id}={line}",
            template,
        )
        if parsed:
            facts.append(parsed[0].model_copy(update={"source_text": line}))
    return facts


def _same_value(left: SpecificationFact, right: SpecificationFact) -> bool:
    return left.value == right.value and left.unit == right.unit


def merge_specification_facts(
    existing: list[SpecificationFact],
    incoming: list[SpecificationFact],
) -> tuple[list[SpecificationFact], list[str]]:
    merged = _fact_map(existing)
    conflicts: list[str] = []
    for fact in incoming:
        previous = merged.get(fact.fact_id)
        if previous is not None and not _same_value(previous, fact):
            conflicts.append(
                f"'{fact.fact_id}' was supplied as {previous.value} {previous.unit} "
                f"and later as {fact.value} {fact.unit}."
            )
        merged[fact.fact_id] = fact
    return list(merged.values()), conflicts


def _compact_physical_unit(value: str) -> str:
    return (
        value.casefold()
        .replace("°f", "degf")
        .replace(" ", "")
        .replace("·", "*")
        .replace("⋅", "*")
    )


def _validate_derivation_sources(
    fact: SpecificationFact, source_texts: list[str]
) -> None:
    assert fact.derivation is not None
    joined = "\n".join(source_texts).casefold()
    for excerpt in fact.derivation.source_excerpts:
        if excerpt.casefold() not in joined:
            raise ValueError(
                f"derivation source for '{fact.fact_id}' is not a verbatim user-provided excerpt"
            )
    for item in fact.derivation.inputs:
        if item.source_text.casefold() not in joined:
            raise ValueError(
                f"derivation input '{item.name}' for '{fact.fact_id}' has no verbatim source"
            )
        numeric_values = [
            float(value) for value in re.findall(_NUMBER, item.source_text)
        ]
        if not any(
            math.isclose(value, item.value, rel_tol=1e-12, abs_tol=1e-12)
            for value in numeric_values
        ):
            raise ValueError(
                f"derivation input '{item.name}' for '{fact.fact_id}' does not match its source number"
            )
        if _compact_physical_unit(item.unit) not in _compact_physical_unit(
            item.source_text
        ):
            raise ValueError(
                f"derivation input '{item.name}' for '{fact.fact_id}' does not match its source unit"
            )


def _registered_derivation_result(fact: SpecificationFact) -> tuple[float, str, str]:
    assert fact.derivation is not None
    rule_id = fact.derivation.rule_id
    inputs = {item.name: item for item in fact.derivation.inputs}
    if len(inputs) != len(fact.derivation.inputs):
        raise ValueError(f"derivation '{rule_id}' contains duplicate input names")

    def require(expected: dict[str, str]) -> dict[str, float]:
        if set(inputs) != set(expected):
            raise ValueError(
                f"derivation '{rule_id}' requires inputs: {', '.join(expected)}"
            )
        values: dict[str, float] = {}
        for name, expected_unit in expected.items():
            item = inputs[name]
            if _compact_physical_unit(item.unit) != _compact_physical_unit(
                expected_unit
            ):
                raise ValueError(
                    f"derivation '{rule_id}' input '{name}' requires unit {expected_unit}"
                )
            if not math.isfinite(item.value):
                raise ValueError(
                    f"derivation '{rule_id}' input '{name}' must be finite"
                )
            values[name] = item.value
        return values

    if rule_id == "thermal_time_constant_c_over_h":
        if fact.fact_id != "response_time_s":
            raise ValueError(f"derivation '{rule_id}' cannot produce '{fact.fact_id}'")
        values = require(
            {
                "heat_capacity": "Btu/degF",
                "heat_transfer_coefficient": "Btu/(h degF)",
            }
        )
        if min(values.values()) <= 0.0:
            raise ValueError(
                f"derivation '{rule_id}' requires positive physical inputs"
            )
        return (
            3600.0 * values["heat_capacity"] / values["heat_transfer_coefficient"],
            "s",
            "3600 * heat_capacity / heat_transfer_coefficient",
        )
    if rule_id == "thermal_steady_rise_q_over_h":
        if fact.fact_id != "steady_output_change":
            raise ValueError(f"derivation '{rule_id}' cannot produce '{fact.fact_id}'")
        values = require(
            {
                "furnace_rate": "Btu/h",
                "heat_transfer_coefficient": "Btu/(h degF)",
            }
        )
        if min(values.values()) <= 0.0:
            raise ValueError(
                f"derivation '{rule_id}' requires positive physical inputs"
            )
        return (
            values["furnace_rate"] / values["heat_transfer_coefficient"],
            "degF",
            "furnace_rate / heat_transfer_coefficient",
        )
    if rule_id == "thermostat_band_setpoint_plus_minus_half_width":
        if fact.fact_id not in {"output_min", "output_max"}:
            raise ValueError(f"derivation '{rule_id}' cannot produce '{fact.fact_id}'")
        values = require({"setpoint": "degF", "hysteresis_half_width": "degF"})
        if values["hysteresis_half_width"] <= 0.0:
            raise ValueError(f"derivation '{rule_id}' requires a positive half-width")
        sign = -1.0 if fact.fact_id == "output_min" else 1.0
        operator = "-" if sign < 0.0 else "+"
        return (
            values["setpoint"] + sign * values["hysteresis_half_width"],
            "degF",
            f"setpoint {operator} hysteresis_half_width",
        )
    if rule_id == "binary_command_domain":
        if inputs:
            raise ValueError(f"derivation '{rule_id}' does not accept numeric inputs")
        expected = {
            "input_change": 1.0,
            "input_min": 0.0,
            "input_max": 1.0,
        }
        if fact.fact_id not in expected:
            raise ValueError(f"derivation '{rule_id}' cannot produce '{fact.fact_id}'")
        context = " ".join(fact.derivation.source_excerpts).casefold()
        if not any(token in context for token in ("binary", "on/off", "二值", "开关")):
            raise ValueError(
                f"derivation '{rule_id}' requires explicit binary-command context"
            )
        return expected[fact.fact_id], "binary_command", "binary command domain {0, 1}"
    raise ValueError(f"unregistered specification derivation rule '{rule_id}'")


def _verify_registered_derivation(
    fact: SpecificationFact,
    *,
    source_texts: list[str],
) -> SpecificationFact:
    if fact.source_type != "derived_from_declared_physics" or fact.derivation is None:
        return fact
    _validate_derivation_sources(fact, source_texts)
    expected_value, expected_unit, expression = _registered_derivation_result(fact)
    normalized_expected, canonical_unit = normalize_scalar_unit(
        expected_value, expected_unit
    )
    if not isinstance(fact.value, float):
        raise ValueError(f"derived specification fact '{fact.fact_id}' must be scalar")
    if fact.unit != canonical_unit or not math.isclose(
        fact.value,
        normalized_expected,
        rel_tol=1e-9,
        abs_tol=1e-12,
    ):
        raise ValueError(
            f"derived specification fact '{fact.fact_id}' does not match backend recomputation "
            f"({normalized_expected:g} {canonical_unit})"
        )
    return fact.model_copy(
        update={
            "value": normalized_expected,
            "unit": canonical_unit,
            "source_text": f"Verified by {fact.derivation.rule_id}: {expression}",
            "derivation": fact.derivation.model_copy(update={"expression": expression}),
        }
    )


def validate_specification_assessment_payload(
    payload: dict[str, Any],
    *,
    template: SpecificationTemplate,
    source_texts: list[str],
) -> SpecificationAssessment:
    fields = {item.fact_id: item for item in template.fields}
    prepared = dict(payload)
    raw_facts = payload.get("facts", [])
    unit_gaps: list[str] = []
    unit_conflicts: list[str] = []
    rejected_fact_ids: list[str] = []
    rejected_facts = list(payload.get("rejected_facts", []))
    joined_sources = "\n".join(source_texts).casefold()
    normalized_facts: list[dict[str, Any]] = []
    if isinstance(raw_facts, list):
        for raw_fact in raw_facts:
            if not isinstance(raw_fact, dict):
                normalized_facts.append(raw_fact)
                continue
            fact_id = raw_fact.get("fact_id")
            field = fields.get(fact_id)
            if field is None:
                raise ValueError(f"LLM returned unknown specification fact '{fact_id}'")
            unit = raw_fact.get("unit")
            if not isinstance(unit, str) or not unit.strip():
                unit_gaps.append(str(fact_id))
                continue
            try:
                fact = SpecificationFact.model_validate(raw_fact)
                normalized = _normalize_fact_for_field(fact, field)
                normalized = _verify_registered_derivation(
                    normalized,
                    source_texts=source_texts,
                )
            except UnitCompatibilityError as exc:
                unit_gaps.append(str(fact_id))
                unit_conflicts.append(str(exc))
                continue
            except ValueError as exc:
                rejected_fact_ids.append(str(fact_id))
                rejected_facts.append(f"{fact_id}: {exc}")
                continue
            if (
                normalized.source_type != "derived_from_declared_physics"
                and normalized.source_text.casefold() not in joined_sources
            ):
                rejected_fact_ids.append(str(fact_id))
                rejected_facts.append(
                    f"{fact_id}: source_text is not a verbatim user-provided excerpt"
                )
                continue
            normalized_facts.append(normalized.model_dump(mode="json"))
        prepared["facts"] = normalized_facts
    if unit_gaps or rejected_fact_ids:
        declared_missing = prepared.get("missing_fact_ids", [])
        if isinstance(declared_missing, list):
            prepared["missing_fact_ids"] = list(
                dict.fromkeys([*declared_missing, *unit_gaps, *rejected_fact_ids])
            )
        if unit_conflicts:
            declared_conflicts = prepared.get("conflicts", [])
            if isinstance(declared_conflicts, list):
                prepared["conflicts"] = [*declared_conflicts, *unit_conflicts]
            prepared["status"] = "conflict"
        else:
            prepared["status"] = "need_more"
    prepared["rejected_facts"] = rejected_facts

    assessment = SpecificationAssessment.model_validate(prepared)
    if assessment.template_id != template.template_id:
        raise ValueError("LLM selected an unknown or disallowed specification template")
    for fact in assessment.facts:
        field = fields.get(fact.fact_id)
        if field is None:
            raise ValueError(
                f"LLM returned unknown specification fact '{fact.fact_id}'"
            )
        if (
            fact.source_type != "derived_from_declared_physics"
            and fact.source_text.casefold() not in joined_sources
        ):
            raise ValueError(
                f"source_text for '{fact.fact_id}' is not a verbatim user-provided excerpt"
            )
    requested = {
        fact_id
        for question in assessment.questions
        for fact_id in question.requested_fact_ids
    }
    if requested - set(fields):
        raise ValueError("LLM question requests facts outside the selected template")
    forbidden_user_facing_terms = {
        "natural_frequency",
        "damping_ratio",
        "input_gain",
        "static_gain",
        "time_constant",
        "local_gain_matrix",
        "pairing_indicator",
        "csv",
        "three times",
        "three repeats",
        "三次",
    }
    for question in assessment.questions:
        rendered = f"{question.prompt} {question.why_needed} {question.where_to_find} {question.example}".lower()
        if any(term in rendered for term in forbidden_user_facing_terms):
            raise ValueError(
                "LLM user-facing specification question exposed an internal field or forbidden test protocol"
            )
    return assessment


def assess_specification_text(
    description: SystemDescription,
    template: SpecificationTemplate,
    text: str,
    *,
    previous: SpecificationAssessment | None = None,
    adapter=None,
    diagnosis=None,
    classification=None,
    method_profile_id: str | None = None,
    answer_history: list[str] | None = None,
) -> SpecificationAssessment:
    history = [*(answer_history or []), text]
    incoming_explicit = extract_explicit_specification_facts(text, template)
    derived_thermal = derive_thermostat_specification_facts(
        description,
        template,
        "\n".join(history),
    )
    explicit_ids = {fact.fact_id for fact in incoming_explicit}
    incoming_local = [
        *incoming_explicit,
        *(fact for fact in derived_thermal if fact.fact_id not in explicit_ids),
    ]
    if adapter is not None and hasattr(adapter, "assess_specifications"):
        payload = adapter.assess_specifications(
            description,
            diagnosis,
            classification,
            method_profile_id or template.method_profile_id,
            [template],
            history,
            previous,
        )
        incoming = validate_specification_assessment_payload(
            payload,
            template=template,
            source_texts=[description.text, *history],
        )
        facts, local_conflicts = merge_specification_facts(
            previous.facts if previous else [], incoming_local
        )
        facts, llm_conflicts = merge_specification_facts(facts, incoming.facts)
        rebuilt = build_initial_specification_assessment(
            description,
            template,
            facts=facts,
            conflicts=[*incoming.conflicts, *local_conflicts, *llm_conflicts],
        )
        if rebuilt.status == "need_more" and incoming.questions:
            missing = set(rebuilt.missing_fact_ids)
            if all(
                set(question.requested_fact_ids).issubset(missing)
                for question in incoming.questions
            ):
                rebuilt = rebuilt.model_copy(update={"questions": incoming.questions})
        return _with_submission_diagnostics(
            rebuilt,
            previous,
            rejected_facts=incoming.rejected_facts,
        )

    incoming = incoming_local
    if not incoming:
        current = previous or build_initial_specification_assessment(
            description,
            template,
        )
        incoming = _extract_answers_in_question_order(text, template, current)
    facts, conflicts = merge_specification_facts(
        previous.facts if previous else [], incoming
    )
    rebuilt = build_initial_specification_assessment(
        description,
        template,
        facts=facts,
        conflicts=conflicts,
    )
    return _with_submission_diagnostics(rebuilt, previous)
