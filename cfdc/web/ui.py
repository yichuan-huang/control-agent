from __future__ import annotations

import os

import gradio as gr

from cfdc.web.linked_tuning_ui import (
    bind_linked_tuning_events,
    build_linked_tuning_panel,
)
from cfdc.web.presentation import render_report
from cfdc.web.service import (
    start_app_run,
    submit_app_measurement_response,
)

NATURAL_LANGUAGE_MODE = "自然语言自动分析（主流程）"

LICENSE_NOTICE = (
    "Copyright (C) 2026 Yichuan Huang · "
    "[GNU AGPL v3.0 only](https://www.gnu.org/licenses/agpl-3.0.en.html) · "
    "[Source code](https://github.com/yichuan-huang/control-agent)"
)

CSS = """
.gradio-container { max-width: 1500px !important; }
#app-title h1 { font-size: 28px; margin-bottom: 4px; letter-spacing: 0; }
#run-status { border-left: 4px solid #1677ff; padding: 2px 0 2px 14px; }
.stage-table table { font-size: 13px; }
.stage-table td, .stage-table th { white-space: normal !important; }
.primary-run { min-height: 46px; }
.flow-strip { display: grid; grid-template-columns: repeat(6, minmax(108px, 1fr)); gap: 6px; margin: 4px 0 12px; }
.flow-step { min-height: 68px; border: 1px solid #d8dee8; border-radius: 6px; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 5px; background: #f7f9fc; color: #687386; }
.flow-step span { width: 26px; height: 26px; border-radius: 50%; display: grid; place-items: center; background: #dfe5ee; font-weight: 700; }
.flow-step small { font-size: 12px; text-align: center; }
.flow-step.done { background: #eef9f2; border-color: #9cd3ae; color: #196c39; }
.flow-step.done span { background: #258a4b; color: white; }
.flow-step.waiting { background: #fff8e8; border-color: #e8c66c; color: #7c5a00; }
.flow-step.blocked { background: #fff0f0; border-color: #e6a4a4; color: #9b2c2c; }
.metric-grid { display: grid; grid-template-columns: repeat(5, minmax(120px, 1fr)); gap: 8px; margin-bottom: 10px; }
.metric { min-height: 76px; padding: 12px; border: 1px solid #d8dee8; border-radius: 6px; background: white; display: flex; flex-direction: column; justify-content: space-between; }
.metric small { color: #687386; }
.metric strong { font-size: 16px; overflow-wrap: anywhere; }
.comparison-panel { border: 1px solid #d8dee8; border-radius: 6px; padding: 14px; background: white; }
.comparison-row + .comparison-row { margin-top: 16px; }
.comparison-label, .comparison-values { display: flex; align-items: center; justify-content: space-between; gap: 12px; }
.comparison-label span { font-size: 12px; font-weight: 700; }
.comparison-values { margin-top: 6px; color: #687386; font-size: 12px; }
.bar-track { height: 10px; border-radius: 3px; background: #e8edf4; overflow: hidden; margin-top: 7px; }
.bar { height: 100%; border-radius: 3px; }
.bar.safe { background: #258a4b; }
.bar.unsafe { background: #c43d3d; }
.safe { color: #19743d; }
.unsafe { color: #a72d2d; }
.comparison-note { margin-top: 14px; padding-top: 10px; border-top: 1px solid #e5e9ef; font-weight: 600; }
.empty-result { min-height: 90px; display: grid; place-items: center; color: #687386; border: 1px dashed #cbd3df; border-radius: 6px; }
@media (max-width: 900px) {
  .flow-strip { grid-template-columns: repeat(3, 1fr); }
  .metric-grid { grid-template-columns: repeat(2, 1fr); }
}
"""


def _outputs(report, state):
    view = render_report(report)
    session = report.diagnostic_session
    diagnostic_measurement_statuses = {
        "awaiting_measurements",
        "measurement_needs_more",
        "measurement_conflict",
    }
    profile_measurement_statuses = {
        "awaiting_profile_measurements",
        "specification_conflict",
    }
    profile_assessment_status = (
        session.specification_assessment.status
        if session is not None and session.specification_assessment is not None
        else None
    )
    profile_needs_more = bool(
        session is not None
        and session.status in profile_measurement_statuses
        and profile_assessment_status in {None, "need_more", "conflict"}
    )
    diagnostic_input = bool(
        session
        and session.status in diagnostic_measurement_statuses
        and not view["clarifications"]
    )
    automatically_ready = bool(
        session is not None
        and session.status == "specification_model_ready"
        and profile_assessment_status == "ready"
    )
    show_measurement = diagnostic_input or profile_needs_more or automatically_ready
    confirmation_only = bool(
        show_measurement
        and session is not None
        and session.status in profile_measurement_statuses
        and session.specification_assessment is not None
        and session.specification_assessment.status == "ready"
    )
    show_measurement_input = (diagnostic_input or profile_needs_more) and not confirmation_only
    visibility = view["technical_visibility"]
    return (
        state,
        view["status"],
        view["progress"],
        view["summary"],
        view["performance_visual"],
        gr.update(
            label=view["checklist_title"],
            open=not view["checklist_collapsed"],
        ),
        view["checklist"],
        view["measurement_guidance"],
        view["timeline"],
        view["diagnosis"],
        view["route"],
        view["experiments"],
        view["features"],
        view["controller"],
        view["tuning"],
        view["performance"],
        view["raw"],
        gr.update(
            visible=show_measurement_input,
            value="",
            label=(
                "继续补充缺少的核心参数" if profile_needs_more else "核心参数与测量回复"
            ),
        ),
        gr.update(
            visible=show_measurement,
            value=(
                "已自动确认软件仿真边界"
                if automatically_ready
                else "确认软件仿真边界并继续"
                if confirmation_only
                else ("继续补充参数" if profile_needs_more else "提交测量回复")
            ),
            interactive=not automatically_ready,
        ),
        gr.update(
            visible=show_measurement,
            value=automatically_ready,
            interactive=not automatically_ready,
        ),
        gr.update(visible=visibility["diagnosis"]),
        gr.update(visible=visibility["route"]),
        gr.update(visible=visibility["model"]),
        gr.update(visible=visibility["features"]),
        gr.update(visible=visibility["controller"]),
        gr.update(visible=visibility["tuning"]),
    )


def run_from_ui(description, base_url, model, api_key):
    try:
        report, state = start_app_run(
            description,
            "",
            "",
            "",
            NATURAL_LANGUAGE_MODE,
            True,
            base_url,
            model,
            api_key,
            False,
        )
        return _outputs(report, state)
    except Exception as exc:
        raise gr.Error(str(exc)) from exc


def submit_measurement_from_ui(
    state,
    measurement_response,
    simulation_bounds_confirmed,
    base_url,
    model,
    api_key,
):
    try:
        report, state = submit_app_measurement_response(
            state,
            measurement_response,
            simulation_bounds_confirmed=simulation_bounds_confirmed,
            base_url=base_url,
            model=model,
            api_key=api_key,
        )
        return _outputs(report, state)
    except Exception as exc:
        raise gr.Error(str(exc)) from exc


def reset_ui():
    return (
        "",
        os.getenv("CFDC_LLM_BASE_URL", ""),
        os.getenv("CFDC_LLM_MODEL", ""),
        "",
        {},
        "### 等待控制问题",
        "",
        "",
        "",
        gr.update(label="诊断检查清单（0/8 已完成）", open=True),
        [],
        "",
        "",
        [],
        [],
        [],
        [],
        [],
        [],
        [],
        {},
        gr.update(visible=False, value=""),
        gr.update(visible=False),
        gr.update(visible=False, value=False),
        gr.update(visible=False),
        gr.update(visible=False),
        gr.update(visible=False),
        gr.update(visible=False),
        gr.update(visible=False),
        gr.update(visible=False),
    )


def build_app() -> gr.Blocks:
    with gr.Blocks(title="CFDC Control Studio") as demo:
        app_state = gr.State({})
        gr.Markdown("# CFDC Control Studio", elem_id="app-title")

        with gr.Row(equal_height=False):
            with gr.Column(scale=5, min_width=360):
                gr.Markdown(
                    "先在同一个输入框中用自然语言描述控制问题。八项未完成时，请直接在原描述中"
                    "继续补充并重新检查；全部完成后会自动分类，并只显示建模所需的核心参数。"
                )
                description = gr.Textbox(
                    label="控制问题描述",
                    value="",
                    lines=8,
                    placeholder=(
                        "描述对象、能够观察到的现象、可用的控制作用，以及已经掌握的记录。"
                        "不知道的内容可以明确写“不知道”。"
                    ),
                )
                with gr.Accordion("LLM Provider（必需）", open=False):
                    base_url = gr.Textbox(
                        label="Base URL",
                        value=os.getenv("CFDC_LLM_BASE_URL", ""),
                        placeholder="https://provider.example/v1",
                    )
                    model = gr.Textbox(
                        label="Model",
                        value=os.getenv("CFDC_LLM_MODEL", ""),
                        placeholder="provider-model",
                    )
                    api_key = gr.Textbox(label="API Key", value="", type="password")
                with gr.Row():
                    run_button = gr.Button(
                        "检查描述并继续",
                        variant="primary",
                        elem_classes="primary-run",
                        scale=4,
                    )
                    clear_button = gr.Button("清空", scale=1)
            with gr.Column(scale=8, min_width=560):
                status = gr.Markdown("### 等待控制问题", elem_id="run-status")
                progress = gr.HTML(elem_id="stage-progress")
                summary = gr.HTML()
                performance_visual = gr.HTML()
                with gr.Accordion(
                    "诊断检查清单（0/8 已完成）", open=True
                ) as checklist_accordion:
                    checklist = gr.Dataframe(
                        headers=["需要了解的现象", "状态", "证据摘录"],
                        datatype=["str", "str", "str"],
                        interactive=False,
                        elem_classes="stage-table",
                    )
                measurement_guidance = gr.Markdown()
                timeline = gr.Markdown()

                measurement_response = gr.Textbox(
                    label="核心参数与测量回复",
                    value="",
                    lines=8,
                    visible=False,
                    placeholder=(
                        "按上方问题用自然语言填写已知的变化量、单位、响应时间和"
                        "软件仿真边界；不知道的项目请明确写“不知道”。"
                    ),
                )
                simulation_bounds_confirmed = gr.Checkbox(
                    label="我确认所提交的输入/输出范围仅作为本次软件仿真的停止边界",
                    value=False,
                    visible=False,
                    info=("这不代表真实硬件安全认证，也不授权向真实物理硬件下发命令。"),
                )
                measurement_button = gr.Button(
                    "提交测量回复", variant="primary", visible=False
                )

                with gr.Tabs():
                    with gr.Tab("结构诊断", visible=False) as diagnosis_tab:
                        diagnosis = gr.Dataframe(
                            headers=["字段", "Assessment", "置信度", "证据"],
                            datatype=["str", "str", "str", "str"],
                            interactive=False,
                            elem_classes="stage-table",
                        )
                    with gr.Tab("归类与路由", visible=False) as route_tab:
                        route_result = gr.Dataframe(
                            headers=["项目", "结果"],
                            datatype=["str", "str"],
                            interactive=False,
                            elem_classes="stage-table",
                        )
                    with gr.Tab("模型响应", visible=False) as model_tab:
                        experiments = gr.Dataframe(
                            headers=["#", "实验", "重复", "提取目标", "采样数", "信号"],
                            datatype=[
                                "number",
                                "str",
                                "number",
                                "str",
                                "number",
                                "str",
                            ],
                            interactive=False,
                            elem_classes="stage-table",
                        )
                    with gr.Tab("核心特征", visible=False) as features_tab:
                        features = gr.Dataframe(
                            headers=[
                                "特征",
                                "值",
                                "单位",
                                "置信区间",
                                "置信度",
                                "方法",
                            ],
                            datatype=["str", "str", "str", "str", "str", "str"],
                            interactive=False,
                            elem_classes="stage-table",
                        )
                    with gr.Tab("控制器", visible=False) as controller_tab:
                        controller = gr.Dataframe(
                            headers=["参数", "值"],
                            datatype=["str", "str"],
                            interactive=False,
                            elem_classes="stage-table",
                        )
                    with gr.Tab("调优与适应", visible=False) as tuning_tab:
                        tuning = gr.Dataframe(
                            headers=["项目", "状态", "变化/迭代", "结果"],
                            datatype=["str", "str", "str", "str"],
                            interactive=False,
                            elem_classes="stage-table",
                        )
                        performance = gr.Dataframe(
                            headers=[
                                "场景",
                                "安全性",
                                "最终误差",
                                "稳定时间/s",
                                "饱和率",
                                "违规",
                            ],
                            datatype=["str", "str", "str", "str", "str", "str"],
                            interactive=False,
                            elem_classes="stage-table",
                        )
                        linked_components = build_linked_tuning_panel()
                    with gr.Tab("审计 JSON"):
                        raw_json = gr.JSON(label="完整阶段记录")

        bind_linked_tuning_events(
            linked_components,
            report_json=raw_json,
            app_state=app_state,
            base_url=base_url,
            model=model,
            api_key=api_key,
            progress=progress,
        )
        gr.Markdown(LICENSE_NOTICE, elem_id="license-notice")

        output_components = [
            app_state,
            status,
            progress,
            summary,
            performance_visual,
            checklist_accordion,
            checklist,
            measurement_guidance,
            timeline,
            diagnosis,
            route_result,
            experiments,
            features,
            controller,
            tuning,
            performance,
            raw_json,
            measurement_response,
            measurement_button,
            simulation_bounds_confirmed,
            diagnosis_tab,
            route_tab,
            model_tab,
            features_tab,
            controller_tab,
            tuning_tab,
        ]
        run_button.click(
            run_from_ui,
            inputs=[description, base_url, model, api_key],
            outputs=output_components,
        )
        measurement_button.click(
            submit_measurement_from_ui,
            inputs=[
                app_state,
                measurement_response,
                simulation_bounds_confirmed,
                base_url,
                model,
                api_key,
            ],
            outputs=output_components,
        )
        clear_button.click(
            reset_ui,
            outputs=[
                description,
                base_url,
                model,
                api_key,
                *output_components,
            ],
        )
    return demo
