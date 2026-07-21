from __future__ import annotations

import os

import gradio as gr

from cfdc.web.presentation import render_report
from cfdc.web.service import (
    ROUTE_CHOICES,
    continue_app_run,
    start_app_run,
    submit_app_evidence,
    submit_app_json,
    submit_app_specifications,
)


NATURAL_LANGUAGE_MODE = "自然语言自动分析（主流程）"


EXAMPLES = [
    [
        "这是一个由电加热器调节的恒温箱。控制输入是归一化加热功率，输出是温度传感器连续记录的箱内温度（temperature）。在多个小幅且可逆的功率试验中，提高功率后一个采样周期内就能看到温度开始上升，初始变化方向始终与加热作用一致，没有先下降或停顿；之后变化速度逐渐减小并停在新的恒定水平，功率恢复原值后温度也逐渐回到原工作水平。试验曲线平滑，没有持续往复波动，也没有明显分开的多个快慢阶段。当前工作区间只有一个加热器和一个主要温度输出，传感器覆盖整个试验过程；相同幅度的正负功率变化会产生方向相反、大小近似成比例的温度变化，未观察到死区、滞回或饱和。环境温度和装载量缓慢变化时，最终温差和达到恒定水平所需时间会有小幅到中等变化，但上述运动方向、响应时机和回到工作水平的现象保持不变。",
        "temperature",
        "heater",
    ],
    [
        "这是一个质量块通过弹簧（spring）和粘性阻尼器连接在固定支架上的装置。控制输入是施加在质量块上的双向水平力，输出是位置传感器连续记录的位置。质量块从小位移静止释放后，会反复穿过平衡位置，往复移动的幅度逐次减小，最后停回平衡位置附近；这一现象在多次小幅释放试验中都能重复观察到。施加小幅且可逆的力脉冲后，一个采样周期内就能看到位置开始变化，初始移动方向始终与施力方向一致，没有先向相反方向移动或停顿。加力后位置保持连续、不会突然跳变，位置曲线的斜率由零逐渐建立；撤去脉冲后仍会出现幅度逐次减小的往复移动。装置只有一个力执行器和一个主要位置输出，传感器能记录完整的移动过程；在小位移范围内，把脉冲幅度增大一倍时，初始弯曲程度和最大位移也近似按比例增大，未观察到死区、滞回或饱和。载荷小幅改变时，往复移动的周期、衰减速度和位移大小会有小幅到中等变化，但最终仍会回到平衡位置附近。",
        "position",
        "force",
    ],
    [
        "这是一个在水平轨道上运动的低摩擦小车（low-friction cart）。控制输入是双向电机施加的水平力，输出是位置传感器和速度传感器连续记录的小车位置与速度。在多个小幅且可逆的试验中，施加恒定小力后一个采样周期内速度就开始沿施力方向变化，初始运动不会反向或停顿；保持施力时，速度近似以恒定速率变化，位置曲线连续弯曲而不会突然跳变。撤去力后，速度会在较长时间内保持接近撤力瞬间的数值，位置继续沿原方向以近似恒定斜率移动，不会自行减速并返回起点。正向和负向力会产生方向相反的速度变化，力幅增大一倍时速度变化率也近似增大一倍，限定行程和速度范围内未观察到死区、滞回或饱和。装置只有一个电机执行器；位置和速度两个读数描述的是同一段平移运动，不存在第二个执行器或其他独立运动通道。摩擦和负载小幅改变时，速度变化率会有小幅到中等变化，但撤力后的持续移动现象保持不变。",
        "position, velocity",
        "motor force",
    ],
    [
        "这是一个带蒸汽析出的加热储液容器（tank）。控制输入是进液阀门开度，输出是液位传感器连续记录的容器液位。在多个小幅且可逆的阀门试验中，稍微增大阀门开度后一个采样周期内液位就开始变化，但初始会短暂下降，与之后的上升方向相反（opposite direction）；随后下降停止，液位转为上升并逐渐停在更高的恒定位置。稍微减小阀门开度时会观察到镜像过程：液位先短暂上升，随后转为下降并停在较低位置。整个过程中没有纯等待，液位曲线连续且不会突然跳变；阀门恢复原开度后，液位也会逐渐回到原工作位置。装置只有一个阀门执行器和一个主要液位输出，传感器覆盖完整变化过程；在当前工作范围内，把小幅阀门变化增大一倍时，初始反向幅度和最终液位变化也近似按比例增大，未观察到死区、滞回或饱和。蒸汽负荷和进液温度缓慢改变时，短暂反向移动的持续时间、幅度以及最终液位会有小幅到中等变化，但先反向再转向并停稳的现象保持不变。",
        "liquid level",
        "inlet valve",
    ],
    [
        "这是两个通过下部连通管相连的储液容器（interconnected tank levels）。控制输入是分别向两个容器供液的泵 A 和泵 B，输出是两个液位传感器连续记录的液位 A 与液位 B。在多个小幅且可逆的单泵试验中，只提高泵 A 后一个采样周期内两个液位都开始变化，初始均沿上升方向移动，其中液位 A 变化较大、液位 B 变化较小；只提高泵 B 时也会同时看到两个液位上升，但液位 B 的变化更大。分别降低任一泵时，两个液位都会沿相反方向变化，没有先反向或停顿。保持新的泵速后，两个液位最终都会停在新的恒定位置；泵速恢复后，两个液位也逐渐回到原工作位置。两个泵都是独立可调的执行器，两个传感器覆盖完整变化过程；每个泵都会明显改变两个输出，因此不能在试验中把任何一个液位视为只受其中一个泵影响。在当前工作范围内，泵速小幅变化增大一倍时，两条液位曲线的最终变化也近似按比例增大，未观察到死区、滞回或饱和。连通管阻力、泵效率和总出液负荷缓慢变化时，各液位的变化幅度和达到恒定位置所需时间会有中等变化，但每个泵都会影响两个液位的现象保持不变。",
        "level A, level B",
        "pump A, pump B",
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
.flow-strip { display: grid; grid-template-columns: repeat(5, minmax(108px, 1fr)); gap: 6px; margin: 4px 0 12px; }
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
    show_evidence = report.status in {
        "awaiting_specifications",
        "need_more_specifications",
        "specification_conflict",
        "evidence_rejected",
    }
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
        gr.update(visible=show_evidence),
        view["specification_guidance"],
    )


def run_from_ui(
    description,
    observed_outputs,
    actuators,
    safety_bounds,
    forbidden_actions,
    time_scale_hint_s,
    route,
    use_llm,
    base_url,
    model,
    api_key,
    include_trajectory,
):
    try:
        report, state = start_app_run(
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
            forbidden_actions=forbidden_actions,
            time_scale_hint_s=time_scale_hint_s,
        )
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


def submit_evidence_from_ui(
    state,
    model_json,
    validation_json,
    simulation_bounds_confirmed,
    demo_confirmed,
):
    try:
        report, state = submit_app_evidence(
            state,
            model_json=model_json,
            trace_files=None,
            trace_manifest_json="",
            validation_json=validation_json,
            demo_confirmed=demo_confirmed,
            simulation_bounds_confirmed=simulation_bounds_confirmed,
        )
        return _outputs(report, state)
    except Exception as exc:
        raise gr.Error(str(exc)) from exc


def submit_specifications_from_ui(
    state,
    specification_text,
    simulation_bounds_confirmed,
):
    try:
        report, state = submit_app_specifications(
            state,
            specification_text,
            simulation_bounds_confirmed=simulation_bounds_confirmed,
        )
        return _outputs(report, state)
    except Exception as exc:
        raise gr.Error(str(exc)) from exc


def submit_json_from_ui(state, uploaded_json, pasted_json, simulation_bounds_confirmed):
    try:
        report, state = submit_app_json(
            state,
            uploaded_json=uploaded_json,
            pasted_json=pasted_json,
            simulation_bounds_confirmed=simulation_bounds_confirmed,
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
        "**自然语言自动分析：** 使用下方六项控制问题输入；可选择启用 LLM。"
        if natural_language
        else "**开发验证场景：** 使用预注册描述、诊断和 Profile；不会调用 LLM。下方用户输入仅暂时禁用并会被后端忽略，切回主流程后内容仍保留。"
    )
    return (
        note,
        input_update,
        input_update,
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
        "**自然语言自动分析：** 使用下方六项控制问题输入；可选择启用 LLM。",
        "",  # description
        "",  # observed outputs
        "",  # actuators
        "",  # safety bounds
        "",  # forbidden actions
        "",  # dominant time scale
        False,  # include trajectory
        False,  # use LLM
        os.getenv("CFDC_LLM_BASE_URL", ""),
        os.getenv("CFDC_LLM_MODEL", ""),
        "",  # API key
        "",  # supplemental description
        "",  # natural-language specifications
        None,  # uploaded JSON
        "",  # pasted JSON
        "",  # advanced model JSON
        "",  # validation JSON
        False,  # software-simulation boundary confirmation
        False,  # demo confirmation
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
        gr.update(visible=False),
        "",
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
                    "**自然语言自动分析：** 使用下方六项控制问题输入；可选择启用 LLM。"
                )
                description = gr.Textbox(
                    label="控制问题",
                    value="",
                    lines=6,
                    placeholder="描述对象如何运动、能够测量什么、可以施加什么控制，以及已知约束。",
                )
                with gr.Row():
                    observed_outputs = gr.Textbox(
                        label="可观察输出", value="", placeholder="temperature, position"
                    )
                    actuators = gr.Textbox(
                        label="执行器", value="", placeholder="heater, motor force"
                    )
                with gr.Accordion("已知边界与时间尺度（可选）", open=False):
                    safety_bounds = gr.Textbox(
                        label="安全边界",
                        value="",
                        lines=3,
                        placeholder="max_abs_control=1.0\nmax_abs_output=2.0",
                    )
                    forbidden_actions = gr.Textbox(
                        label="禁止实验动作",
                        value="",
                        lines=3,
                        placeholder="free release\npulse",
                    )
                    time_scale_hint_s = gr.Textbox(
                        label="主导时间尺度（秒）",
                        value="",
                        placeholder="例如：2.0；用户模型实验不允许使用默认时间尺度",
                    )
                    include_trajectory = gr.Checkbox(label="保留完整轨迹", value=False)
                with gr.Accordion("LLM Provider", open=False):
                    use_llm = gr.Checkbox(label="启用 LLM 诊断、语义路由与规格整理", value=False)
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
                    run_button = gr.Button("开始诊断", variant="primary", elem_classes="primary-run", scale=4)
                    clear_button = gr.Button("清空", scale=1)
                gr.Examples(
                    examples=EXAMPLES,
                    inputs=[description, observed_outputs, actuators],
                    label="可完成结构诊断的详细示例（随后会按具体对象追问设备规格）",
                )

            with gr.Column(scale=8, min_width=560):
                status = gr.Markdown("### 等待控制问题", elem_id="run-status")
                progress = gr.HTML()
                summary = gr.HTML()
                performance_visual = gr.HTML()
                with gr.Group(visible=False) as clarification_group:
                    gr.Markdown("### 补充诊断证据")
                    question_1 = gr.Textbox(value="", visible=False)
                    question_2 = gr.Textbox(value="", visible=False)
                    question_3 = gr.Textbox(value="", visible=False)
                    question_4 = gr.Textbox(value="", visible=False)
                    supplemental = gr.Textbox(label="补充描述", value="", lines=2)
                    continue_button = gr.Button("提交诊断补充", variant="primary")

                with gr.Group(visible=False) as evidence_group:
                    evidence_requirements = gr.Markdown()
                    simulation_bounds_confirmed = gr.Checkbox(
                        label="我确认所提交的输入/输出范围仅作为本次软件仿真的停止边界",
                        value=False,
                        info=(
                            "这不代表真实硬件安全认证，也不授权向真实物理硬件下发命令。"
                        ),
                    )
                    gr.Markdown("**方式 1（推荐）· 回答当前设备规格问题**")
                    specification_text = gr.Textbox(
                        label="用自然语言补充设备规格",
                        value="",
                        lines=6,
                        placeholder="可以描述已知参数、粘贴手册原文，或说明暂时不知道。未启用 LLM 时，请按上方问题顺序每行填写一个“数值 + 单位”。",
                    )
                    specification_button = gr.Button("提交规格信息", variant="primary")
                    with gr.Accordion("方式 2 · 上传或粘贴 JSON 数据", open=False):
                        uploaded_json = gr.File(
                            label="JSON 数据文件（.json）",
                            file_types=[".json"],
                            type="filepath",
                        )
                        pasted_json = gr.Textbox(
                            label="粘贴 JSON 数据（可选）",
                            value="",
                            lines=8,
                            placeholder=(
                                "可粘贴 dataset 中包含 specification_facts、model、"
                                "experiment 与 eight_segment_evidence 的完整 JSON。"
                            ),
                        )
                        json_button = gr.Button("提交 JSON 数据", variant="primary")
                    with gr.Accordion("方式 3（高级）· 提供完整数值模型", open=False):
                        model_json = gr.Textbox(
                            label="数学模型 JSON",
                            value="",
                            lines=8,
                            placeholder=(
                                '{"kind":"transfer_function","numerator":[1.0],'
                                '"denominator":[2.0,1.0],"input_signal_id":"heater",'
                                '"output_signal_id":"temperature","input_units":"power",'
                                '"output_units":"degC"}'
                            ),
                        )
                        validation_json = gr.Textbox(
                            label="闭环验证条件 JSON（可选）",
                            value="",
                            lines=6,
                            placeholder="参考输入、时长、初始状态、执行器/状态边界和性能指标。",
                        )
                    with gr.Accordion("方式 4 · 运行标准对象演示", open=False):
                        demo_confirmed = gr.Checkbox(
                            label="确认仅运行标准对象演示",
                            value=False,
                            info="演示结果只代表标准 Fixture，不代表我的真实对象。",
                        )
                    evidence_button = gr.Button("提交高级模型 / 运行演示", variant="secondary")

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
                    with gr.Tab("模型响应"):
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
            evidence_group,
            evidence_requirements,
        ]
        run_button.click(
            run_from_ui,
            inputs=[
                description,
                observed_outputs,
                actuators,
                safety_bounds,
                forbidden_actions,
                time_scale_hint_s,
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
                forbidden_actions,
                time_scale_hint_s,
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
        specification_button.click(
            submit_specifications_from_ui,
            inputs=[app_state, specification_text, simulation_bounds_confirmed],
            outputs=output_components,
        )
        json_button.click(
            submit_json_from_ui,
            inputs=[app_state, uploaded_json, pasted_json, simulation_bounds_confirmed],
            outputs=output_components,
        )
        evidence_button.click(
            submit_evidence_from_ui,
            inputs=[
                app_state,
                model_json,
                validation_json,
                simulation_bounds_confirmed,
                demo_confirmed,
            ],
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
                forbidden_actions,
                time_scale_hint_s,
                include_trajectory,
                use_llm,
                base_url,
                model,
                api_key,
                supplemental,
                specification_text,
                uploaded_json,
                pasted_json,
                model_json,
                validation_json,
                simulation_bounds_confirmed,
                demo_confirmed,
                *output_components,
            ],
        )
    return demo
