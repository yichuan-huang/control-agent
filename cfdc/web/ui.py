from __future__ import annotations

import os

import gradio as gr

from cfdc.web.linked_tuning_ui import (
    bind_linked_tuning_events,
    build_linked_tuning_panel,
)
from cfdc.web.presentation import render_report
from cfdc.web.service import (
    continue_app_run,
    start_app_run,
    submit_app_measurement_response,
)

NATURAL_LANGUAGE_MODE = "自然语言自动分析（主流程）"

LICENSE_NOTICE = (
    "Copyright (C) 2026 Yichuan Huang · "
    "[GNU AGPL v3.0 only](https://www.gnu.org/licenses/agpl-3.0.en.html) · "
    "[Source code](https://github.com/yichuan-huang/control-agent)"
)

EXAMPLES = [
    [
        (
            "这是一个由电加热器调节的恒温箱。温度传感器连续记录箱内温度，"
            "已有日志包含小幅加热功率变化前后的温度曲线；一个采样周期内温度就沿最终方向开始变化，"
            "恢复原功率后温度逐渐回到原水平，正反变化平滑且近似成比例。"
        )
    ],
    [
        (
            "质量块通过弹簧和阻尼器连接在支架上，由双向水平力驱动，位置传感器记录完整运动。"
            "现有小幅试验记录显示释放后会出现往复运动并多次穿过平衡位置，振幅逐次减小；"
            "一个采样周期内就开始变化，正反方向的小力变化产生近似对称的响应。"
        )
    ],
    [
        (
            "低摩擦小车由双向电机力驱动，位置和速度传感器连续记录同一段平移运动。"
            "已有小幅试验记录显示施力后一个采样周期内速度就沿施力方向变化；撤力后速度保持，"
            "位置继续漂移而不会自行返回，正反方向的力产生近似对称的变化。"
        )
    ],
    [
        (
            "带蒸汽析出的储液容器由进液阀门调节，液位传感器连续记录完整变化。"
            "已有小幅阀门试验显示一个采样周期内液位就开始变化，但开始时会先沿不利或相反方向运动，"
            "随后才转向并停在新的恒定位置；正反试验近似对称。"
        )
    ],
    [
        (
            "两个泵分别向连通容器供液，两个液位传感器同步记录液位。已有小幅单泵变化记录显示，"
            "改变任一执行器都会明显改变多个输出，但靠近该泵的液位变化更大；保持新泵速后两个液位"
            "最终停在新的恒定位置，正反泵速变化近似对称。"
        )
    ],
]

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


def _question_updates(items: list[tuple[str, str]]):
    updates = []
    for index in range(4):
        if index < len(items):
            question_id, question = items[index]
            updates.append(
                gr.update(label=f"{question_id} · {question}", visible=True, value="")
            )
        else:
            updates.append(gr.update(visible=False, value=""))
    return updates


def _outputs(report, state):
    view = render_report(report)
    session = report.diagnostic_session
    show_questions = bool(session and session.status == "collecting_description")
    show_measurement = bool(
        session
        and session.status
        in {
            "awaiting_measurements",
            "measurement_needs_more",
            "measurement_conflict",
            "awaiting_profile_measurements",
            "specification_conflict",
        }
    )
    visibility = view["technical_visibility"]
    return (
        state,
        view["status"],
        view["progress"],
        view["summary"],
        view["performance_visual"],
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
        gr.update(visible=show_questions),
        *_question_updates(view["clarifications"]),
        gr.update(visible=show_questions),
        gr.update(visible=show_measurement, value=""),
        gr.update(visible=show_measurement),
        gr.update(visible=show_measurement, value=False),
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


def continue_from_ui(
    state,
    answer_1,
    answer_2,
    answer_3,
    answer_4,
    supplemental,
    base_url,
    model,
    api_key,
):
    try:
        report, state = continue_app_run(
            state,
            [answer_1, answer_2, answer_3, answer_4],
            supplemental,
            base_url=base_url,
            model=model,
            api_key=api_key,
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
        "",
        {},
        "### 等待控制问题",
        "",
        "",
        "",
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
        gr.update(visible=False),
        gr.update(visible=False, value=""),
        gr.update(visible=False, value=""),
        gr.update(visible=False, value=""),
        gr.update(visible=False, value=""),
        gr.update(visible=False),
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
                    "先用一段自然语言描述控制问题。系统会生成测量计划，并只请你从已有记录、"
                    "日志或手册中回填证据；测量验证前不会展示正式分类、Profile 或控制器。"
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
                        "开始引导诊断",
                        variant="primary",
                        elem_classes="primary-run",
                        scale=4,
                    )
                    clear_button = gr.Button("清空", scale=1)
                gr.Examples(examples=EXAMPLES, inputs=[description], label="控制问题描述示例")

            with gr.Column(scale=8, min_width=560):
                status = gr.Markdown("### 等待控制问题", elem_id="run-status")
                progress = gr.HTML(elem_id="stage-progress")
                summary = gr.HTML()
                performance_visual = gr.HTML()
                checklist = gr.Dataframe(
                    label="诊断检查清单",
                    headers=["需要了解的现象", "状态", "证据摘录"],
                    datatype=["str", "str", "str"],
                    interactive=False,
                    elem_classes="stage-table",
                )
                measurement_guidance = gr.Markdown()
                timeline = gr.Markdown()

                with gr.Group(visible=False) as question_group:
                    gr.Markdown("### 补充问题描述")
                    question_1 = gr.Textbox(value="", visible=False)
                    question_2 = gr.Textbox(value="", visible=False)
                    question_3 = gr.Textbox(value="", visible=False)
                    question_4 = gr.Textbox(value="", visible=False)
                    supplemental = gr.Textbox(label="补充描述", value="", lines=3)
                    continue_button = gr.Button(
                        "提交描述补充", variant="primary", visible=False
                    )

                measurement_response = gr.Textbox(
                    label="现有记录与测量回复",
                    value="",
                    lines=8,
                    visible=False,
                    placeholder=(
                        "粘贴已有记录或手册摘录，并逐项说明观察结果；"
                        "没有记录的项目请明确写“不知道”。"
                    ),
                )
                simulation_bounds_confirmed = gr.Checkbox(
                    label="我确认所提交的输入/输出范围仅作为本次软件仿真的停止边界",
                    value=False,
                    visible=False,
                    info=(
                        "这不代表真实硬件安全认证，也不授权向真实物理硬件下发命令。"
                    ),
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
                            datatype=["number", "str", "number", "str", "number", "str"],
                            interactive=False,
                            elem_classes="stage-table",
                        )
                    with gr.Tab("核心特征", visible=False) as features_tab:
                        features = gr.Dataframe(
                            headers=["特征", "值", "单位", "置信区间", "置信度", "方法"],
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
                            headers=["场景", "安全性", "最终误差", "稳定时间/s", "饱和率", "违规"],
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
            question_group,
            question_1,
            question_2,
            question_3,
            question_4,
            continue_button,
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
        continue_button.click(
            continue_from_ui,
            inputs=[
                app_state,
                question_1,
                question_2,
                question_3,
                question_4,
                supplemental,
                base_url,
                model,
                api_key,
            ],
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
                supplemental,
                *output_components,
            ],
        )
    return demo
