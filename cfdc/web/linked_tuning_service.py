"""Connect a fifth-stage controller candidate to one simulation session."""

from __future__ import annotations

from copy import deepcopy
import hashlib
import json
import math
from typing import Any, Mapping

import pandas as pd

from cfdc.diagnosis import OpenAICompatibleDiagnosticAdapter
from cfdc.lab import (
    SimulationRunConfig,
    approve_llm_proposal,
    bootstrap_controller_candidate,
    create_stage5_session,
    edit_initial_controller_parameters,
    export_session,
    extract_tunable_parameters,
    reject_llm_proposal,
    request_gain_for_session,
    restore_initial_controller,
    run_next_trial,
    sanitize_for_audit,
    validate_session_mapping,
)
from cfdc.models import (
    CompiledSpecificationModel,
    ControllerCandidate,
    RegisteredNonlinearModelSpec,
    StateSpaceModelSpec,
    SystemDescription,
    TransferFunctionModelSpec,
)
from cfdc.web.linked_tuning_presentation import (
    empty_linked_tuning_view,
    render_linked_tuning,
)


def encode_lab_state(session) -> dict[str, Any]:
    return json.loads(export_session(session))


def decode_lab_state(payload: Mapping[str, Any]):
    if not isinstance(payload, Mapping) or not payload:
        raise ValueError("控制器调试尚未创建会话")
    return validate_session_mapping(payload)


def _canonical_sha256(value: Mapping[str, Any]) -> str:
    serialized = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


def _signal_ids(
    model: TransferFunctionModelSpec
    | StateSpaceModelSpec
    | RegisteredNonlinearModelSpec,
) -> tuple[list[str], list[str]]:
    if isinstance(model, TransferFunctionModelSpec):
        return [model.input_signal_id], [model.output_signal_id]
    return list(model.input_signal_ids), list(model.output_signal_ids)


def _run_config(
    compiled: CompiledSpecificationModel,
    description: SystemDescription | None,
) -> tuple[SimulationRunConfig, list[str]]:
    model = compiled.model
    if isinstance(model, RegisteredNonlinearModelSpec):
        from cfdc.sim import registered_run_envelope

        envelope = registered_run_envelope(
            model,
            declared_bounds=compiled.safety_bounds,
        )
        return (
            SimulationRunConfig.model_validate(envelope),
            [
                *compiled.assumptions,
                "The registered nonlinear runtime uses its fixed five-scenario "
                "validation envelope.",
            ],
        )
    bounds = compiled.safety_bounds
    required = {"input_min", "input_max", "output_min", "output_max"}
    missing = sorted(required - set(bounds))
    if missing:
        raise ValueError("已编译规格缺少仿真边界：" + ", ".join(missing))
    input_min = float(bounds["input_min"])
    input_max = float(bounds["input_max"])
    output_min = float(bounds["output_min"])
    output_max = float(bounds["output_max"])
    if input_min >= input_max or output_min >= output_max:
        raise ValueError("已编译规格中的输入或输出边界无效")

    assumptions = list(compiled.assumptions)
    if input_min <= 0.0 <= input_max:
        runtime_input_bounds = (input_min, input_max)
    else:
        half_input_span = 0.5 * (input_max - input_min)
        runtime_input_bounds = (-half_input_span, half_input_span)
        assumptions.append(
            "Absolute actuator limits were expressed around their midpoint "
            "for the local deviation-coordinate simulation."
        )
    if output_min <= 0.0 <= output_max:
        runtime_output_bounds = (output_min, output_max)
    else:
        half_output_span = 0.5 * (output_max - output_min)
        runtime_output_bounds = (-half_output_span, half_output_span)
        assumptions.append(
            "Absolute output limits were expressed around their midpoint "
            "for the local deviation-coordinate simulation."
        )

    time_scale = float(
        description.time_scale_hint_s
        if description is not None and description.time_scale_hint_s is not None
        else compiled.time_scale_hint_s
    )
    horizon = 6.0 * time_scale
    description_bounds = description.safety_bounds if description else {}
    declared_max = description_bounds.get("max_test_duration_s")
    if declared_max is not None:
        horizon = min(horizon, float(declared_max))
    discrete_sample_time = model.sample_time_s
    if model.time_domain == "discrete" and discrete_sample_time is not None:
        sample_time = float(discrete_sample_time)
    else:
        sample_time = min(time_scale / 100.0, horizon / 100.0)
    sample_time = max(sample_time, horizon / 19_999.0)

    reference_limit = 0.1 * (runtime_output_bounds[1] - runtime_output_bounds[0])
    declared_reference = description_bounds.get("max_abs_reference_normalized")
    if declared_reference is not None and float(declared_reference) > 0.0:
        reference_limit = min(reference_limit, float(declared_reference))
    if not math.isfinite(reference_limit) or reference_limit <= 0.0:
        raise ValueError("无法从已声明边界构造正的保守参考变化")

    input_ids, output_ids = _signal_ids(model)
    return (
        SimulationRunConfig(
            reference={name: reference_limit for name in output_ids},
            horizon_s=horizon,
            sample_time_s=sample_time,
            actuator_bounds={name: runtime_input_bounds for name in input_ids},
            output_bounds={name: runtime_output_bounds for name in output_ids},
        ),
        assumptions,
    )


def _candidate_from_report(report: Mapping[str, Any]) -> ControllerCandidate:
    raw = report.get("controller")
    if not isinstance(raw, Mapping):
        raise ValueError("第五步尚未生成可试验的控制器候选")
    payload = deepcopy(dict(raw))
    gains = payload.get("gains")
    final_gains = report.get("final_gains")
    if isinstance(gains, Mapping) and isinstance(final_gains, Mapping):
        payload["gains"] = {
            name: final_gains.get(name, value) for name, value in gains.items()
        }
    return ControllerCandidate.model_validate(payload)


def link_stage5_report(
    report_payload: Mapping[str, Any],
    current_payload: Mapping[str, Any] | None = None,
    *,
    base_url: str = "",
    model: str = "",
    api_key: str = "",
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Create or reuse tuning directly from the validated compiled model."""

    del base_url, model, api_key
    if not isinstance(report_payload, Mapping):
        return {}, empty_linked_tuning_view("五步流程尚未产生结构化结果。")
    raw_compiled = report_payload.get("compiled_specification_model")
    if not isinstance(raw_compiled, Mapping):
        return {}, empty_linked_tuning_view(
            "第五步报告缺少已编译对象模型，请返回规格信息阶段补充数值。"
        )
    try:
        compiled = CompiledSpecificationModel.model_validate(raw_compiled)
        description = (
            SystemDescription.model_validate(report_payload["system_description"])
            if isinstance(
                report_payload.get("system_description"),
                Mapping,
            )
            else None
        )
        candidate = _candidate_from_report(report_payload)
        if candidate.plant_id != compiled.plant_id:
            raise ValueError("控制器候选与已编译对象的 plant_id 不一致")
        run_config, assumptions = _run_config(compiled, description)
        cutoff = candidate.design_parameters.get("filter_cutoff_rad_s")
        bootstrap = bootstrap_controller_candidate(
            candidate,
            compiled.model,
            filter_cutoff_rad_s=cutoff,
        )
        if (
            bootstrap.status != "ready"
            or bootstrap.controller is None
            or bootstrap.tuning_profile is None
        ):
            raise ValueError(bootstrap.lock_reason or "控制器架构无法安全转换")
        run_id = report_payload.get("run_id")
        if not isinstance(run_id, str) or not run_id.strip():
            raise ValueError("五步报告缺少 run_id")
        link_sha256 = _canonical_sha256(
            {
                "run_id": run_id,
                "plant_id": compiled.plant_id,
                "model": compiled.model.model_dump(mode="json"),
                "candidate": candidate.model_dump(mode="json"),
                "run_config": run_config.model_dump(mode="json"),
            }
        )
        if current_payload:
            try:
                current = decode_lab_state(current_payload)
            except ValueError:
                current = None
            if (
                current is not None
                and current.origin == "stage5_candidate_model"
                and current.source_run_id == run_id
                and current.source_plant_id == compiled.plant_id
                and current.source_link_sha256 == link_sha256
            ):
                return (
                    encode_lab_state(current),
                    render_linked_tuning(current),
                )
        session = create_stage5_session(
            source_run_id=run_id,
            source_plant_id=compiled.plant_id,
            source_controller_architecture=candidate.architecture,
            source_link_sha256=link_sha256,
            model=compiled.model,
            controller=bootstrap.controller,
            tuning_profile=bootstrap.tuning_profile,
            run_config=run_config,
            model_assumptions=[
                *assumptions,
                "The controller originated from the fifth-stage candidate.",
            ],
        )
        return (
            encode_lab_state(session),
            render_linked_tuning(session),
        )
    except (TypeError, ValueError) as exc:
        return {}, empty_linked_tuning_view(str(exc))


def _parameter_mapping(rows: object) -> dict[str, float]:
    if isinstance(rows, pd.DataFrame):
        values = rows.values.tolist()
    elif isinstance(rows, list):
        values = rows
    else:
        raise ValueError("控制器参数表格式无效")
    result: dict[str, float] = {}
    for row in values:
        if not isinstance(row, (list, tuple)) or len(row) < 2:
            raise ValueError("每个控制器参数行必须包含名称和值")
        name, raw_value = row[0], row[1]
        if not isinstance(name, str) or not name:
            raise ValueError("控制器参数名称无效")
        if isinstance(raw_value, bool) or not isinstance(
            raw_value,
            (int, float),
        ):
            raise ValueError(f"控制器参数 {name} 必须是数值")
        value = float(raw_value)
        if not math.isfinite(value):
            raise ValueError(f"控制器参数 {name} 必须是有限值")
        if name in result:
            raise ValueError(f"控制器参数 {name} 重复")
        result[name] = value
    return result


def run_linked_trial(
    payload: Mapping[str, Any],
    parameter_rows: object,
    *,
    expected_revision: int,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Apply allowed first-round edits and execute exactly one trial."""

    session = decode_lab_state(payload)
    parameters = _parameter_mapping(parameter_rows)
    if not session.trials:
        if session.trial_controller is None or session.tuning_profile is None:
            raise ValueError("关联会话没有可运行的控制器")
        current = extract_tunable_parameters(
            session.trial_controller,
            session.tuning_profile,
        )
        if parameters != current:
            session = edit_initial_controller_parameters(
                session,
                parameters,
                expected_revision=expected_revision,
            )
            expected_revision = session.revision
    session = run_next_trial(
        session,
        expected_revision=expected_revision,
    )
    return encode_lab_state(session), render_linked_tuning(session)


def request_linked_gain(
    payload: Mapping[str, Any],
    *,
    expected_revision: int,
    base_url: str,
    model: str,
    api_key: str,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Request one constrained proposal without applying or running it."""

    session = decode_lab_state(payload)
    try:
        adapter = OpenAICompatibleDiagnosticAdapter(
            base_url=base_url.strip() or None,
            model=model.strip() or None,
            api_key=api_key.strip() or None,
        )
        session, _ = request_gain_for_session(
            session,
            adapter,
            expected_revision=expected_revision,
            secret_literals=[api_key],
        )
    except Exception as exc:
        safe = sanitize_for_audit(
            str(exc),
            secret_literals=[api_key],
        )
        raise ValueError(str(safe)) from None
    return encode_lab_state(session), render_linked_tuning(session)


def approve_and_run_linked_gain(
    payload: Mapping[str, Any],
    *,
    expected_revision: int,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Approve the pending LLM proposal and run exactly one trial."""

    session = approve_llm_proposal(
        decode_lab_state(payload),
        expected_revision=expected_revision,
    )
    session = run_next_trial(
        session,
        expected_revision=session.revision,
    )
    return encode_lab_state(session), render_linked_tuning(session)


def reject_linked_gain(
    payload: Mapping[str, Any],
    *,
    expected_revision: int,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Reject a pending LLM proposal without changing the controller."""

    session = reject_llm_proposal(
        decode_lab_state(payload),
        expected_revision=expected_revision,
    )
    return encode_lab_state(session), render_linked_tuning(session)


def restore_linked_initial(
    payload: Mapping[str, Any],
    *,
    expected_revision: int,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Queue the original fifth-stage parameters again."""

    session = restore_initial_controller(
        decode_lab_state(payload),
        expected_revision=expected_revision,
    )
    return encode_lab_state(session), render_linked_tuning(session)


__all__ = [
    "approve_and_run_linked_gain",
    "decode_lab_state",
    "encode_lab_state",
    "link_stage5_report",
    "reject_linked_gain",
    "request_linked_gain",
    "restore_linked_initial",
    "run_linked_trial",
]
