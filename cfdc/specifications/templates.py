from __future__ import annotations

from cfdc.models import (
    SpecificationCompletionPath,
    SpecificationFieldDefinition,
    SpecificationTemplate,
    SpecificationTemplateCatalog,
)


def _field(
    fact_id: str,
    label: str,
    unit: str,
    prompt: str,
    why: str,
    example: str,
    *,
    accepted_units: list[str] | None = None,
    unit_policy: str = "dimensioned",
    answer_kind: str = "number",
    where_to_find: str = (
        "可查看设备手册、铭牌、供应商规格页，或填写您已经知道的定量行为；暂时找不到可以明确回答不知道。"
    ),
) -> SpecificationFieldDefinition:
    return SpecificationFieldDefinition(
        fact_id=fact_id,
        label=label,
        canonical_unit=unit,
        accepted_units=accepted_units or [unit],
        unit_policy=unit_policy,
        prompt_template=prompt,
        why_needed=why,
        where_to_find=where_to_find,
        example_template=example,
        answer_kind=answer_kind,
    )


_INPUT_CHANGE = _field(
    "input_change",
    "已知输入变化量",
    "input_unit",
    "当 {input} 改变一个已知数值时，改变了多少？请同时写单位。",
    "需要用真实输入变化作为比例基准，不能使用归一化 Fixture 数值。",
    "例如：加热功率增加 1 kW，或阀门开度增加 10%。",
    accepted_units=["input_unit", "normalized_input", "W", "kW", "%", "N", "Nm"],
    unit_policy="open",
)
_STEADY_OUTPUT = _field(
    "steady_output_change",
    "最终输出变化量",
    "output_unit",
    "上述 {input} 变化后，{output} 的最终变化是多少？可以引用手册中的稳态影响。",
    "输入与最终输出的比例决定当前对象的静态作用强度。",
    "例如：功率增加 1 kW 后，最终温度提高 10 degC。",
    accepted_units=["output_unit", "degC", "K", "m", "Pa", "%", "rad"],
    unit_policy="open",
)
_RESPONSE_TIME = _field(
    "response_time_s",
    "63% 响应时间",
    "s",
    "如果已经知道，{output} 达到最终变化约 63% 需要多久？也可以粘贴手册中的时间常数。",
    "该时间决定控制器应当多快，不能默认使用 1 秒。",
    "例如：约 30 s 达到最终温升的 63%。",
    accepted_units=["s", "ms", "min"],
)
_INPUT_MIN = _field(
    "input_min",
    "输入仿真下限",
    "input_unit",
    "本次软件仿真中，{input} 采用的运行下限是多少？请注明单位。",
    "仿真候选必须遵守用户声明的输入停止边界；这不等同于硬件额定下限。",
    "例如：仿真中的最小加热功率为 0 kW。",
    accepted_units=["input_unit", "normalized_input", "W", "kW", "%", "N", "Nm"],
    unit_policy="open",
)
_INPUT_MAX = _field(
    "input_max",
    "输入仿真上限",
    "input_unit",
    "本次软件仿真中，{input} 采用的运行上限是多少？请注明单位。",
    "仿真候选必须遵守用户声明的输入停止边界；这不等同于硬件额定上限。",
    "例如：仿真中的最大加热功率为 2 kW。",
    accepted_units=["input_unit", "normalized_input", "W", "kW", "%", "N", "Nm"],
    unit_policy="open",
)
_OUTPUT_MIN = _field(
    "output_min",
    "输出仿真下限",
    "output_unit",
    "本次软件仿真中，{output} 采用的停止下限是多少？请注明单位。",
    "缺少输出停止边界时不能运行数值候选；该边界不代表硬件安全认证。",
    "例如：仿真在温度低于 -20 degC 时停止。",
    accepted_units=["output_unit", "degC", "K", "m", "Pa", "%", "rad"],
    unit_policy="open",
)
_OUTPUT_MAX = _field(
    "output_max",
    "输出仿真上限",
    "output_unit",
    "本次软件仿真中，{output} 采用的停止上限是多少？请注明单位。",
    "缺少输出停止边界时不能运行数值候选；该边界不代表硬件安全认证。",
    "例如：仿真在温度高于 80 degC 时停止。",
    accepted_units=["output_unit", "degC", "K", "m", "Pa", "%", "rad"],
    unit_policy="open",
)


def _first_order_template(profile_id: str, *, delay: bool) -> SpecificationTemplate:
    fields = [
        _INPUT_CHANGE,
        _STEADY_OUTPUT,
        _RESPONSE_TIME,
        _INPUT_MIN,
        _INPUT_MAX,
        _OUTPUT_MIN,
        _OUTPUT_MAX,
    ]
    required = [item.fact_id for item in fields]
    if delay:
        delay_field = _field(
            "dead_time_s",
            "纯等待时间",
            "s",
            "{input} 改变后，{output} 在开始变化前会等待多久？请提供已知规格值。",
            "显著纯时延会改变可用的控制带宽。",
            "例如：输入改变约 2 s 后输出才开始变化。",
            accepted_units=["s", "ms", "min"],
        )
        fields.insert(3, delay_field)
        required.insert(3, "dead_time_s")
    return SpecificationTemplate(
        template_id=f"spec_{profile_id}",
        method_profile_id=profile_id,
        user_summary="需要确认当前对象的输入输出比例、响应速度和本次软件仿真运行边界。",
        fields=fields,
        completion_paths=[
            SpecificationCompletionPath(
                path_id="known_behavior", required_fact_ids=required
            )
        ],
        compiler_id="first_order_delay" if delay else "first_order",
    )


def _second_order_template() -> SpecificationTemplate:
    fields = [
        _field(
            "oscillation_period_s",
            "相邻同向峰值间隔",
            "s",
            "{output} 相邻两次同方向最大值大约相隔多久？如果手册给出固有频率，也可以粘贴原文。",
            "相邻两次峰值间隔用于计算这台装置自身的振动速度。",
            "例如：相邻两次向右最大位移相隔 2 s。",
            accepted_units=["s", "ms"],
        ),
        _field(
            "successive_peak_ratio",
            "相邻峰值幅度比例",
            "ratio",
            "下一次同方向最大幅度大约是前一次的多少倍或百分之多少？",
            "峰值衰减比例用于计算阻尼，不能从“振动较弱”推成数值。",
            "例如：下一次峰值约为前一次的 50%。",
            accepted_units=["ratio", "%"],
        ),
        _INPUT_CHANGE,
        _field(
            "acceleration_change",
            "对应运动变化",
            "m/s^2",
            "已知 {input} 变化时，{output} 对应的初始加速度或角加速度是多少？",
            "该比例决定执行器推动当前对象的实际能力。",
            "例如：施加 2 N 后初始加速度约 4 m/s^2。",
            accepted_units=["m/s^2", "rad/s^2"],
            unit_policy="motion_acceleration",
        ),
        _field(
            "mass_kg",
            "有效运动质量",
            "kg",
            "运动部件连同负载大约多重？可填写产品重量或有效运动质量。",
            "质量与刚度、阻尼可构成可执行的物理模型。",
            "例如：运动部分和负载合计 5 kg。",
            accepted_units=["kg", "g"],
        ),
        _field(
            "stiffness_n_m",
            "等效刚度",
            "N/m",
            "手册是否给出弹簧或回复机构的刚度？请粘贴数值和单位。",
            "刚度决定回复力和振动速度。",
            "例如：等效刚度 200 N/m。",
            accepted_units=["N/m", "Nm/rad"],
        ),
        _field(
            "damping_n_s_m",
            "等效阻尼",
            "N*s/m",
            "手册是否给出阻尼或粘性摩擦系数？请粘贴数值和单位。",
            "阻尼决定振动衰减速度。",
            "例如：等效阻尼 8 N*s/m。",
            accepted_units=["N*s/m", "Nm*s/rad"],
        ),
        _field(
            "actuator_force_per_input",
            "执行器力度换算",
            "N/input_unit",
            "{input} 的一个命令单位对应多少实际推力或转矩？",
            "需要把执行器命令换算成作用在对象上的物理量。",
            "例如：100% 命令对应 20 N。",
            accepted_units=["N/input_unit", "Nm/input_unit"],
            unit_policy="actuator_per_input",
        ),
        _INPUT_MIN,
        _INPUT_MAX,
        _OUTPUT_MIN,
        _OUTPUT_MAX,
    ]
    bounds = ["input_min", "input_max", "output_min", "output_max"]
    return SpecificationTemplate(
        template_id="spec_second_order_oscillator",
        method_profile_id="second_order_oscillator",
        user_summary="需要确认这台振动装置的惯性、衰减速度和执行器实际力度。",
        fields=fields,
        completion_paths=[
            SpecificationCompletionPath(
                path_id="known_behavior",
                required_fact_ids=[
                    "oscillation_period_s",
                    "successive_peak_ratio",
                    "input_change",
                    "acceleration_change",
                    *bounds,
                ],
            ),
            SpecificationCompletionPath(
                path_id="physical_parameters",
                required_fact_ids=[
                    "mass_kg",
                    "stiffness_n_m",
                    "damping_n_s_m",
                    "actuator_force_per_input",
                    *bounds,
                ],
            ),
        ],
        compiler_id="second_order",
    )


def _double_integrator_template() -> SpecificationTemplate:
    fields = [
        _INPUT_CHANGE,
        _field(
            "acceleration_change",
            "对应加速度变化",
            "m/s^2",
            "当 {input} 改变一个已知数值时，运动加速度或角加速度改变多少？",
            "输入到加速度的比例决定该运动对象的控制参数。",
            "例如：电机力增加 2 N 时加速度增加 1 m/s^2。",
            accepted_units=["m/s^2", "rad/s^2"],
            unit_policy="motion_acceleration",
        ),
        _field(
            "mass_kg",
            "有效质量或惯量",
            "kg",
            "运动部件和负载的有效质量是多少？旋转系统也可提供转动惯量。",
            "质量或惯量可与执行器力度换算出加速度增益。",
            "例如：移动总质量 10 kg。",
            accepted_units=["kg", "kg*m^2"],
        ),
        _field(
            "actuator_force_per_input",
            "执行器力度换算",
            "N/input_unit",
            "{input} 的一个命令单位对应多少实际力或转矩？",
            "需要把命令换算成运动加速度。",
            "例如：100% 命令对应 50 N。",
            accepted_units=["N/input_unit", "Nm/input_unit"],
            unit_policy="actuator_per_input",
        ),
        _field(
            "motion_time_scale_s",
            "典型运动时间尺度",
            "s",
            "在正常工作中，{output} 完成一次典型目标变化大约需要多久？",
            "该时间只用于确定保守的初始控制带宽，不能默认成 1 秒。",
            "例如：小车完成一次正常位置调整约需 5 s。",
            accepted_units=["s", "ms", "min"],
        ),
        _INPUT_MIN,
        _INPUT_MAX,
        _OUTPUT_MIN,
        _OUTPUT_MAX,
    ]
    bounds = ["input_min", "input_max", "output_min", "output_max"]
    return SpecificationTemplate(
        template_id="spec_double_integrator",
        method_profile_id="double_integrator",
        user_summary="需要确认执行器命令能产生多大加速度，以及运动范围。",
        fields=fields,
        completion_paths=[
            SpecificationCompletionPath(
                path_id="known_behavior",
                required_fact_ids=[
                    "input_change",
                    "acceleration_change",
                    "motion_time_scale_s",
                    *bounds,
                ],
            ),
            SpecificationCompletionPath(
                path_id="physical_parameters",
                required_fact_ids=[
                    "mass_kg",
                    "actuator_force_per_input",
                    "motion_time_scale_s",
                    *bounds,
                ],
            ),
        ],
        compiler_id="double_integrator",
    )


def _nmp_template() -> SpecificationTemplate:
    fields = [
        _INPUT_CHANGE,
        _STEADY_OUTPUT,
        _field(
            "inverse_peak_change",
            "初始反向变化",
            "output_unit",
            "{input} 改变后，{output} 初始反向移动的最大幅度是多少？",
            "反向幅度决定逆响应限制，不能只依据“先反向”补一个固定值。",
            "例如：最终上升 10 cm 前，先下降了 2 cm。",
            accepted_units=["output_unit", "degC", "m", "%"],
            unit_policy="open",
        ),
        _field(
            "inverse_recovery_time_s",
            "反向恢复时间",
            "s",
            "{output} 从初始反向峰值恢复并重新穿过原工作点需要多久？",
            "恢复时间用于构造对象专属的逆响应近似模型。",
            "例如：约 3 s 后重新穿过原液位。",
            accepted_units=["s", "ms", "min"],
        ),
        _RESPONSE_TIME,
        _INPUT_MIN,
        _INPUT_MAX,
        _OUTPUT_MIN,
        _OUTPUT_MAX,
    ]
    return SpecificationTemplate(
        template_id="spec_nmp_inverse_response",
        method_profile_id="nmp_inverse_response",
        user_summary="需要确认最终作用、初始反向幅度、恢复速度和安全范围。",
        fields=fields,
        completion_paths=[
            SpecificationCompletionPath(
                path_id="known_inverse_behavior",
                required_fact_ids=[item.fact_id for item in fields],
            )
        ],
        compiler_id="nmp_inverse_response",
    )


def _structured_only_template() -> SpecificationTemplate:
    field = _field(
        "complete_numeric_model",
        "完整数值模型",
        "structured_model",
        "该对象属于任意高阶或不稳定系统，仅凭语言规格不足以安全构造模型；请改用完整数值模型，并提供全部参数与初始状态。",
        "只给自然频率或一个增益无法确定高阶不稳定动态。",
        "可提供数值传递函数、状态空间矩阵，或选择已注册的白名单物理模板。",
        accepted_units=["structured_model"],
        answer_kind="structured_model",
        unit_policy="structured",
    )
    return SpecificationTemplate(
        template_id="spec_generic_unstable_higher_order",
        method_profile_id="generic_unstable_higher_order",
        user_summary="当前对象需要完整数值模型，系统不会从少量描述补造高阶动态。",
        fields=[field],
        completion_paths=[
            SpecificationCompletionPath(
                path_id="structured_model_only", required_fact_ids=[field.fact_id]
            )
        ],
        compiler_id="unsupported_natural_language",
    )


def _cartpole_template() -> SpecificationTemplate:
    definitions = [
        ("cart_mass_kg", "小车质量", "kg", "小车连同固定负载的质量是多少？"),
        ("pole_mass_kg", "摆杆质量", "kg", "摆杆的质量是多少？"),
        ("com_length_m", "摆杆质心距离", "m", "转轴到摆杆质心的距离是多少？"),
        (
            "pole_inertia_kg_m2",
            "摆杆转动惯量",
            "kg*m^2",
            "摆杆绕转轴的转动惯量是多少？",
        ),
        (
            "cart_friction_n_s_m",
            "小车摩擦",
            "N*s/m",
            "手册给出的小车粘性摩擦系数是多少？",
        ),
        ("gravity_m_s2", "重力加速度", "m/s^2", "模型使用的重力加速度是多少？"),
        ("force_limit_n", "推力限制", "N", "小车执行器允许的最大双向推力是多少？"),
        (
            "cart_position_limit_m",
            "小车行程",
            "m",
            "小车中心位置允许的最大绝对行程是多少？",
        ),
    ]
    fields = [
        _field(
            fid,
            label,
            unit,
            prompt,
            "该数值是小车倒立摆白名单模型的必需物理参数。",
            f"例如：{label}=1 {unit}。",
        )
        for fid, label, unit, prompt in definitions
    ]
    return SpecificationTemplate(
        template_id="spec_underactuated_cartpole",
        method_profile_id="underactuated_cartpole",
        user_summary="需要确认这套小车倒立摆的全部质量、几何、摩擦和执行器边界。",
        fields=fields,
        completion_paths=[
            SpecificationCompletionPath(
                path_id="registered_cartpole",
                required_fact_ids=[item.fact_id for item in fields],
            )
        ],
        compiler_id="cartpole",
    )


def _vtol_template() -> SpecificationTemplate:
    definitions = [
        ("mass_kg", "飞行器质量", "kg", "飞行器连同当前载荷的总质量是多少？"),
        (
            "pitch_inertia_kg_m2",
            "俯仰转动惯量",
            "kg*m^2",
            "手册或辨识结果中的俯仰转动惯量是多少？",
        ),
        ("gravity_m_s2", "重力加速度", "m/s^2", "模型使用的重力加速度是多少？"),
        ("linear_drag_n_s_m", "平移阻力", "N*s/m", "飞行器的线性阻力系数是多少？"),
        ("pitch_damping_n_m_s", "俯仰阻尼", "Nm*s/rad", "俯仰轴阻尼系数是多少？"),
        ("thrust_min_n", "最小推力", "N", "飞行器推进系统的最小总推力是多少？"),
        ("thrust_max_n", "最大推力", "N", "飞行器推进系统的最大总推力是多少？"),
        (
            "torque_limit_n_m",
            "最大俯仰转矩",
            "Nm",
            "姿态执行器允许的最大俯仰转矩是多少？",
        ),
        (
            "response_time_s",
            "典型响应时间",
            "s",
            "飞行器完成一次正常高度调整大约需要多久？",
        ),
        ("max_tilt_rad", "最大安全倾角", "rad", "允许的最大安全倾角是多少？"),
        ("max_altitude_error", "最大高度误差", "m", "允许的最大高度偏差是多少？"),
    ]
    fields = [
        _field(
            fid,
            label,
            unit,
            prompt,
            "该数值是 VTOL 白名单模型的必需物理参数。",
            f"例如：{label}=1 {unit}。",
        )
        for fid, label, unit, prompt in definitions
    ]
    return SpecificationTemplate(
        template_id="spec_vtol_cascaded",
        method_profile_id="vtol_cascaded",
        user_summary="需要确认这架飞行器的质量、惯量、阻尼和推力/转矩限制。",
        fields=fields,
        completion_paths=[
            SpecificationCompletionPath(
                path_id="registered_vtol",
                required_fact_ids=[item.fact_id for item in fields],
            )
        ],
        compiler_id="vtol",
    )


def _mimo_template() -> SpecificationTemplate:
    fields = [
        _field(
            "local_gain_matrix",
            "局部输入输出影响矩阵",
            "output/input",
            "请提供每个 {input} 对每个 {output} 的已知局部影响，包括交叉影响；按输出行、输入列填写 2×2 数值矩阵。",
            "强耦合对象必须使用当前对象的完整局部增益矩阵，不能复用标准矩阵。",
            "例如：[[2.0, 0.7], [0.5, 1.6]] output/input。",
            accepted_units=["output/input"],
            answer_kind="matrix",
            unit_policy="open",
        ),
        _field(
            "local_time_constant_s",
            "局部响应时间",
            "s",
            "在当前工作点，各输出达到最终变化约 63% 的代表性时间是多少？",
            "需要从当前对象的响应速度确定多变量控制带宽。",
            "例如：两个液位通道代表性时间约 15 s。",
            accepted_units=["s", "ms", "min"],
        ),
        _INPUT_MIN,
        _INPUT_MAX,
        _OUTPUT_MIN,
        _OUTPUT_MAX,
    ]
    return SpecificationTemplate(
        template_id="spec_mimo_2x2_coupled",
        method_profile_id="mimo_2x2_coupled",
        user_summary="需要确认每个输入对每个输出的直接及交叉影响、响应速度和边界。",
        fields=fields,
        completion_paths=[
            SpecificationCompletionPath(
                path_id="known_local_model",
                required_fact_ids=[item.fact_id for item in fields],
            )
        ],
        compiler_id="mimo_first_order",
    )


def default_specification_template_catalog() -> SpecificationTemplateCatalog:
    return SpecificationTemplateCatalog(
        templates=[
            _first_order_template("first_order_lag", delay=False),
            _first_order_template("first_order_lag_with_delay", delay=True),
            _second_order_template(),
            _double_integrator_template(),
            _nmp_template(),
            _structured_only_template(),
            _cartpole_template(),
            _vtol_template(),
            _mimo_template(),
        ]
    )


def specification_template_for_profile(method_profile_id: str) -> SpecificationTemplate:
    for template in default_specification_template_catalog().templates:
        if template.method_profile_id == method_profile_id:
            return template
    raise ValueError(
        f"no specification template is registered for method profile '{method_profile_id}'"
    )
