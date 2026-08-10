from __future__ import annotations

import json
import math
import re
from pathlib import Path
from typing import Any
from uuid import uuid4

from cfdc.diagnosis import (
    OpenAICompatibleDiagnosticAdapter,
    clarification_question_map,
    continue_diagnostic_session,
    start_diagnostic_session,
    submit_evidence_to_session,
)
from cfdc.models import (
    CFDCRunReport,
    ClosedLoopValidationSpec,
    DiagnosticSessionState,
    MeasuredTraceManifest,
    PlantEvidencePackage,
    SimulationBoundaryConfirmation,
    SystemDescription,
)
from cfdc.runtime import run_cfdc_route

ROUTE_CHOICES = {
    "自然语言自动分析（主流程）": "generic",
}

LEGACY_ROUTE_LABELS = {
    "自动选择": "generic",
}


def _textbox_text(value: str | None) -> str:
    return "" if value is None else value


def parse_names(value: str | None) -> list[str]:
    text = _textbox_text(value)
    names = []
    for item in text.replace("、", ",").replace("\n", ",").split(","):
        name = re.sub(r"^(?:and|与|和)\s+", "", item.strip(), flags=re.IGNORECASE)
        if name:
            names.append(name)
    return names


def parse_forbidden_actions(value: str | None) -> list[str]:
    text = _textbox_text(value)
    return [line.strip() for line in text.splitlines() if line.strip()]


def parse_safety_bounds(value: str | None) -> dict[str, float]:
    text = _textbox_text(value)
    bounds: dict[str, float] = {}
    for line in text.replace(",", "\n").splitlines():
        if not line.strip():
            continue
        key, separator, raw = line.partition("=")
        clean_key = key.strip()
        if not separator or not clean_key or not raw.strip():
            raise ValueError(f"安全边界格式错误：{line!r}，应使用 name=value")
        if clean_key in bounds:
            raise ValueError(f"安全边界 {clean_key!r} 重复定义")
        try:
            parsed = float(raw)
        except ValueError as exc:
            raise ValueError(f"安全边界 {clean_key!r} 必须是数字") from exc
        if not math.isfinite(parsed):
            raise ValueError(f"安全边界 {clean_key!r} 必须是有限数字")
        bounds[clean_key] = parsed
    if "max_abs_output_normalized" in bounds:
        value = bounds["max_abs_output_normalized"]
        bounds.setdefault("max_abs_output", value)
        bounds.setdefault("output_min", -value)
        bounds.setdefault("output_max", value)
    if "max_abs_actuator_normalized" in bounds:
        value = bounds["max_abs_actuator_normalized"]
        bounds.setdefault("max_abs_control", value)
        bounds.setdefault("input_min", -value)
        bounds.setdefault("input_max", value)
    return bounds


def parse_time_scale_hint(value: str | float | None) -> float | None:
    if value is None:
        return None
    raw = str(value).strip()
    if not raw:
        return None
    try:
        parsed = float(raw)
    except ValueError as exc:
        raise ValueError("主导时间尺度必须是有限的正数，单位为秒") from exc
    if not math.isfinite(parsed) or parsed <= 0.0:
        raise ValueError("主导时间尺度必须是有限的正数，单位为秒")
    return parsed


def build_adapter(
    use_llm: bool,
    base_url: str | None,
    model: str | None,
    api_key: str | None,
):
    if not use_llm:
        return None
    return OpenAICompatibleDiagnosticAdapter(
        base_url=_textbox_text(base_url).strip() or None,
        model=_textbox_text(model).strip() or None,
        api_key=_textbox_text(api_key).strip() or None,
    )


def _run_ready_session(
    session: DiagnosticSessionState,
    adapter,
    include_trajectory: bool,
) -> CFDCRunReport:
    class SessionReplayAdapter:
        def diagnose(self, description):
            del description
            return session.current_diagnosis.model_dump(mode="json")

        def select_profile(self, description, diagnosis, classification, catalog):
            del description, diagnosis, classification, catalog
            return session.semantic_selection.model_dump(mode="json")

    if session.status == "ready_for_experiments":
        if session.current_diagnosis is None or session.semantic_selection is None:
            raise RuntimeError(
                "ready diagnostic session is missing cached routing evidence"
            )

        return run_cfdc_route(
            session.route_id,
            description=session.accumulated_description,
            diagnostic_adapter=SessionReplayAdapter(),
            include_trajectory=include_trajectory,
        )
    return run_cfdc_route(
        session.route_id,
        diagnostic_session_state=session,
        diagnostic_adapter=adapter,
        include_trajectory=include_trajectory,
    )


def start_app_run(
    description: str | None,
    observed_outputs: str | None,
    actuators: str | None,
    safety_bounds: str | None,
    route_label: str | None,
    use_llm: bool,
    base_url: str | None,
    model: str | None,
    api_key: str | None,
    include_trajectory: bool = False,
    forbidden_actions: str | None = None,
    time_scale_hint_s: str | float | None = None,
) -> tuple[CFDCRunReport, dict[str, Any]]:
    route_id = ROUTE_CHOICES.get(
        route_label,
        LEGACY_ROUTE_LABELS.get(route_label, route_label or "generic"),
    )
    known_route_ids = set(ROUTE_CHOICES.values())
    if route_id not in known_route_ids:
        raise ValueError(f"未知运行方式：{route_label!r}")
    description_text = _textbox_text(description).strip()
    base_url_text = _textbox_text(base_url)
    model_text = _textbox_text(model)
    api_key_text = _textbox_text(api_key)
    if not description_text:
        raise ValueError("请描述需要控制的对象、可观察输出和可用执行器。")
    if route_id == "generic" and not use_llm:
        raise ValueError("通用引导测量流程需要启用 LLM。")
    adapter = build_adapter(use_llm, base_url_text, model_text, api_key_text)

    system = SystemDescription(
        text=description_text,
        observed_outputs=parse_names(observed_outputs),
        actuators=parse_names(actuators),
        safety_bounds=parse_safety_bounds(safety_bounds),
        forbidden_actions=parse_forbidden_actions(forbidden_actions),
        time_scale_hint_s=parse_time_scale_hint(time_scale_hint_s),
    )
    report = run_cfdc_route(
        route_id,
        description=system,
        diagnostic_adapter=adapter,
        include_trajectory=include_trajectory,
    )
    session = report.diagnostic_session
    if report.status in {"need_more_information", "awaiting_specifications"}:
        if report.diagnosis is None:
            raise RuntimeError("incomplete route report is missing its diagnosis")
        if report.status == "awaiting_specifications":
            session = DiagnosticSessionState(
                session_id=f"diagnostic-{uuid4().hex[:16]}",
                route_id=route_id,
                initial_description=system,
                accumulated_description=system,
                current_diagnosis=report.diagnosis,
                classification=report.classification,
                semantic_selection=report.semantic_selection,
                experiment_plan=report.experiment_plan,
                evidence_requirement_plan=report.evidence_requirement_plan,
                specification_templates=report.specification_templates,
                specification_assessment=report.specification_assessment,
                candidate_route=report.candidate_route,
                compiled_route=report.compiled_route,
                pending_clarification_questions=[],
                status="awaiting_specifications",
            )
        else:
            session = start_diagnostic_session(
                system,
                route_id=route_id,
                diagnostic_adapter=adapter,
                diagnosis=report.diagnosis,
            )
        report = report.model_copy(update={"diagnostic_session": session})
    awaiting_llm_dialogue = bool(
        session is not None
        and session.status
        in {
            "collecting_description",
            "awaiting_measurements",
            "measurement_needs_more",
            "measurement_conflict",
            "awaiting_profile_measurements",
            "specification_conflict",
        }
    )
    return report, {
        "session": session.model_dump(mode="json") if session is not None else None,
        "use_llm": use_llm if awaiting_llm_dialogue else False,
        "include_trajectory": include_trajectory,
        "input_source": "natural_language",
    }


def continue_app_run(
    app_state: dict[str, Any],
    answers: list[str | None],
    supplemental_description: str | None,
    *,
    base_url: str | None = None,
    model: str | None = None,
    api_key: str | None = None,
) -> tuple[CFDCRunReport, dict[str, Any]]:
    if not app_state or not app_state.get("session"):
        raise ValueError("当前没有等待回答的诊断会话。")
    session = DiagnosticSessionState.model_validate(app_state["session"])
    adapter = build_adapter(
        bool(app_state.get("use_llm")),
        base_url,
        model,
        api_key,
    )
    question_ids = list(clarification_question_map(session))
    question_map = clarification_question_map(session)
    keyed_answers = {}
    for question_id, answer in zip(question_ids, answers):
        answer_text = _textbox_text(answer).strip()
        if answer_text:
            keyed_answers[question_id] = answer_text
    observed_outputs = list(session.accumulated_description.observed_outputs)
    actuators = list(session.accumulated_description.actuators)
    for question_id, answer in keyed_answers.items():
        question = question_map[question_id].lower()
        if "watch or record" in question and answer not in observed_outputs:
            observed_outputs.append(answer)
        if "physical action or device" in question and answer not in actuators:
            actuators.append(answer)
    if (
        observed_outputs != session.accumulated_description.observed_outputs
        or actuators != session.accumulated_description.actuators
    ):
        session = session.model_copy(
            update={
                "accumulated_description": session.accumulated_description.model_copy(
                    update={
                        "observed_outputs": observed_outputs,
                        "actuators": actuators,
                    }
                )
            }
        )
    updated = continue_diagnostic_session(
        session,
        keyed_answers,
        supplemental_description=_textbox_text(supplemental_description).strip()
        or None,
        expected_revision=session.revision,
        diagnostic_adapter=adapter,
    )
    report = _run_ready_session(
        updated,
        adapter,
        bool(app_state.get("include_trajectory")),
    )
    if updated.status == "collecting_information":
        report = report.model_copy(update={"diagnostic_session": updated})
    next_state = dict(app_state)
    next_state["session"] = (
        updated.model_dump(mode="json")
        if updated.status
        in {
            "collecting_information",
            "awaiting_specifications",
            "need_more_specifications",
            "specification_conflict",
            "evidence_rejected",
        }
        else None
    )
    if next_state["session"] is None:
        next_state["use_llm"] = False
    return report, next_state


def submit_app_measurement_response(
    app_state: dict[str, Any],
    measurement_response: str | None,
    *,
    base_url: str | None = None,
    model: str | None = None,
    api_key: str | None = None,
    simulation_bounds_confirmed: bool = False,
) -> tuple[CFDCRunReport, dict[str, Any]]:
    """Advance diagnostic records or profile facts through the shared textbox."""

    if not app_state or not app_state.get("session"):
        raise ValueError("当前没有等待测量记录的诊断会话。")
    session = DiagnosticSessionState.model_validate(app_state["session"])
    text = _textbox_text(measurement_response).strip()
    if not text:
        raise ValueError("请填写现有记录、手册摘录或明确说明未知。")
    adapter = build_adapter(
        bool(app_state.get("use_llm")), base_url, model, api_key
    )
    if adapter is None:
        raise ValueError("通用引导测量流程需要启用 LLM。")
    report = run_cfdc_route(
        session.route_id,
        diagnostic_session_state=session,
        diagnostic_adapter=adapter,
        measurement_response=text,
        simulation_bounds_confirmed=simulation_bounds_confirmed,
        include_trajectory=bool(app_state.get("include_trajectory")),
    )
    waiting = report.status in {
        "awaiting_measurements",
        "measurement_needs_more",
        "measurement_conflict",
        "awaiting_profile_measurements",
        "specification_conflict",
        "awaiting_evidence",
        "evidence_rejected",
    }
    next_state = dict(app_state)
    next_state["session"] = (
        report.diagnostic_session.model_dump(mode="json")
        if waiting and report.diagnostic_session is not None
        else None
    )
    if next_state["session"] is None:
        next_state["use_llm"] = False
    return report, next_state


def _session_replay_adapter(session: DiagnosticSessionState):
    class SessionReplayAdapter:
        def diagnose(self, description):
            del description
            return session.current_diagnosis.model_dump(mode="json")

        def select_profile(self, description, diagnosis, classification, catalog):
            del description, diagnosis, classification, catalog
            return session.semantic_selection.model_dump(mode="json")

    return SessionReplayAdapter()


def _record_simulation_boundary_confirmation(
    session: DiagnosticSessionState,
    confirmed: bool,
) -> DiagnosticSessionState:
    description = session.accumulated_description
    if description.simulation_boundary_confirmation is not None:
        return session
    if not confirmed:
        raise ValueError(
            "提交用户规格或模型前，请确认所填范围仅作为本次软件仿真的运行/停止边界；"
            "该确认不代表真实硬件安全认证，也不授权下发硬件命令。"
        )
    updated_description = description.model_copy(
        update={"simulation_boundary_confirmation": SimulationBoundaryConfirmation()}
    )
    return session.model_copy(update={"accumulated_description": updated_description})


def submit_app_specifications(
    app_state: dict[str, Any],
    specification_text: str | None,
    simulation_bounds_confirmed: bool = False,
    *,
    base_url: str | None = None,
    model: str | None = None,
    api_key: str | None = None,
) -> tuple[CFDCRunReport, dict[str, Any]]:
    """Advance the ordinary-user natural-language specification dialogue."""

    if not app_state or not app_state.get("session"):
        raise ValueError("当前没有等待设备规格的诊断会话。")
    session = DiagnosticSessionState.model_validate(app_state["session"])
    if session.status not in {
        "awaiting_profile_measurements",
        "specification_conflict",
    }:
        raise ValueError("当前诊断会话不处于设备规格补充阶段。")
    session = _record_simulation_boundary_confirmation(
        session,
        simulation_bounds_confirmed,
    )
    text = _textbox_text(specification_text).strip()
    if not text:
        raise ValueError("请填写已知设备规格、手册原文或明确选择暂时不知道。")
    adapter = build_adapter(
        bool(app_state.get("use_llm")),
        base_url,
        model,
        api_key,
    )
    report = run_cfdc_route(
        session.route_id,
        diagnostic_session_state=session,
        diagnostic_adapter=adapter,
        measurement_response=text,
        include_trajectory=bool(app_state.get("include_trajectory")),
    )
    waiting = report.status in {
        "awaiting_profile_measurements",
        "specification_conflict",
    }
    next_state = dict(app_state)
    next_state["session"] = (
        report.diagnostic_session.model_dump(mode="json")
        if waiting and report.diagnostic_session is not None
        else None
    )
    if not waiting:
        next_state["use_llm"] = False
    return report, next_state


def _read_json_submission_source(
    uploaded_json, pasted_json: str | None
) -> dict[str, Any]:
    uploaded = (
        uploaded_json is not None
        and str(getattr(uploaded_json, "name", uploaded_json)).strip() != ""
    )
    pasted = bool(_textbox_text(pasted_json).strip())
    if not uploaded and not pasted:
        raise ValueError("请选择一种 JSON 提交方式：上传 .json 文件或粘贴 JSON 数据。")
    if uploaded and pasted:
        raise ValueError("上传文件和粘贴内容只能选择一种，以免提交来源不明确。")
    if uploaded:
        path = Path(str(getattr(uploaded_json, "name", uploaded_json)))
        if path.suffix.lower() != ".json":
            raise ValueError("上传文件必须使用 .json 扩展名。")
        try:
            if path.stat().st_size > 5_000_000:
                raise ValueError("JSON 文件不能超过 5 MB。")
            source = path.read_text(encoding="utf-8")
        except OSError as exc:
            raise ValueError(f"无法读取上传的 JSON 文件：{exc}") from None
    else:
        source = _textbox_text(pasted_json).strip()
    try:
        payload = json.loads(source)
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"JSON 格式无效：第 {exc.lineno} 行第 {exc.colno} 列。"
        ) from None
    if not isinstance(payload, dict):
        raise ValueError("JSON 顶层必须是对象。")
    return payload


def _specification_facts_to_text(
    session: DiagnosticSessionState,
    facts_payload: Any,
) -> str:
    if not isinstance(facts_payload, list) or not facts_payload:
        raise ValueError("specification_facts 必须是非空数组。")
    allowed_ids = {
        field.fact_id
        for template in session.specification_templates
        for field in template.fields
    }
    rendered: list[str] = []
    seen: set[str] = set()
    for index, item in enumerate(facts_payload, 1):
        if not isinstance(item, dict):
            raise ValueError(f"specification_facts[{index}] 必须是对象。")
        fact_id = item.get("fact_id")
        value = item.get("value")
        unit = item.get("unit")
        if not isinstance(fact_id, str) or fact_id not in allowed_ids:
            raise ValueError(
                f"specification_facts[{index}] 的 fact_id 不属于当前规格模板。"
            )
        if fact_id in seen:
            raise ValueError(f"specification_facts 中重复定义了 {fact_id!r}。")
        if (
            isinstance(value, bool)
            or not isinstance(value, (int, float))
            or not math.isfinite(float(value))
        ):
            raise ValueError(f"specification_facts[{index}] 的 value 必须是有限数值。")
        if (
            not isinstance(unit, str)
            or not unit.strip()
            or ";" in unit
            or any(character.isspace() for character in unit.strip())
            or re.search(r"[\x00-\x1f]", unit)
        ):
            raise ValueError(
                f"specification_facts[{index}] 的 unit 必须是无空白的单一单位标记。"
            )
        seen.add(fact_id)
        rendered.append(f"{fact_id}={float(value):.17g} {unit.strip()};")
    return " ".join(rendered)


def submit_app_json(
    app_state: dict[str, Any],
    *,
    uploaded_json,
    pasted_json: str | None,
    simulation_bounds_confirmed: bool = False,
    base_url: str | None = None,
    model: str | None = None,
    api_key: str | None = None,
) -> tuple[CFDCRunReport, dict[str, Any]]:
    """Submit a dataset wrapper, a bare executable model, or specification facts."""

    payload = _read_json_submission_source(uploaded_json, pasted_json)
    if not app_state or not app_state.get("session"):
        raise ValueError("当前没有等待 JSON 数据的诊断会话。")
    session = DiagnosticSessionState.model_validate(app_state["session"])
    session = _record_simulation_boundary_confirmation(
        session,
        simulation_bounds_confirmed,
    )
    confirmed_state = dict(app_state)
    confirmed_state["session"] = session.model_dump(mode="json")

    # Dataset wrappers intentionally carry both a model and specification facts.
    # At the specification stage, use the facts first so the ordinary compiler
    # preserves its safety bounds and provenance. Bare/full-model JSON remains a
    # supported advanced path below.
    if payload.get("specification_facts"):
        return submit_app_specifications(
            confirmed_state,
            _specification_facts_to_text(session, payload["specification_facts"]),
            simulation_bounds_confirmed=True,
            base_url=base_url,
            model=model,
            api_key=api_key,
        )

    model_payload = payload if "kind" in payload else payload.get("model")
    if model_payload is not None:
        validation_payload = payload.get("validation_spec")
        if validation_payload is None:
            validation_payload = payload.get("validation")
        return submit_app_evidence(
            confirmed_state,
            model_json=json.dumps(model_payload, ensure_ascii=False),
            trace_files=None,
            trace_manifest_json="",
            validation_json=(
                json.dumps(validation_payload, ensure_ascii=False)
                if validation_payload is not None
                else ""
            ),
            demo_confirmed=False,
            simulation_bounds_confirmed=True,
        )

    raise ValueError(
        "JSON 必须包含 model、specification_facts，或本身就是带 kind 的完整数值模型。"
    )


def submit_app_evidence(
    app_state: dict[str, Any],
    *,
    model_json: str | None,
    trace_files,
    trace_manifest_json: str | None,
    validation_json: str | None,
    demo_confirmed: bool,
    simulation_bounds_confirmed: bool = False,
) -> tuple[CFDCRunReport, dict[str, Any]]:
    """Parse structured UI evidence and resume the cached diagnostic route."""

    if not app_state or not app_state.get("session"):
        raise ValueError("当前没有等待对象证据的诊断会话。")
    session = DiagnosticSessionState.model_validate(app_state["session"])
    if session.status not in {
        "awaiting_specifications",
        "need_more_specifications",
        "specification_conflict",
        "awaiting_evidence",
        "evidence_rejected",
    }:
        raise ValueError("当前诊断会话不处于对象证据收集阶段。")
    adapter = _session_replay_adapter(session)
    if demo_confirmed:
        if (
            (model_json or "").strip()
            or trace_files
            or (trace_manifest_json or "").strip()
            or (validation_json or "").strip()
        ):
            raise ValueError("标准对象演示不能与用户模型或实测数据同时提交。")
        report = run_cfdc_route(
            session.route_id,
            description=session.accumulated_description,
            diagnostic_adapter=adapter,
            include_trajectory=bool(app_state.get("include_trajectory")),
            execution_mode="demo_fixture",
        )
        next_state = dict(app_state)
        next_state["session"] = None
        return report, next_state

    session = _record_simulation_boundary_confirmation(
        session,
        simulation_bounds_confirmed,
    )

    try:
        model_payload = json.loads(model_json) if (model_json or "").strip() else None
        manifest_payload = (
            json.loads(trace_manifest_json)
            if (trace_manifest_json or "").strip()
            else []
        )
        if isinstance(manifest_payload, dict):
            manifest_payload = manifest_payload.get("measured_traces", [])
        file_paths = []
        for item in trace_files or []:
            file_paths.append(str(getattr(item, "name", item)))
        if len(file_paths) != len(manifest_payload):
            raise ValueError("每个实测 manifest 都必须一一对应界面中上传的 CSV。")
        manifests = []
        for index, item in enumerate(manifest_payload):
            payload = dict(item)
            # Never trust a browser-provided server path.  The path is always
            # replaced by the file object created by Gradio's upload handler.
            payload["csv_path"] = file_paths[index]
            manifests.append(MeasuredTraceManifest.model_validate(payload))
        validation = (
            ClosedLoopValidationSpec.model_validate_json(validation_json)
            if (validation_json or "").strip()
            else None
        )
        package = PlantEvidencePackage.model_validate(
            {
                "plant_id": session.evidence_requirement_plan.plant_id,
                "model": model_payload,
                "measured_traces": manifests,
                "validation_spec": validation,
                "provenance": ["Gradio structured object evidence"],
            }
        )
    except (ValueError, TypeError, KeyError, json.JSONDecodeError) as exc:
        raise ValueError(f"对象证据格式无效：{exc}") from None

    reviewed = submit_evidence_to_session(session, package)
    report = run_cfdc_route(
        session.route_id,
        description=session.accumulated_description,
        diagnostic_adapter=adapter,
        include_trajectory=bool(app_state.get("include_trajectory")),
        evidence_package=package,
    )
    next_state = dict(app_state)
    next_state["session"] = (
        reviewed.model_dump(mode="json")
        if report.status in {"awaiting_evidence", "evidence_rejected"}
        else None
    )
    return report, next_state
