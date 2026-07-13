from __future__ import annotations

import math
from typing import Any

from cfdc.diagnosis import (
    OpenAICompatibleDiagnosticAdapter,
    clarification_question_map,
    continue_diagnostic_session,
    start_diagnostic_session,
)
from cfdc.models import CFDCRunReport, DiagnosticSessionState, SystemDescription
from cfdc.runtime import run_cfdc_route


ROUTE_CHOICES = {
    "自然语言自动分析（主流程）": "generic",
    "开发验证 · CartPole 完整流程": "cartpole",
    "开发验证 · CartPole 安全边界": "cartpole-boundary",
    "开发验证 · VTOL 位置控制": "vtol-position",
    "开发验证 · VTOL 安全边界": "vtol-boundary",
    "开发验证 · VTOL 高度控制": "vtol-altitude",
    "开发验证 · VTOL 悬停控制": "vtol-hover",
    "开发验证 · VTOL 参数变化": "vtol-variation",
}

# Keep old labels valid for saved browser/API calls without showing them in the UI.
LEGACY_ROUTE_LABELS = {
    "自动选择": "generic",
    "CartPole 验证": "cartpole",
    "CartPole 边界": "cartpole-boundary",
    "VTOL 位置控制": "vtol-position",
    "VTOL 安全边界": "vtol-boundary",
    "VTOL 高度控制": "vtol-altitude",
    "VTOL 悬停控制": "vtol-hover",
    "VTOL 参数变化": "vtol-variation",
}


def parse_names(value: str) -> list[str]:
    return [item.strip() for item in value.replace("\n", ",").split(",") if item.strip()]


def parse_safety_bounds(value: str) -> dict[str, float]:
    bounds: dict[str, float] = {}
    for line in value.replace(",", "\n").splitlines():
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
    return bounds


def build_adapter(
    use_llm: bool,
    base_url: str,
    model: str,
    api_key: str,
):
    if not use_llm:
        return None
    return OpenAICompatibleDiagnosticAdapter(
        base_url=base_url.strip() or None,
        model=model.strip() or None,
        api_key=api_key.strip() or None,
    )


def _run_ready_session(
    session: DiagnosticSessionState,
    adapter,
    include_trajectory: bool,
) -> CFDCRunReport:
    if session.status == "ready_for_experiments":
        if session.current_diagnosis is None or session.semantic_selection is None:
            raise RuntimeError("ready diagnostic session is missing cached routing evidence")

        class SessionReplayAdapter:
            def diagnose(self, description):
                del description
                return session.current_diagnosis.model_dump(mode="json")

            def select_profile(self, description, diagnosis, classification, catalog):
                del description, diagnosis, classification, catalog
                return session.semantic_selection.model_dump(mode="json")

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
    description: str,
    observed_outputs: str,
    actuators: str,
    safety_bounds: str,
    route_label: str,
    use_llm: bool,
    base_url: str,
    model: str,
    api_key: str,
    include_trajectory: bool = False,
) -> tuple[CFDCRunReport, dict[str, Any]]:
    route_id = ROUTE_CHOICES.get(
        route_label,
        LEGACY_ROUTE_LABELS.get(route_label, route_label or "generic"),
    )
    known_route_ids = set(ROUTE_CHOICES.values())
    if route_id not in known_route_ids:
        raise ValueError(f"未知运行方式：{route_label!r}")
    if route_id != "generic":
        report = run_cfdc_route(
            route_id,
            diagnostic_adapter=None,
            include_trajectory=include_trajectory,
        )
        return report, {
            "session": None,
            "use_llm": False,
            "base_url": "",
            "model": "",
            "api_key": "",
            "include_trajectory": include_trajectory,
            "input_source": "preregistered_developer_scenario",
        }

    if not description.strip():
        raise ValueError("请描述需要控制的对象、可观察输出和可用执行器。")
    adapter = build_adapter(use_llm, base_url, model, api_key)

    system = SystemDescription(
        text=description.strip(),
        observed_outputs=parse_names(observed_outputs),
        actuators=parse_names(actuators),
        safety_bounds=parse_safety_bounds(safety_bounds),
    )
    report = run_cfdc_route(
        route_id,
        description=system,
        diagnostic_adapter=adapter,
        include_trajectory=include_trajectory,
    )
    session = None
    if report.status == "need_more_information":
        if report.diagnosis is None:
            raise RuntimeError("incomplete route report is missing its diagnosis")
        session = start_diagnostic_session(
            system,
            route_id=route_id,
            diagnostic_adapter=adapter,
            diagnosis=report.diagnosis,
        )
        report = report.model_copy(update={"diagnostic_session": session})
    awaiting_clarification = session is not None
    return report, {
        "session": session.model_dump(mode="json") if session is not None else None,
        "use_llm": use_llm if awaiting_clarification else False,
        "base_url": base_url if awaiting_clarification else "",
        "model": model if awaiting_clarification else "",
        "api_key": api_key if awaiting_clarification else "",
        "include_trajectory": include_trajectory,
        "input_source": "natural_language",
    }


def continue_app_run(
    app_state: dict[str, Any],
    answers: list[str],
    supplemental_description: str,
) -> tuple[CFDCRunReport, dict[str, Any]]:
    if not app_state or not app_state.get("session"):
        raise ValueError("当前没有等待回答的诊断会话。")
    session = DiagnosticSessionState.model_validate(app_state["session"])
    adapter = build_adapter(
        bool(app_state.get("use_llm")),
        str(app_state.get("base_url", "")),
        str(app_state.get("model", "")),
        str(app_state.get("api_key", "")),
    )
    question_ids = list(clarification_question_map(session))
    question_map = clarification_question_map(session)
    keyed_answers = {
        question_id: answer.strip()
        for question_id, answer in zip(question_ids, answers)
        if answer.strip()
    }
    observed_outputs = list(session.accumulated_description.observed_outputs)
    actuators = list(session.accumulated_description.actuators)
    for question_id, answer in keyed_answers.items():
        question = question_map[question_id].lower()
        if "watch or record" in question and answer not in observed_outputs:
            observed_outputs.append(answer)
        if "physical action or device" in question and answer not in actuators:
            actuators.append(answer)
    if observed_outputs != session.accumulated_description.observed_outputs or actuators != session.accumulated_description.actuators:
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
        supplemental_description=supplemental_description.strip() or None,
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
        if updated.status == "collecting_information"
        else None
    )
    if next_state["session"] is None:
        next_state.update(
            {
                "use_llm": False,
                "base_url": "",
                "model": "",
                "api_key": "",
            }
        )
    return report, next_state
