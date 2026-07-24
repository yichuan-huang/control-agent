"""Inline Gradio controls for Stage-5 effect validation and tuning."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

import gradio as gr

from cfdc.models import CFDCRunReport
from cfdc.web.linked_tuning_presentation import empty_linked_tuning_view
from cfdc.web.presentation import stage_progress_html
from cfdc.web.linked_tuning_service import (
    approve_and_run_linked_gain,
    link_stage5_report,
    reject_linked_gain,
    request_linked_gain,
    restore_linked_initial,
    run_linked_trial,
)


_MUTATION_OPTIONS = {
    "api_visibility": "private",
    "concurrency_id": "cfdc-linked-tuning",
    "concurrency_limit": 1,
    "trigger_mode": "once",
}


@dataclass
class LinkedTuningComponents:
    state: Any
    status: Any
    plant_id: Any
    architecture: Any
    parameters: Any
    derived_parameters: Any
    run_trial: Any
    trial_result: Any
    output_plot: Any
    control_plot: Any
    stability_summary: Any
    request_gain: Any
    proposal_panel: Any
    proposal_diff: Any
    proposal_rationale: Any
    approve_and_run: Any
    reject_gain: Any
    restore_initial: Any
    iterations: Any
    llm_audit: Any


def build_linked_tuning_panel() -> LinkedTuningComponents:
    """Build the direct initial-validation and gain-tuning UI."""

    state = gr.State({})
    with gr.Group(elem_id="linked-tuning-panel"):
        gr.Markdown("### 初始控制器效果验证与调优")
        status = gr.Markdown(
            empty_linked_tuning_view(
                "完成初始控制器设计后，这里会自动载入已编译模型。"
            )["status"],
            elem_id="linked-tuning-status",
        )
        with gr.Row():
            plant_id = gr.Textbox(
                label="已编译对象模型",
                value="",
                interactive=False,
                elem_id="linked-plant-id",
                scale=2,
            )
            architecture = gr.Textbox(
                label="已载入控制器",
                value="",
                interactive=False,
                elem_id="linked-controller-architecture",
                scale=1,
            )
        parameters = gr.Dataframe(
            headers=["参数", "当前值"],
            datatype=["str", "number"],
            value=[],
            interactive=False,
            row_count=0,
            column_count=2,
            label="本轮控制器参数（仅第 1 轮前可编辑）",
            elem_id="linked-controller-parameters",
        )
        derived_parameters = gr.Markdown(
            elem_id="linked-derived-parameters"
        )
        run_trial = gr.Button(
            "运行初始控制器效果验证",
            variant="primary",
            interactive=False,
            elem_id="linked-run-trial",
        )

        with gr.Column(
            visible=False,
            elem_id="linked-trial-result",
        ) as trial_result:
            with gr.Row():
                output_plot = gr.LinePlot(
                    x="time_s",
                    y="value",
                    color="series",
                    title="参考与输出",
                    x_title="时间 / s",
                    elem_id="linked-output-plot",
                )
                control_plot = gr.LinePlot(
                    x="time_s",
                    y="value",
                    color="series",
                    title="请求控制量与实际控制量",
                    x_title="时间 / s",
                    elem_id="linked-control-plot",
                )
            stability_summary = gr.Dataframe(
                headers=["稳定性证据", "值"],
                datatype=["str", "str"],
                value=[],
                interactive=False,
                label="本轮效果验证结果",
                elem_id="linked-stability-summary",
            )
            with gr.Row():
                request_gain = gr.Button(
                    "请求 AI 下一轮参数",
                    interactive=False,
                    visible=False,
                    elem_id="linked-request-gain",
                )
                restore_initial = gr.Button(
                    "恢复第五步初始参数",
                    interactive=False,
                    visible=False,
                    elem_id="linked-restore-initial",
                )

        with gr.Group(
            visible=False,
            elem_id="linked-proposal-panel",
        ) as proposal_panel:
            proposal_diff = gr.Dataframe(
                headers=["参数", "旧值", "建议值", "相对变化"],
                datatype=["str", "number", "number", "number"],
                value=[],
                interactive=False,
                label="AI 参数建议",
                elem_id="linked-proposal-diff",
            )
            proposal_rationale = gr.Markdown(
                elem_id="linked-proposal-rationale"
            )
            with gr.Row():
                approve_and_run = gr.Button(
                    "批准并运行下一轮",
                    variant="primary",
                    interactive=False,
                    elem_id="linked-approve-and-run",
                )
                reject_gain = gr.Button(
                    "拒绝建议",
                    interactive=False,
                    elem_id="linked-reject-gain",
                )
        with gr.Accordion(
            "迭代记录与脱敏 AI 审计",
            open=False,
            elem_id="linked-audit",
        ):
            iterations = gr.Dataframe(
                headers=[
                    "轮次",
                    "来源",
                    "判定",
                    "稳定分数",
                    "饱和率",
                    "硬违规",
                    "回滚",
                    "Proposal ID",
                ],
                interactive=False,
                elem_id="linked-iterations",
            )
            llm_audit = gr.JSON(
                label="脱敏 AI 调用记录",
                elem_id="linked-llm-audit",
            )
    return LinkedTuningComponents(
        state=state,
        status=status,
        plant_id=plant_id,
        architecture=architecture,
        parameters=parameters,
        derived_parameters=derived_parameters,
        run_trial=run_trial,
        trial_result=trial_result,
        output_plot=output_plot,
        control_plot=control_plot,
        stability_summary=stability_summary,
        request_gain=request_gain,
        proposal_panel=proposal_panel,
        proposal_diff=proposal_diff,
        proposal_rationale=proposal_rationale,
        approve_and_run=approve_and_run,
        reject_gain=reject_gain,
        restore_initial=restore_initial,
        iterations=iterations,
        llm_audit=llm_audit,
    )


def _output_components(
    components: LinkedTuningComponents,
) -> list[Any]:
    return [
        components.state,
        components.status,
        components.plant_id,
        components.architecture,
        components.parameters,
        components.derived_parameters,
        components.trial_result,
        components.output_plot,
        components.control_plot,
        components.stability_summary,
        components.proposal_diff,
        components.proposal_rationale,
        components.iterations,
        components.llm_audit,
        components.run_trial,
        components.request_gain,
        components.proposal_panel,
        components.approve_and_run,
        components.reject_gain,
        components.restore_initial,
    ]


def _render_outputs(
    state: Mapping[str, Any],
    view: Mapping[str, Any],
) -> tuple[Any, ...]:
    controls = view["controls"]
    editable = bool(
        state
        and state.get("state") == "trial_pending"
        and not state.get("trials")
    )
    has_trials = bool(state and state.get("trials"))
    show_proposal = bool(controls["approve_and_run"])
    return (
        dict(state),
        view["status"],
        view["plant_id"],
        view["architecture"],
        gr.update(
            value=view["parameter_rows"],
            interactive=editable,
        ),
        view["derived_parameters"],
        gr.update(visible=has_trials),
        view["output_frame"],
        view["control_frame"],
        view["stability_rows"],
        view["proposal_diff"],
        view["proposal_rationale"],
        view["iterations"],
        view["llm_audit"],
        gr.update(
            value=(
                "运行初始控制器效果验证"
                if not has_trials
                else "运行本轮试验"
            ),
            interactive=controls["run_trial"],
        ),
        gr.update(
            interactive=controls["request_gain"],
            visible=controls["request_gain"],
        ),
        gr.update(visible=show_proposal),
        gr.update(interactive=controls["approve_and_run"]),
        gr.update(interactive=controls["reject_gain"]),
        gr.update(
            interactive=controls["restore_initial"],
            visible=controls["restore_initial"],
        ),
    )


def _progress_output(
    report_json: Mapping[str, Any],
    state: Mapping[str, Any],
) -> str:
    progress_fields = {
        "run_id",
        "route_id",
        "status",
        "diagnosis",
        "classification",
        "evidence_readiness",
        "compiled_specification_model",
        "features",
        "controller",
    }
    progress_payload = {
        key: value
        for key, value in report_json.items()
        if key in progress_fields
    }
    report = CFDCRunReport.model_validate(progress_payload)
    linked_state = state.get("state") if state else None
    return stage_progress_html(
        report,
        linked_simulation_state=(
            str(linked_state)
            if linked_state is not None
            else None
        ),
    )


def _revision(state: Mapping[str, Any]) -> int:
    if not isinstance(state, Mapping) or not state:
        raise ValueError("第五步控制器尚未载入")
    revision = state.get("revision")
    if isinstance(revision, bool) or not isinstance(revision, int):
        raise ValueError("控制器调试会话 revision 无效")
    return revision


def _service_call(
    function,
    *args,
    report_json: Mapping[str, Any],
    **kwargs,
):
    try:
        state, view = function(*args, **kwargs)
        return (
            *_render_outputs(state, view),
            _progress_output(report_json, state),
        )
    except Exception as exc:
        raise gr.Error(str(exc)) from exc


def _sync_callback(report_json, state):
    return _service_call(
        link_stage5_report,
        report_json or {},
        state or None,
        report_json=report_json or {},
    )


def _run_callback(state, parameters, report_json):
    return _service_call(
        run_linked_trial,
        state,
        parameters,
        report_json=report_json,
        expected_revision=_revision(state),
    )


def _cleared_credential_state(app_state):
    clean = dict(app_state or {})
    for key in (
        "api_key",
        "authorization",
        "token",
        "secret",
        "password",
    ):
        if key in clean:
            clean[key] = ""
    return clean


def _request_callback(
    state,
    base_url,
    model,
    api_key,
    app_state,
    report_json,
):
    outputs = _service_call(
        request_linked_gain,
        state,
        report_json=report_json,
        expected_revision=_revision(state),
        base_url=base_url or "",
        model=model or "",
        api_key=api_key or "",
    )
    return (*outputs, _cleared_credential_state(app_state))


def _approve_callback(state, report_json):
    return _service_call(
        approve_and_run_linked_gain,
        state,
        report_json=report_json,
        expected_revision=_revision(state),
    )


def _reject_callback(state, report_json):
    return _service_call(
        reject_linked_gain,
        state,
        report_json=report_json,
        expected_revision=_revision(state),
    )


def _restore_callback(state, report_json):
    return _service_call(
        restore_linked_initial,
        state,
        report_json=report_json,
        expected_revision=_revision(state),
    )


def bind_linked_tuning_events(
    components: LinkedTuningComponents,
    *,
    report_json: Any,
    app_state: Any,
    base_url: Any,
    model: Any,
    api_key: Any,
    progress: Any,
) -> None:
    """Bind automatic model reuse and serialized tuning actions."""

    outputs = [*_output_components(components), progress]
    report_json.change(
        _sync_callback,
        inputs=[report_json, components.state],
        outputs=outputs,
        **_MUTATION_OPTIONS,
    )
    components.run_trial.click(
        _run_callback,
        inputs=[
            components.state,
            components.parameters,
            report_json,
        ],
        outputs=outputs,
        **_MUTATION_OPTIONS,
    )
    components.request_gain.click(
        _request_callback,
        inputs=[
            components.state,
            base_url,
            model,
            api_key,
            app_state,
            report_json,
        ],
        outputs=[*outputs, app_state],
        **_MUTATION_OPTIONS,
    )
    components.approve_and_run.click(
        _approve_callback,
        inputs=[components.state, report_json],
        outputs=outputs,
        **_MUTATION_OPTIONS,
    )
    components.reject_gain.click(
        _reject_callback,
        inputs=[components.state, report_json],
        outputs=outputs,
        **_MUTATION_OPTIONS,
    )
    components.restore_initial.click(
        _restore_callback,
        inputs=[components.state, report_json],
        outputs=outputs,
        **_MUTATION_OPTIONS,
    )


__all__ = [
    "LinkedTuningComponents",
    "bind_linked_tuning_events",
    "build_linked_tuning_panel",
]
