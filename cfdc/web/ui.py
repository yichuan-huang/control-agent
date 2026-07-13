from __future__ import annotations

import os

import gradio as gr

from cfdc.web.presentation import render_report
from cfdc.web.service import (
    ROUTE_CHOICES,
    continue_app_run,
    start_app_run,
)


NATURAL_LANGUAGE_MODE = "自然语言自动分析（主流程）"


EXAMPLES = [
    [
        "这是一个由电加热器调节的恒温箱，可视为 first-order self-regulating temperature process。输入是归一化加热功率，输出是连续测量的箱内温度。小幅提高功率后，温度立即沿预期方向平滑上升，不会先反向变化，也没有可察觉的等待；随后以单调、近似指数的方式收敛到新的稳定值，撤去变化后会回到原工作点。对象只有一个输入和一个主要输出，执行器和温度传感器均可用，非线性较弱。环境温度和装载量可能缓慢变化，因此增益和时间尺度存在中等不确定性，但不会改变其自稳结构。",
        "temperature",
        "heater",
    ],
    [
        "这是一个带粘性阻尼的 spring-mass-damper oscillator，输入是施加在质量块上的水平力，输出是连续测量的位置。质量块从小位移释放后会围绕平衡点往复振动，振幅逐周期衰减并最终回到平衡位置；小力脉冲产生相同的衰减振荡，初始运动方向与施力方向一致，没有反向响应。系统是单输入单输出，位置传感器和力执行器均可用，在小位移范围内近似线性、可控且可观。质量和阻尼会随载荷略有变化，因此固有频率、阻尼比和输入增益存在中等不确定性，但开环响应保持稳定。",
        "position",
        "force",
    ],
    [
        "这是一个水平轨道上的 low-friction cart，输入是双向电机力，输出是可连续测量的小车位置和速度。短时施加恒定小力时，小车产生近似恒定加速度；撤去力后速度基本保持、位置继续线性 drift，不会自行回到原位置，因此对象表现为 double integrator / non-restoring motion。力方向反转时加速度也立即反转，没有先反向的异常响应。系统只有一个控制输入，位置和速度传感器均可用，在限定行程和速度范围内近似线性、可控且可观。摩擦和负载可能小幅变化，使输入到加速度的增益存在中等不确定性，但不改变积分结构。",
        "position, velocity",
        "motor force",
    ],
    [
        "一个稳定过程对阀门阶跃先反向运动，随后才向最终方向稳定。",
        "output",
        "valve",
    ],
    [
        "强耦合双输入双输出过程，每个输入都会明显影响两个输出。",
        "y1, y2",
        "u1, u2",
    ],
]


CSS = """
.gradio-container { max-width: 1500px !important; }
#app-title h1 { font-size: 28px; margin-bottom: 4px; letter-spacing: 0; }
#run-status { border-left: 4px solid #1677ff; padding: 2px 0 2px 14px; }
.stage-table table { font-size: 13px; }
.stage-table td, .stage-table th { white-space: normal !important; }
.primary-run { min-height: 46px; }
.flow-strip { display: grid; grid-template-columns: repeat(8, minmax(92px, 1fr)); gap: 6px; margin: 4px 0 12px; }
.flow-step { min-height: 68px; border: 1px solid #d8dee8; border-radius: 6px; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 5px; background: #f7f9fc; color: #687386; }
.flow-step span { width: 26px; height: 26px; border-radius: 50%; display: grid; place-items: center; background: #dfe5ee; font-weight: 700; }
.flow-step small { font-size: 12px; }
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
  .flow-strip { grid-template-columns: repeat(4, 1fr); }
  .metric-grid { grid-template-columns: repeat(2, 1fr); }
}
"""


def _question_updates(items: list[tuple[str, str]]):
    updates = []
    for index in range(4):
        if index < len(items):
            question_id, question = items[index]
            updates.append(gr.update(label=f"{question_id} · {question}", visible=True, value=""))
        else:
            updates.append(gr.update(visible=False, value=""))
    return updates


def _outputs(report, state):
    view = render_report(report)
    questions = view["clarifications"]
    return (
        state,
        view["status"],
        view["progress"],
        view["summary"],
        view["performance_visual"],
        view["diagnosis"],
        view["route"],
        view["experiments"],
        view["features"],
        view["controller"],
        view["tuning"],
        view["performance"],
        view["raw"],
        gr.update(visible=bool(questions)),
        *_question_updates(questions),
    )


def run_from_ui(*args):
    try:
        report, state = start_app_run(*args)
        return _outputs(report, state)
    except Exception as exc:
        raise gr.Error(str(exc)) from exc


def continue_from_ui(state, answer_1, answer_2, answer_3, answer_4, supplemental):
    try:
        report, state = continue_app_run(
            state,
            [answer_1, answer_2, answer_3, answer_4],
            supplemental,
        )
        return _outputs(report, state)
    except Exception as exc:
        raise gr.Error(str(exc)) from exc


def update_run_mode(route_label: str):
    natural_language = ROUTE_CHOICES.get(route_label) == "generic"
    input_update = gr.update(interactive=natural_language)
    llm_update = gr.update(interactive=natural_language, value=False if not natural_language else None)
    provider_update = gr.update(interactive=natural_language)
    note = (
        "**自然语言自动分析：** 使用下方描述、输出和执行器；可选择启用 LLM。"
        if natural_language
        else "**开发验证场景：** 使用预注册描述、诊断和 Profile；不会调用 LLM。下方用户输入仅暂时禁用并会被后端忽略，切回主流程后内容仍保留。"
    )
    return (
        note,
        input_update,
        input_update,
        input_update,
        input_update,
        llm_update,
        provider_update,
        provider_update,
        provider_update,
    )


def reset_ui():
    return (
        NATURAL_LANGUAGE_MODE,
        "**自然语言自动分析：** 使用下方描述、输出和执行器；可选择启用 LLM。",
        "",
        "",
        "",
        "",
        False,
        False,
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
    )


def build_app() -> gr.Blocks:
    with gr.Blocks(title="CFDC Control Studio") as demo:
        app_state = gr.State({})
        gr.Markdown("# CFDC Control Studio", elem_id="app-title")

        with gr.Row(equal_height=False):
            with gr.Column(scale=5, min_width=360):
                route = gr.Dropdown(
                    choices=list(ROUTE_CHOICES),
                    value=NATURAL_LANGUAGE_MODE,
                    label="运行方式",
                )
                mode_note = gr.Markdown(
                    "**自然语言自动分析：** 使用下方描述、输出和执行器；可选择启用 LLM。"
                )
                description = gr.Textbox(
                    label="控制问题",
                    lines=6,
                    placeholder="描述对象如何运动、能够测量什么、可以施加什么控制，以及已知约束。",
                )
                with gr.Row():
                    observed_outputs = gr.Textbox(label="可观察输出", placeholder="temperature, position")
                    actuators = gr.Textbox(label="执行器", placeholder="heater, motor force")
                with gr.Accordion("高级仿真设置", open=False):
                    safety_bounds = gr.Textbox(
                        label="安全边界",
                        lines=3,
                        placeholder="max_abs_control=1.0\nmax_abs_output=2.0",
                    )
                    include_trajectory = gr.Checkbox(label="保留完整轨迹", value=False)
                with gr.Accordion("LLM Provider", open=False):
                    use_llm = gr.Checkbox(label="启用 LLM 诊断与语义路由", value=False)
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
                    api_key = gr.Textbox(label="API Key", type="password")
                with gr.Row():
                    run_button = gr.Button("运行完整仿真", variant="primary", elem_classes="primary-run", scale=4)
                    clear_button = gr.Button("清空", scale=1)
                gr.Examples(
                    examples=EXAMPLES,
                    inputs=[description, observed_outputs, actuators],
                    label="可直接完成全流程的控制问题（含详细 Type I / II / III）",
                )

            with gr.Column(scale=8, min_width=560):
                status = gr.Markdown("### 等待控制问题", elem_id="run-status")
                progress = gr.HTML()
                summary = gr.HTML()
                performance_visual = gr.HTML()
                with gr.Group(visible=False) as clarification_group:
                    gr.Markdown("### 补充诊断证据")
                    question_1 = gr.Textbox(visible=False)
                    question_2 = gr.Textbox(visible=False)
                    question_3 = gr.Textbox(visible=False)
                    question_4 = gr.Textbox(visible=False)
                    supplemental = gr.Textbox(label="补充描述", lines=2)
                    continue_button = gr.Button("提交并继续仿真", variant="primary")

                with gr.Tabs():
                    with gr.Tab("结构诊断"):
                        diagnosis = gr.Dataframe(
                            headers=["字段", "Assessment", "置信度", "证据"],
                            datatype=["str", "str", "str", "str"],
                            interactive=False,
                            elem_classes="stage-table",
                        )
                    with gr.Tab("归类与路由"):
                        route_result = gr.Dataframe(
                            headers=["项目", "结果"],
                            datatype=["str", "str"],
                            interactive=False,
                            elem_classes="stage-table",
                        )
                    with gr.Tab("安全实验"):
                        experiments = gr.Dataframe(
                            headers=["#", "实验", "重复", "提取目标", "采样数", "信号"],
                            datatype=["number", "str", "number", "str", "number", "str"],
                            interactive=False,
                            elem_classes="stage-table",
                        )
                    with gr.Tab("核心特征"):
                        features = gr.Dataframe(
                            headers=["特征", "值", "单位", "置信区间", "置信度", "方法"],
                            datatype=["str", "str", "str", "str", "str", "str"],
                            interactive=False,
                            elem_classes="stage-table",
                        )
                    with gr.Tab("控制器"):
                        controller = gr.Dataframe(
                            headers=["参数", "值"],
                            datatype=["str", "str"],
                            interactive=False,
                            elem_classes="stage-table",
                        )
                    with gr.Tab("调优与适应"):
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
                    with gr.Tab("审计 JSON"):
                        raw_json = gr.JSON(label="完整阶段记录")

        output_components = [
            app_state,
            status,
            progress,
            summary,
            performance_visual,
            diagnosis,
            route_result,
            experiments,
            features,
            controller,
            tuning,
            performance,
            raw_json,
            clarification_group,
            question_1,
            question_2,
            question_3,
            question_4,
        ]
        run_button.click(
            run_from_ui,
            inputs=[
                description,
                observed_outputs,
                actuators,
                safety_bounds,
                route,
                use_llm,
                base_url,
                model,
                api_key,
                include_trajectory,
            ],
            outputs=output_components,
        )
        route.change(
            update_run_mode,
            inputs=[route],
            outputs=[
                mode_note,
                description,
                observed_outputs,
                actuators,
                safety_bounds,
                use_llm,
                base_url,
                model,
                api_key,
            ],
        )
        continue_button.click(
            continue_from_ui,
            inputs=[app_state, question_1, question_2, question_3, question_4, supplemental],
            outputs=output_components,
        )
        clear_button.click(
            reset_ui,
            outputs=[
                route,
                mode_note,
                description,
                observed_outputs,
                actuators,
                safety_bounds,
                include_trajectory,
                use_llm,
                base_url,
                model,
                api_key,
                supplemental,
                *output_components,
            ],
        )
    return demo
