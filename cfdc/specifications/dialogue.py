from __future__ import annotations

import ast
import math
import re
from copy import deepcopy
from dataclasses import dataclass
from typing import Any

from cfdc.models import (
    ProfileFactCandidate,
    ProfileFactCandidateAssessment,
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
    normalize_unit_token,
    resolve_unit,
    unit_family,
    unit_is_actuator_per_input,
    unit_is_compatible_with_examples,
)

_NUMBER = r"[-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][-+]?\d+)?"
_SCALAR_UNIT = (
    r"(?:[A-Za-z%°][A-Za-z0-9%°²³*/^()._\-·⋅×]*|"
    r"秒|毫秒|分钟|小时|度|摄氏度|华氏度|伏|安|瓦|牛|千克|帕)"
)


class UnitCompatibilityError(ValueError):
    pass


@dataclass
class LabeledSpecificationParse:
    facts: list[SpecificationFact]
    claimed_fact_ids: set[str]
    rejected_facts: list[str]
    all_nonempty_lines_labeled: bool


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
        for match in pattern.finditer(normalized_text):
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


def extract_range_specification_facts(
    description: SystemDescription,
    template: SpecificationTemplate,
) -> list[SpecificationFact]:
    """Parse explicit input/output ranges without assigning a simulation purpose.

    The parser is deliberately narrow: a single clause must name exactly one signal
    role, contain a range marker, two ordered numeric endpoints, and at least one
    unit. Physical rated ranges are retained as candidate values, while the later
    simulation-boundary gate decides whether their declared purpose is sufficient.
    """

    fields = {field.fact_id: field for field in template.fields}
    source_type = (
        "manufacturer_document"
        if any(
            token in description.text.casefold()
            for token in ("manual", "datasheet", "铭牌", "手册")
        )
        else "user_known_behavior"
    )
    input_signal = (
        r"input|command|actuat|throttle|heater|valve|pump|voltage|current|power|"
        r"force|torque|输入|命令|执行|油门|加热|阀|泵|电压|电流|功率|力|转矩"
    )
    output_signal = (
        r"output|response|speed|temperature|level|position|"
        r"输出|响应|车速|温度|液位|位置"
    )
    range_marker = r"range|limits?|bounds?|boundary|范围|区间|边界|上下限"
    range_pattern = re.compile(
        rf"(?P<lower>{_NUMBER})\s*(?P<lower_unit>{_SCALAR_UNIT})?\s*"
        rf"(?:\bto\b|至|到|~|～|—|–)\s*"
        rf"(?P<upper>{_NUMBER})\s*(?P<upper_unit>{_SCALAR_UNIT})?",
        flags=re.IGNORECASE,
    )
    facts: list[SpecificationFact] = []
    clauses = [
        clause.strip()
        for clause in re.split(
            r"(?:[。;；!?！？\n]+|[,.]\s+|，|\b(?:and|while|whereas)\b|以及|同时|而)",
            description.text,
            flags=re.IGNORECASE,
        )
        if clause.strip()
    ]
    for clause in clauses:
        if re.search(range_marker, clause, flags=re.IGNORECASE) is None:
            continue
        has_input_role = (
            re.search(input_signal, clause, flags=re.IGNORECASE) is not None
        )
        has_output_role = (
            re.search(output_signal, clause, flags=re.IGNORECASE) is not None
        )
        if has_input_role == has_output_role:
            # No role, or two roles competing for one pair of endpoints, is
            # insufficient evidence for assigning input/output bounds.
            continue
        match = range_pattern.search(clause.replace("−", "-"))
        if match is None:
            continue
        lower_unit = match.group("lower_unit") or match.group("upper_unit")
        upper_unit = match.group("upper_unit") or match.group("lower_unit")
        if lower_unit is None or upper_unit is None:
            continue
        lower_unit = lower_unit.rstrip(".")
        upper_unit = upper_unit.rstrip(".")
        bound_ids = (
            ("input_min", "input_max")
            if has_input_role
            else ("output_min", "output_max")
        )
        if any(fact_id not in fields for fact_id in bound_ids):
            continue
        for fact_id, value, unit in (
            (bound_ids[0], match.group("lower"), lower_unit),
            (bound_ids[1], match.group("upper"), upper_unit),
        ):
            try:
                facts.append(
                    _normalize_fact_for_field(
                        SpecificationFact(
                            fact_id=fact_id,
                            value=float(value),
                            unit=unit,
                            source_type=source_type,
                            source_text=clause,
                        ),
                        fields[fact_id],
                    )
                )
            except (UnitCompatibilityError, ValueError):
                continue
    return facts


def _validated_profile_candidate_fact(
    fact: SpecificationFact,
    field,
    source_texts: list[str],
) -> SpecificationFact:
    """Apply the same provenance and unit gates used for selected Profiles."""

    _validate_fact_value_kind(fact, field)
    _validate_direct_fact_source(fact, source_texts)
    _validate_direct_fact_role(fact)
    normalized = _normalize_fact_for_field(fact, field)
    return _verify_registered_derivation(normalized, source_texts=source_texts)


def _merge_profile_candidates(
    candidates: list[ProfileFactCandidate],
    incoming: list[ProfileFactCandidate],
) -> tuple[list[ProfileFactCandidate], list[str]]:
    merged = {
        (candidate.template_id, candidate.fact.fact_id): candidate
        for candidate in candidates
    }
    conflicts: list[str] = []
    for candidate in incoming:
        key = (candidate.template_id, candidate.fact.fact_id)
        previous = merged.get(key)
        if previous is not None and not _same_value(previous.fact, candidate.fact):
            conflicts.append(
                f"'{candidate.template_id}:{candidate.fact.fact_id}' was supplied as "
                f"{previous.fact.value} {previous.fact.unit} and later as "
                f"{candidate.fact.value} {candidate.fact.unit}."
            )
        merged[key] = candidate
    return list(merged.values()), conflicts


def _cross_template_profile_conflicts(
    candidates: list[ProfileFactCandidate],
) -> list[str]:
    by_fact_id: dict[str, list[ProfileFactCandidate]] = {}
    for candidate in candidates:
        by_fact_id.setdefault(candidate.fact.fact_id, []).append(candidate)
    conflicts: list[str] = []
    for fact_id, scoped_candidates in by_fact_id.items():
        first = scoped_candidates[0]
        if all(
            _same_value(first.fact, candidate.fact)
            for candidate in scoped_candidates[1:]
        ):
            continue
        rendered = ", ".join(
            f"{candidate.template_id}={candidate.fact.value} {candidate.fact.unit}"
            for candidate in scoped_candidates
        )
        conflicts.append(
            f"'{fact_id}' has inconsistent candidates across templates: {rendered}."
        )
    return conflicts


def collect_profile_fact_candidates(
    description: SystemDescription,
    *,
    adapter=None,
    previous: ProfileFactCandidateAssessment | None = None,
) -> ProfileFactCandidateAssessment:
    """Extract template-scoped Profile facts from description text.

    This runs before structural Profile selection. Deterministic labeled facts and
    registered physical derivations are authoritative; an optional adapter may
    add natural-language candidates, which are validated against the same gates.
    """

    from cfdc.specifications.templates import default_specification_template_catalog

    templates = default_specification_template_catalog().templates
    template_by_id = {template.template_id: template for template in templates}
    source_texts = [description.text]
    candidates: list[ProfileFactCandidate] = []
    rejected: list[str] = []
    conflicts: list[str] = []
    for template in templates:
        labeled = extract_labeled_specification_facts(description.text, template)
        deterministic = [
            *extract_explicit_specification_facts(description.text, template),
            *extract_range_specification_facts(description, template),
            *labeled.facts,
            *derive_thermostat_specification_facts(
                description, template, description.text
            ),
        ]
        rejected.extend(
            f"{template.template_id}:{item}" for item in labeled.rejected_facts
        )
        local: list[ProfileFactCandidate] = []
        fields = {field.fact_id: field for field in template.fields}
        for fact in deterministic:
            field = fields.get(fact.fact_id)
            if field is None:
                continue
            try:
                normalized = _validated_profile_candidate_fact(
                    fact, field, source_texts
                )
            except (UnitCompatibilityError, ValueError) as exc:
                rejected.append(f"{template.template_id}:{fact.fact_id}: {exc}")
                continue
            local.append(
                ProfileFactCandidate(template_id=template.template_id, fact=normalized)
            )
        candidates, local_conflicts = _merge_profile_candidates(candidates, local)
        conflicts.extend(local_conflicts)

    if adapter is not None and callable(
        getattr(adapter, "extract_profile_facts", None)
    ):
        payload = adapter.extract_profile_facts(
            description.model_copy(deep=True),
            [template.model_copy(deep=True) for template in templates],
            previous.model_copy(deep=True) if previous is not None else None,
        )
        if isinstance(payload, ProfileFactCandidateAssessment):
            payload = payload.model_dump(mode="python")
        if not isinstance(payload, dict):
            raise ValueError("Profile fact extraction must return one JSON object")
        raw_candidates = payload.get("candidates", [])
        if not isinstance(raw_candidates, list):
            raise ValueError("Profile fact candidates must be an array")
        llm_candidates: list[ProfileFactCandidate] = []
        for raw_candidate in raw_candidates:
            try:
                candidate = ProfileFactCandidate.model_validate(raw_candidate)
            except (TypeError, ValueError) as exc:
                rejected.append(f"malformed Profile fact candidate: {exc}")
                continue
            template = template_by_id.get(candidate.template_id)
            if template is None:
                rejected.append(
                    "Profile fact candidate uses unknown template "
                    f"'{candidate.template_id}'"
                )
                continue
            field = next(
                (
                    item
                    for item in template.fields
                    if item.fact_id == candidate.fact.fact_id
                ),
                None,
            )
            if field is None:
                rejected.append(
                    "Profile fact candidate uses unknown field "
                    f"'{candidate.fact.fact_id}' for '{candidate.template_id}'"
                )
                continue
            try:
                normalized = _validated_profile_candidate_fact(
                    candidate.fact, field, source_texts
                )
            except (UnitCompatibilityError, ValueError) as exc:
                rejected.append(
                    f"{candidate.template_id}:{candidate.fact.fact_id}: {exc}"
                )
                continue
            llm_candidates.append(candidate.model_copy(update={"fact": normalized}))
        candidates, llm_conflicts = _merge_profile_candidates(
            candidates, llm_candidates
        )
        conflicts.extend(llm_conflicts)
        raw_conflicts = payload.get("conflicts", [])
        if isinstance(raw_conflicts, list):
            conflicts.extend(str(item) for item in raw_conflicts)
        raw_rejected = payload.get("rejected_facts", [])
        if isinstance(raw_rejected, list):
            rejected.extend(str(item) for item in raw_rejected)

    if previous is not None:
        validated_previous: list[ProfileFactCandidate] = []
        for candidate in previous.candidates:
            template = template_by_id.get(candidate.template_id)
            field = (
                next(
                    (
                        item
                        for item in template.fields
                        if item.fact_id == candidate.fact.fact_id
                    ),
                    None,
                )
                if template is not None
                else None
            )
            if template is None or field is None:
                rejected.append(
                    "Persisted Profile candidate uses an unknown template or field: "
                    f"{candidate.template_id}:{candidate.fact.fact_id}"
                )
                continue
            try:
                normalized = _validated_profile_candidate_fact(
                    candidate.fact, field, source_texts
                )
            except (UnitCompatibilityError, ValueError) as exc:
                rejected.append(
                    f"{candidate.template_id}:{candidate.fact.fact_id}: {exc}"
                )
                continue
            validated_previous.append(candidate.model_copy(update={"fact": normalized}))
        candidates, previous_conflicts = _merge_profile_candidates(
            validated_previous,
            candidates,
        )
        conflicts = [*previous.conflicts, *conflicts, *previous_conflicts]
        rejected.extend(previous.rejected_facts)
    conflicts.extend(_cross_template_profile_conflicts(candidates))
    return ProfileFactCandidateAssessment(
        candidates=candidates,
        conflicts=list(dict.fromkeys(conflicts)),
        rejected_facts=list(dict.fromkeys(rejected)),
    )


def _strip_labeled_line_formatting(line: str) -> str:
    line = re.sub(r"^\s*(?:[-+*]\s+|\d+[.)]\s*)", "", line)
    return line.replace("**", "").replace("__", "").strip()


def _validate_labeled_unit_suffix(suffix: str) -> None:
    suffix = suffix.strip(" \t。．.!！?？;；,，、()[]{}（）［］｛｝\"'“”‘’")
    if not suffix:
        return
    if re.fullmatch(
        r"(?:作为|用作)(?:停止)?(?:下限|上限|边界)",
        suffix,
        flags=re.IGNORECASE,
    ):
        return
    if re.fullmatch(
        r"as\s+(?:the\s+)?(?:stop|lower|upper|boundary)"
        r"(?:\s+(?:limit|bound(?:ary)?))?",
        suffix,
        flags=re.IGNORECASE,
    ):
        return
    raise ValueError("labeled specification has unsupported trailing text after unit")


def _extract_labeled_value_and_unit(body: str) -> tuple[float, str]:
    normalized_body = body.replace("−", "-").replace("–", "-")
    number_match = re.search(_NUMBER, normalized_body)
    if number_match is None:
        raise ValueError("labeled specification is missing a numeric value")
    value = float(number_match.group(0))
    if not math.isfinite(value):
        raise ValueError("labeled specification value must be finite")

    tail = normalized_body[number_match.end() :].strip()
    tail = re.sub(r"[\s。．.!！?？;；,，、]+$", "", tail).strip()
    if not tail:
        raise ValueError("labeled specification is missing a unit")

    binary_alias_match = re.match(
        r"(?:binary\s+command(?:\s+level)?|二值命令档位|个二值命令档位)",
        tail,
        flags=re.IGNORECASE,
    )
    if binary_alias_match is not None:
        suffix = tail[binary_alias_match.end() :]
        if re.search(_NUMBER, suffix):
            raise ValueError(
                "labeled specification contains more than one independent numeric value"
            )
        _validate_labeled_unit_suffix(suffix)
        return value, binary_alias_match.group(0).strip()

    ascii_unit_match = re.match(
        r"[A-Za-z%°][A-Za-z0-9%°²³*/^()._\-·⋅×]*",
        tail,
    )
    if ascii_unit_match is not None:
        suffix = tail[ascii_unit_match.end() :]
        if re.search(_NUMBER, suffix):
            raise ValueError(
                "labeled specification contains more than one independent numeric value"
            )
        _validate_labeled_unit_suffix(suffix)
        return value, ascii_unit_match.group(0).strip()

    chinese_tail = re.split(
        r"(?:作为|用作|as\s+(?:the\s+)?(?:stop|lower|upper|boundary))",
        tail,
        maxsplit=1,
        flags=re.IGNORECASE,
    )[0]
    chinese_tail = chinese_tail.strip(" \t。．.!！?？;；,，、")
    if not chinese_tail:
        raise ValueError("labeled specification is missing a unit")
    if re.search(_NUMBER, chinese_tail):
        raise ValueError(
            "labeled specification contains more than one independent numeric value"
        )
    return value, chinese_tail


def extract_labeled_specification_facts(
    text: str,
    template: SpecificationTemplate,
) -> LabeledSpecificationParse:
    """Parse one template-labelled numeric specification per input line.

    The original line is retained as the evidence excerpt.  A recognised label
    is considered claimed even when its value is malformed, so the LLM cannot
    silently guess a value for a field the user attempted to answer.
    """

    source_type = (
        "manufacturer_document"
        if any(
            token in text.lower() for token in ("manual", "datasheet", "铭牌", "手册")
        )
        else "user_known_behavior"
    )
    numeric_fields = [
        field for field in template.fields if field.answer_kind == "number"
    ]
    facts: list[SpecificationFact] = []
    claimed_fact_ids: set[str] = set()
    rejected_facts: list[str] = []
    has_nonempty_line = False
    all_nonempty_lines_labeled = True
    for raw_line in text.splitlines():
        normalized_line = _strip_labeled_line_formatting(raw_line)
        if not normalized_line:
            continue
        has_nonempty_line = True
        matched_field = None
        body = ""
        for field in numeric_fields:
            match = re.match(
                rf"^{re.escape(field.label)}\s*[:：]\s*(?P<body>.*)$",
                normalized_line,
                flags=re.IGNORECASE,
            )
            if match is not None:
                matched_field = field
                body = match.group("body")
                break
        if matched_field is None:
            all_nonempty_lines_labeled = False
            continue

        fact_id = matched_field.fact_id
        claimed_fact_ids.add(fact_id)
        try:
            value, unit = _extract_labeled_value_and_unit(body)
            raw_fact = SpecificationFact(
                fact_id=fact_id,
                value=value,
                unit=unit,
                source_type=source_type,
                source_text=raw_line.strip(),
            )
            _validate_direct_fact_source(raw_fact, [text])
            _validate_direct_fact_role(raw_fact)
            fact = _normalize_fact_for_field(raw_fact, matched_field)
        except (UnitCompatibilityError, ValueError) as exc:
            rejected_facts.append(f"{fact_id}: labeled specification rejected: {exc}")
            continue
        facts.append(fact)
    return LabeledSpecificationParse(
        facts=facts,
        claimed_fact_ids=claimed_fact_ids,
        rejected_facts=rejected_facts,
        all_nonempty_lines_labeled=has_nonempty_line and all_nonempty_lines_labeled,
    )


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


def _unresolved_previous_conflicts(
    previous: SpecificationAssessment | None,
    template: SpecificationTemplate,
    addressed_fact_ids: set[str],
) -> list[str]:
    """Keep conflicts until the current reply actually addresses their fields."""

    if previous is None:
        return []
    field_markers = {
        field.fact_id: (field.fact_id.casefold(), field.label.casefold())
        for field in template.fields
    }
    unresolved: list[str] = []
    for conflict in previous.conflicts:
        normalized = conflict.casefold()
        referenced_ids = {
            fact_id
            for fact_id, markers in field_markers.items()
            if any(marker in normalized for marker in markers)
        }
        if referenced_ids & addressed_fact_ids:
            # Rebuilding from the updated facts below will recreate any conflict
            # that the new value did not actually resolve.
            continue
        unresolved.append(conflict)
    return unresolved


def _compact_physical_unit(value: str) -> str:
    return (
        value.casefold()
        .replace("°f", "degf")
        .replace(" ", "")
        .replace("·", "*")
        .replace("⋅", "*")
    )


def _flatten_numeric_values(value) -> list[float]:
    if isinstance(value, float):
        return [value]
    return [number for item in value for number in _flatten_numeric_values(item)]


def _source_contains_unit(source_text: str, unit: str) -> bool:
    normalized_source = (
        source_text.replace("²", "^2")
        .replace("³", "^3")
        .replace("−", "-")
        .replace("·", "*")
        .replace("⋅", "*")
        .replace("×", "*")
    )
    normalized_unit = normalize_unit_token(unit)
    source_aliases = {
        "s": {"s", "sec", "second", "seconds", "秒"},
        "ms": {"ms", "millisecond", "milliseconds", "毫秒"},
        "deg": {"deg", "degree", "degrees", "°", "度"},
        "V": {"V", "volt", "volts", "伏"},
        "A": {"A", "amp", "amps", "安"},
        "W": {"W", "watt", "watts", "瓦"},
        "N": {"N", "newton", "newtons", "牛"},
        "kg": {"kg", "kilogram", "kilograms", "千克"},
        "binary_command": {
            "binary_command",
            "binary command",
            "binary command level",
            "二值命令档位",
            "个二值命令档位",
        },
    }
    candidates = {
        str(unit).strip(),
        normalized_unit,
        *source_aliases.get(normalized_unit, set()),
    }
    for candidate in candidates:
        if not candidate:
            continue
        if candidate[0].isascii() and candidate[0].isalnum():
            prefix = r"(?<![A-Za-z0-9_])"
        elif candidate[0].isalnum():
            prefix = r"(?<=[0-9.\s])"
        else:
            prefix = ""
        suffix = (
            r"(?![A-Za-z0-9_])"
            if candidate[-1].isascii() and candidate[-1].isalnum()
            else ""
        )
        if re.search(
            prefix + re.escape(candidate) + suffix,
            normalized_source,
            flags=re.IGNORECASE,
        ):
            return True
    return False


def _source_contains_fact_value(source_text: str, fact: SpecificationFact) -> bool:
    numeric_source = source_text.replace("−", "-").replace("–", "-")
    attested = [float(value) for value in re.findall(_NUMBER, numeric_source)]
    return all(
        any(
            math.isclose(value, expected, rel_tol=1e-12, abs_tol=1e-12)
            for value in attested
        )
        for expected in _flatten_numeric_values(fact.value)
    )


def _source_contains_normalized_scalar(
    source_text: str, fact: SpecificationFact
) -> bool:
    """Accept unit conversions while retaining the original numeric evidence."""

    if not isinstance(fact.value, float):
        return False
    expected_resolution = resolve_unit(fact.unit)
    unit_pattern = (
        r"(?:[A-Za-z%°][A-Za-z0-9%°²³*/^()._\-·⋅×]*|"
        r"秒|毫秒|分钟|小时|度|摄氏度|华氏度|伏|安|瓦|牛|千克|帕)"
    )
    for match in re.finditer(
        rf"({_NUMBER})\s*({unit_pattern})",
        source_text.replace("−", "-"),
        flags=re.IGNORECASE,
    ):
        try:
            value, canonical_unit = normalize_scalar_unit(
                float(match.group(1)), match.group(2).rstrip(".")
            )
        except (TypeError, ValueError):
            continue
        if canonical_unit == expected_resolution.canonical_unit and math.isclose(
            value, fact.value, rel_tol=1e-9, abs_tol=1e-12
        ):
            return True
    return False


def _source_contains_normalized_range_endpoint(
    source_text: str,
    fact: SpecificationFact,
) -> bool:
    """Verify either endpoint when one range unit applies to both numbers."""

    if not isinstance(fact.value, float):
        return False
    expected = resolve_unit(fact.unit)
    unit_pattern = (
        r"(?:[A-Za-z%°][A-Za-z0-9%°²³*/^()._\-·⋅×]*|"
        r"秒|毫秒|分钟|小时|度|摄氏度|华氏度|伏|安|瓦|牛|千克|帕)"
    )
    pattern = re.compile(
        rf"(?P<lower>{_NUMBER})\s*"
        rf"(?P<lower_unit>(?!to\b){unit_pattern})?\s*"
        rf"(?:\bto\b|至|到|~|～|—|–)\s*"
        rf"(?P<upper>{_NUMBER})\s*(?P<upper_unit>{unit_pattern})?",
        flags=re.IGNORECASE,
    )
    for match in pattern.finditer(source_text.replace("−", "-")):
        shared_unit = match.group("lower_unit") or match.group("upper_unit")
        if shared_unit is None:
            continue
        for group_name in ("lower", "upper"):
            try:
                value, canonical = normalize_scalar_unit(
                    float(match.group(group_name)),
                    shared_unit.rstrip("."),
                )
            except (TypeError, ValueError):
                continue
            if canonical == expected.canonical_unit and math.isclose(
                value,
                fact.value,
                rel_tol=1e-9,
                abs_tol=1e-12,
            ):
                return True
    return False


def _source_contains_compatible_unit(source_text: str, unit: str) -> bool:
    expected = resolve_unit(unit)
    unit_pattern = (
        r"(?:[A-Za-z%°][A-Za-z0-9%°²³*/^()._\-·⋅×]*|"
        r"秒|毫秒|分钟|小时|度|摄氏度|华氏度|伏|安|瓦|牛|千克|帕)"
    )
    for token in re.findall(unit_pattern, source_text, flags=re.IGNORECASE):
        try:
            if (
                resolve_unit(token.rstrip(".")).canonical_unit
                == expected.canonical_unit
            ):
                return True
        except ValueError:
            continue
    return False


def _validate_direct_fact_source(
    fact: SpecificationFact,
    source_texts: list[str],
) -> None:
    if fact.source_type == "derived_from_declared_physics":
        return
    joined_sources = "\n".join(source_texts)
    if fact.source_text not in joined_sources:
        raise ValueError("source_text is not a verbatim user-provided excerpt")
    if re.search(
        r"(?:\b(?:unknown|not known)\b|\bis(?:n't| not)\s+[-+−]?\d|"
        r"\b(?:does not|doesn't)\s+equal\b|\bnot\s+(?:equal to\s+)?[-+−]?\d|"
        r"未知|不知道|不是\s*[-+−]?\d|不等于)",
        fact.source_text,
        flags=re.IGNORECASE,
    ):
        raise ValueError("source excerpt negates or does not establish the value")
    if not (
        _source_contains_fact_value(fact.source_text, fact)
        or _source_contains_normalized_scalar(fact.source_text, fact)
        or _source_contains_normalized_range_endpoint(fact.source_text, fact)
    ):
        raise ValueError("value does not match its source number")
    if not (
        _source_contains_unit(fact.source_text, fact.unit)
        or _source_contains_compatible_unit(fact.source_text, fact.unit)
    ):
        raise ValueError("unit does not match its source unit")


def _validate_direct_fact_role(fact: SpecificationFact) -> None:
    """Prevent a grounded number from being relabeled as another signal role."""

    if fact.source_type == "derived_from_declared_physics":
        return
    input_signal = (
        r"input|command|actuat|throttle|heater|valve|pump|voltage|current|power|"
        r"force|torque|输入|命令|执行|油门|加热|阀|泵|电压|电流|功率|力|转矩"
    )
    output_signal = r"output|response|speed|temperature|level|position|输出|响应|车速|温度|液位|位置"
    role_patterns = {
        "input_change": (
            rf"(?:input_change|{input_signal}).{{0,45}}"
            r"(?:change|step|increment|变化|改变|增量)"
        ),
        "steady_output_change": (
            rf"(?:steady|final|稳态|最终|{output_signal}).{{0,45}}"
            r"(?:change|变化|改变量)"
        ),
        "response_time_s": (
            r"(?:response|63\s*%|time constant|takes?|reach|settling|"
            r"响应|达到|时间常数|需要|稳定时间)"
        ),
        "dead_time_s": r"(?:dead time|delay|wait|silent|时延|延迟|等待|静默)",
        "input_min": (
            rf"(?:(?:input_min|{input_signal}).{{0,45}}"
            r"(?:min|lower|range|下限|范围|最小)|"
            rf"(?:min|lower|range|下限|范围|最小).{{0,45}}(?:{input_signal}|"
            r"[-+−]?\d+(?:\.\d+)?\s*(?:v|a|w|n|nm|normalized_input)))"
        ),
        "input_max": (
            rf"(?:(?:input_max|{input_signal}).{{0,45}}"
            r"(?:max|upper|range|上限|范围|最大)|"
            rf"(?:max|upper|range|上限|范围|最大).{{0,45}}(?:{input_signal}|"
            r"[-+−]?\d+(?:\.\d+)?\s*(?:v|a|w|n|nm|normalized_input)))"
        ),
        "output_min": (
            rf"(?:(?:output_min|{output_signal}).{{0,45}}"
            r"(?:min|lower|range|bound|下限|范围|边界|最小)|"
            rf"(?:min|lower|range|bound|下限|范围|边界|最小).{{0,45}}(?:{output_signal}))"
        ),
        "output_max": (
            rf"(?:(?:output_max|{output_signal}).{{0,45}}"
            r"(?:max|upper|range|bound|上限|范围|边界|最大)|"
            rf"(?:max|upper|range|bound|上限|范围|边界|最大).{{0,45}}(?:{output_signal}))"
        ),
        "oscillation_period_s": r"(?:oscillation_period|period|frequency|peak interval|周期|频率|峰值间隔)",
        "successive_peak_ratio": r"(?:successive_peak_ratio|peak ratio|next peak|相邻峰值|下一峰值)",
        "acceleration_change": r"(?:acceleration_change|acceleration|加速度)",
        "mass_kg": r"(?:mass_kg|effective mass|moving mass|load mass|有效质量|运动质量|负载质量)",
        "stiffness_n_m": r"(?:stiffness_n_m|stiffness|spring constant|刚度|弹簧常数)",
        "damping_n_s_m": r"(?:damping_n_s_m|damping|viscous friction|阻尼|粘性摩擦)",
        "actuator_force_per_input": r"(?:actuator_force_per_input|force per|torque per|每个命令.*(?:力|转矩)|推力|转矩)",
        "motion_time_scale_s": r"(?:motion_time_scale|target change|motion time|takes?|目标变化|运动时间|需要)",
        "inverse_peak_change": r"(?:inverse_peak_change|inverse peak|reverse peak|反向峰值)",
        "inverse_recovery_time_s": r"(?:inverse_recovery_time|recover.*(?:peak|operating point)|反向峰值.*恢复|恢复.*工作点)",
        "complete_numeric_model": r"(?:complete_numeric_model|numeric model|transfer function|state.space|数值模型|传递函数|状态空间)",
        "cart_mass_kg": r"(?:cart_mass_kg|cart mass|小车质量|车体质量)",
        "pole_mass_kg": r"(?:pole_mass_kg|pole mass|rod mass|摆杆质量|杆质量)",
        "com_length_m": r"(?:com_length_m|center of mass length|com length|质心长度|质心距离)",
        "pole_inertia_kg_m2": r"(?:pole_inertia_kg_m2|pole inertia|rod inertia|摆杆惯量|杆转动惯量)",
        "cart_friction_n_s_m": r"(?:cart_friction_n_s_m|cart friction|track friction|小车摩擦|轨道摩擦)",
        "gravity_m_s2": r"(?:gravity_m_s2|gravity|gravitational|重力加速度)",
        "force_limit_n": r"(?:force_limit_n|force limit|maximum force|力限制|最大作用力)",
        "cart_position_limit_m": r"(?:cart_position_limit_m|cart position limit|track limit|小车位置限制|轨道边界)",
        "pitch_inertia_kg_m2": r"(?:pitch_inertia_kg_m2|pitch inertia|俯仰惯量)",
        "linear_drag_n_s_m": r"(?:linear_drag_n_s_m|linear drag|translational drag|线性阻力|平移阻力)",
        "pitch_damping_n_m_s": r"(?:pitch_damping_n_m_s|pitch damping|俯仰阻尼)",
        "thrust_min_n": r"(?:thrust_min_n|minimum thrust|thrust lower|最小推力|推力下限)",
        "thrust_max_n": r"(?:thrust_max_n|maximum thrust|thrust upper|最大推力|推力上限)",
        "torque_limit_n_m": r"(?:torque_limit_n_m|torque limit|maximum torque|转矩限制|最大转矩)",
        "max_tilt_rad": r"(?:max_tilt_rad|maximum tilt|tilt limit|最大倾角|倾角限制)",
        "max_altitude_error": r"(?:max_altitude_error|altitude error|高度误差)",
        "local_gain_matrix": r"(?:local_gain_matrix|local gain matrix|gain matrix|局部增益矩阵|增益矩阵)",
        "local_time_constant_s": r"(?:local_time_constant|local time constant|局部时间常数)",
    }
    pattern = role_patterns.get(fact.fact_id)
    if pattern is None:
        return
    clauses = [
        clause.strip()
        for clause in re.split(
            r"(?:[。;；!?！？\n]+|[,.]\s+|，|\b(?:and|while|whereas)\b|"
            r"以及|同时|而)",
            fact.source_text,
            flags=re.IGNORECASE,
        )
        if clause.strip()
    ]
    role_clauses = [
        clause for clause in clauses if re.search(pattern, clause.casefold())
    ]
    if not role_clauses:
        raise ValueError("source excerpt does not identify the requested signal role")
    if isinstance(fact.value, float) and not any(
        (
            _source_contains_fact_value(clause, fact)
            or _source_contains_normalized_scalar(clause, fact)
            or _source_contains_normalized_range_endpoint(clause, fact)
        )
        and (
            _source_contains_unit(clause, fact.unit)
            or _source_contains_compatible_unit(clause, fact.unit)
        )
        for clause in role_clauses
    ):
        raise ValueError(
            "source value and unit must appear in the same clause as the requested signal role"
        )


def _validate_fact_value_kind(fact: SpecificationFact, field) -> None:
    if field.answer_kind == "number" and not isinstance(fact.value, float):
        raise ValueError(
            f"specification fact '{fact.fact_id}' requires one scalar numeric value"
        )
    if field.answer_kind == "matrix" and not (
        isinstance(fact.value, list)
        and fact.value
        and all(isinstance(row, list) and row for row in fact.value)
    ):
        raise ValueError(
            f"specification fact '{fact.fact_id}' requires a numeric matrix"
        )


def _validate_derivation_sources(
    fact: SpecificationFact, source_texts: list[str]
) -> None:
    assert fact.derivation is not None
    joined = "\n".join(source_texts)
    for excerpt in fact.derivation.source_excerpts:
        if excerpt not in joined:
            raise ValueError(
                f"derivation source for '{fact.fact_id}' is not a verbatim user-provided excerpt"
            )
    for item in fact.derivation.inputs:
        if item.source_text not in joined:
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
                _validate_fact_value_kind(fact, field)
                _validate_direct_fact_source(fact, source_texts)
                normalized = _normalize_fact_for_field(fact, field)
                _validate_direct_fact_role(fact)
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
        rendered = (
            f"{question.prompt} {question.why_needed} "
            f"{question.where_to_find} {question.example}"
        ).lower()
        if any(term in rendered for term in forbidden_user_facing_terms):
            raise ValueError(
                "LLM user-facing specification question exposed an internal field or forbidden test protocol"
            )
        imperative_text = f"{question.prompt} {question.example}"
        if re.search(
            r"(?:^|[.!?。！？]\s*)(?:please\s+)?"
            r"(?:set|apply|increase|decrease|change|step|command|drive|"
            r"actuate|switch|move|run|observe|measure|hold|wait|turn|open|close)\b|"
            r"\b(?:and|then)\s+(?:observe|measure|wait|hold|record)\b|"
            r"(?:^|[。！？]\s*)(?:请)?(?:(?:将|把).{0,25})?"
            r"(?:设置|施加|提高|降低|改变|驱动|操作|启动|打开|关闭|等待|观察|测量)",
            imperative_text,
            flags=re.IGNORECASE,
        ):
            raise ValueError(
                "LLM Profile questions must not instruct physical hardware actions"
            )
        if re.search(
            r"(?:\b(?:apply|command|actuate|switch|move)\b|"
            r"\brun\b.{0,20}\bexperiment\b|施加|下发|驱动|操作|启动)"
            r".{0,80}(?:\d|physical|hardware|actuator|heater|valve|"
            r"实体|硬件|执行器|加热器|阀)",
            rendered,
            flags=re.IGNORECASE,
        ):
            raise ValueError(
                "LLM Profile questions must not instruct physical hardware actions"
            )
        if (
            re.search(
                r"(?:record|manual|log|document|specification|software simulation|"
                r"已有记录|现有记录|手册|日志|文档|规格|软件仿真)",
                question.where_to_find,
                flags=re.IGNORECASE,
            )
            is None
        ):
            raise ValueError(
                "LLM Profile questions require a record-only, manual, or software source"
            )
    # Provider-authored question prose is never retained.  The deterministic
    # template builder below renders the same missing facts as record/manual/
    # software-only prompts, so a model cannot smuggle a hardware procedure into
    # the primary UI through polite or paraphrased wording.
    return assessment.model_copy(update={"questions": []})


def _remove_claimed_fields_from_llm_payload(
    payload: Any,
    claimed_fact_ids: set[str],
) -> Any:
    if not claimed_fact_ids or not isinstance(payload, dict):
        return payload
    prepared = deepcopy(payload)
    raw_facts = prepared.get("facts")
    if isinstance(raw_facts, list):
        prepared["facts"] = [
            item
            for item in raw_facts
            if not isinstance(item, dict) or item.get("fact_id") not in claimed_fact_ids
        ]
    for key in ("missing_fact_ids",):
        values = prepared.get(key)
        if isinstance(values, list):
            prepared[key] = [value for value in values if value not in claimed_fact_ids]
    for key in ("conflicts", "rejected_facts"):
        values = prepared.get(key)
        if isinstance(values, list):
            prepared[key] = [
                value
                for value in values
                if not isinstance(value, str)
                or not any(
                    re.search(rf"\b{re.escape(fact_id)}\b", value)
                    for fact_id in claimed_fact_ids
                )
            ]
    return prepared


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
    labeled = extract_labeled_specification_facts(text, template)
    derived_thermal = derive_thermostat_specification_facts(
        description,
        template,
        "\n".join(history),
    )
    explicit_ids = {fact.fact_id for fact in [*incoming_explicit, *labeled.facts]}
    claimed_fact_ids = explicit_ids | labeled.claimed_fact_ids
    incoming_local = [
        *incoming_explicit,
        *labeled.facts,
        *(fact for fact in derived_thermal if fact.fact_id not in claimed_fact_ids),
    ]
    local_addressed_ids = {fact.fact_id for fact in incoming_local}
    facts, local_conflicts = merge_specification_facts(
        previous.facts if previous else [], incoming_local
    )
    local_assessment = build_initial_specification_assessment(
        description,
        template,
        facts=facts,
        conflicts=[
            *_unresolved_previous_conflicts(
                previous,
                template,
                local_addressed_ids,
            ),
            *local_conflicts,
        ],
    )
    if (incoming_local or labeled.claimed_fact_ids) and local_assessment.status in {
        "ready",
        "conflict",
    }:
        return _with_submission_diagnostics(
            local_assessment,
            previous,
            rejected_facts=labeled.rejected_facts,
        )
    if adapter is not None and hasattr(adapter, "assess_specifications"):
        payload = _remove_claimed_fields_from_llm_payload(
            adapter.assess_specifications(
                description.model_copy(deep=True),
                deepcopy(diagnosis),
                deepcopy(classification),
                method_profile_id or template.method_profile_id,
                [template.model_copy(deep=True)],
                deepcopy(history),
                deepcopy(local_assessment),
            ),
            claimed_fact_ids,
        )
        incoming = validate_specification_assessment_payload(
            payload,
            template=template,
            source_texts=[description.text, *history],
        )
        facts, llm_conflicts = merge_specification_facts(facts, incoming.facts)
        addressed_ids = local_addressed_ids | {fact.fact_id for fact in incoming.facts}
        rebuilt = build_initial_specification_assessment(
            description,
            template,
            facts=facts,
            conflicts=[
                *_unresolved_previous_conflicts(
                    previous,
                    template,
                    addressed_ids,
                ),
                *incoming.conflicts,
                *local_conflicts,
                *llm_conflicts,
            ],
        )
        return _with_submission_diagnostics(
            rebuilt,
            previous,
            rejected_facts=[*labeled.rejected_facts, *incoming.rejected_facts],
        )

    incoming = incoming_local
    if not incoming and not labeled.claimed_fact_ids:
        current = local_assessment
        incoming = _extract_answers_in_question_order(text, template, current)
    facts, fallback_conflicts = merge_specification_facts(facts, incoming)
    addressed_ids = local_addressed_ids | {fact.fact_id for fact in incoming}
    rebuilt = build_initial_specification_assessment(
        description,
        template,
        facts=facts,
        conflicts=[
            *_unresolved_previous_conflicts(
                previous,
                template,
                addressed_ids,
            ),
            *local_conflicts,
            *fallback_conflicts,
        ],
    )
    return _with_submission_diagnostics(
        rebuilt,
        previous,
        rejected_facts=labeled.rejected_facts,
    )
