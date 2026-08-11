from __future__ import annotations

import re
from collections.abc import Iterable

from cfdc.diagnosis.llm import (
    DeterministicDiagnosticAdapter,
    DiagnosticAdapter,
    validate_agent_payload,
)
from cfdc.models import (
    ArchetypeClass,
    ArchetypeClassification,
    ControllabilityObservabilityAssessment,
    ControllabilityObservabilityField,
    CouplingAssessment,
    CouplingField,
    DelayAssessment,
    NonlinearityAssessment,
    NonlinearityField,
    PhaseAssessment,
    PhaseField,
    RelativeDegreeAssessment,
    RelativeDegreeField,
    SignificantDelayField,
    StabilityAssessment,
    StabilityField,
    StructuralDiagnosis,
    SystemDescription,
    UncertaintyAssessment,
    UncertaintyField,
)


def _contains(text: str, terms: Iterable[str]) -> bool:
    return any(term in text for term in terms)


def _has_nonminimum_phase_evidence(text: str) -> bool:
    """Require positive inverse-response evidence instead of matching negated words."""

    negated = (
        (
            r"(?:does not|doesn't|never|without|no)\s+(?:\w+\s+){0,7}"
            r"(?:opposite|reverse|undershoot|unfavorable)"
        ),
        r"(?:不会|没有|并非|不是)[^。；，,.]{0,28}(?:相反|反向|不利)",
    )
    if any(re.search(pattern, text, flags=re.IGNORECASE) for pattern in negated):
        return False
    positive = (
        r"(?:first|initially|initial)\s+(?:\w+\s+){0,8}(?:opposite|reverse|unfavorable)",
        r"(?:opposite|reverse|unfavorable)\s+(?:\w+\s+){0,8}(?:before|then)",
        r"\bundershoot(?:s|ing|ed)?\b",
        r"\bnon[- ]?minimum[- ]?phase\b",
        r"(?:先|首先)[^。；，,.]{0,24}(?:相反|反向|不利)",
        r"(?:相反|反向|不利)[^。；，,.]{0,18}(?:随后|然后|再|之后)",
        r"非最小相位",
    )
    return any(re.search(pattern, text, flags=re.IGNORECASE) for pattern in positive)


def _has_significant_dead_time_evidence(text: str) -> bool:
    negated = (
        (
            r"(?:no|without|does not have|is not)\s+(?:\w+\s+){0,6}"
            r"(?:dead time|pure delay|pause|silent interval|transport delay)"
        ),
        r"(?:没有|不会出现|无|并无)[^。；，,.]{0,30}(?:停顿|静默|纯时延|纯等待|输运时延)",
    )
    if any(re.search(pattern, text, flags=re.IGNORECASE) for pattern in negated):
        return False
    positive = (
        r"\b(?:noticeable|visible|separate|independent)\s+(?:dead time|pause|delay|silent interval)\b",
        r"\b(?:pure|transport)\s+(?:dead time|delay)\b",
        r"\bdead time\b",
        r"(?:明显|可见|独立)[^。；，,.]{0,18}(?:停顿|静默区间|纯等待)",
        r"(?:显著纯时延|输运时延|纯等待时间)",
    )
    return any(re.search(pattern, text, flags=re.IGNORECASE) for pattern in positive)


def _has_explicit_oscillation_evidence(text: str) -> bool:
    negated = (
        (
            r"(?:does not|doesn't|never|without|no)\s+(?:\w+\s+){0,6}"
            r"(?:ring|oscillat|vibrat|repeated peaks)"
        ),
        r"(?:不会|没有|无)[^。；，,.]{0,24}(?:振荡|振动|重复峰值|往复)",
    )
    if any(re.search(pattern, text, flags=re.IGNORECASE) for pattern in negated):
        return False
    if _contains(
        text,
        [
            "oscillat",
            "vibrat",
            "reson",
            "spring",
            "natural frequency",
            "ringing",
            "repeated peaks",
            "successive peaks",
            "振荡",
            "振动",
            "谐振",
            "弹簧",
            "固有频率",
            "相邻峰值",
            "往复运动",
        ],
    ):
        return True
    exact_second_order = _contains(
        text, ["second-order", "second order", "二阶系统", "二阶对象"]
    )
    upper_bound_only = _contains(
        text,
        ["at most two", "no more than two", "up to two", "至多两个", "至多经过两个"],
    )
    return exact_second_order and not upper_bound_only


def _has_explicit_minimum_phase_direction(text: str) -> bool:
    patterns = (
        (
            r"(?:does not|doesn't|never|without|no)\s+(?:\w+\s+){0,7}"
            r"(?:opposite|reverse|undershoot|unfavorable)"
        ),
        r"(?:first|initial)\s+(?:\w+\s+){0,8}(?:final|expected)\s+direction",
        r"(?:不会|没有|并非|不是)[^。；，,.]{0,28}(?:相反|反向|不利)",
        r"首次有效变化[^。；]{0,24}(?:最终方向一致|预期方向一致)",
    )
    return any(re.search(pattern, text, flags=re.IGNORECASE) for pattern in patterns)


def _has_explicit_no_dead_time(text: str) -> bool:
    patterns = (
        (
            r"(?:no|without|does not have|is not)\s+(?:\w+\s+){0,6}"
            r"(?:dead time|pure delay|pause|silent interval|transport delay)"
        ),
        r"(?:没有|不会出现|无|并无)[^。；，,.]{0,30}(?:停顿|静默|纯时延|纯等待|输运时延)",
        r"(?:starts|begins)\s+promptly",
        r"及时开始",
    )
    return any(re.search(pattern, text, flags=re.IGNORECASE) for pattern in patterns)


def _direct_eight_segment_assessments(text: str) -> dict[str, str]:
    """Read the dataset/UI eight-sentence evidence contract without keyword leakage."""

    patterns: dict[str, list[tuple[str, tuple[str, ...]]]] = {
        "open_loop_stability": [
            (
                StabilityAssessment.STABLE.value,
                ("settles or remains bounded", "会收敛或保持有界"),
            ),
            (
                StabilityAssessment.MARGINAL.value,
                (
                    "retain an offset or drift",
                    "retains an offset or keeps drifting",
                    "保持偏差或继续漂移",
                    "会保留偏差或继续漂移",
                ),
            ),
            (
                StabilityAssessment.UNSTABLE.value,
                (
                    "continues to grow rather than return",
                    "keeps growing instead of returning",
                    "偏差会继续增大而不会自行返回",
                    "会继续增大而不会自行返回",
                ),
            ),
        ],
        "minimum_phase": [
            (
                PhaseAssessment.MINIMUM_PHASE.value,
                (
                    "follows its eventual direction and does not move the opposite way first",
                    "starts in its final direction rather than moving the opposite way first",
                    "首次有效变化与最终方向一致，不会先向相反方向运动",
                    "开始时就沿最终方向变化，不会先向相反方向运动",
                    "初始方向与最终方向一致，没有反向响应",
                ),
            ),
            (
                PhaseAssessment.NONMINIMUM_PHASE.value,
                (
                    "moves in an unfavorable or opposite direction before turning",
                    "first moves in an unfavorable or opposite direction before turning",
                    "首次有效变化会先沿不利或相反方向运动",
                    "开始时会先沿不利或相反方向运动，随后才转向",
                ),
            ),
        ],
        "significant_delay": [
            (
                DelayAssessment.SIGNIFICANT.value,
                (
                    "a visible pause separates the command",
                    "a visible quiet interval separates the command",
                    "命令与首次记录响应之间存在可见停顿",
                    "命令与首次变化之间有一段清楚可见的静默区间",
                ),
            ),
            (
                DelayAssessment.NOT_SIGNIFICANT.value,
                (
                    "begins promptly without a separate silent interval",
                    "begins within one sample without a separate silent interval",
                    "首次记录变化会及时开始，不会出现独立静默区间",
                    "一个采样周期内就开始变化，不会出现独立静默区间",
                    "没有独立的静默延迟区间",
                ),
            ),
        ],
        "relative_degree": [
            (
                RelativeDegreeAssessment.LOW.value,
                (
                    "no more than two dominant storage or integration stages",
                    "one or two dominant storage or integration processes",
                    "至多经过两个主导储能或积分环节",
                    "只涉及一到两个主导储能或积分过程",
                    "响应呈单调的一阶形状",
                    "只观察到一个明显的快慢阶段",
                ),
            ),
            (
                RelativeDegreeAssessment.HIGH.value,
                (
                    "three or more successive storage or integration stages",
                    "at least three successive storage or integration processes",
                    "至少经过三个连续储能或积分环节",
                    "至少涉及三个连续的储能或积分过程",
                ),
            ),
        ],
        "controllability_observability": [
            (
                ControllabilityObservabilityAssessment.ADEQUATE.value,
                (
                    "every relevant motion mode appear",
                    "all relevant motion can be reconstructed from these synchronized records",
                    "每个相关运动模态至少出现在一项记录中",
                    "这些同步记录足以重建所有相关运动",
                    "相关运动可以由这些同步记录重建",
                ),
            ),
            (
                ControllabilityObservabilityAssessment.INADEQUATE.value,
                (
                    "one pole-zero-canceled mode absent from the recordings and unreachable",
                    "a pole-zero-cancelled mode is absent from the records and cannot be excited",
                    "一个极零相消模态不出现在记录中，也无法由给定激励到达",
                    "一个被极零相消的模态既不出现在记录中，也无法由输入激发",
                ),
            ),
        ],
        "nonlinearity_strength": [
            (
                NonlinearityAssessment.WEAK.value,
                (
                    "small positive and negative trials remain smooth, reversible, and nearly proportional",
                    "small positive and negative trials are smooth, reversible, and nearly proportional",
                    "produce smooth, reversible, and nearly proportional responses",
                    "produces smooth, reversible, and nearly proportional responses",
                    "小幅正向和反向试验保持平滑、可逆且近似成比例",
                    "小幅正向和反向试验都平滑、可逆且近似成比例",
                    "响应平滑、可逆且近似成比例",
                    "正反方向近似对称且成比例",
                ),
            ),
            (
                NonlinearityAssessment.STATIC_COMPENSABLE.value,
                (
                    "departure from proportional behavior stays in this fixed input-output rule",
                    "nonproportional behavior is confined to this fixed input-output rule",
                    "偏离比例关系的现象只存在于这一固定输入输出规律中",
                    "非比例现象只存在于这条固定输入输出规律中",
                ),
            ),
            (
                NonlinearityAssessment.STRONG_DYNAMIC.value,
                (
                    "response law changes with the evolving state",
                    "response law itself changes as the state evolves",
                    "响应规律会随状态演化",
                    "响应规律本身会随状态演化",
                ),
            ),
        ],
        "coupling_severity": [
            (
                CouplingAssessment.SISO.value,
                (
                    "one principal action-to-recording path",
                    "one main physical route from actuation to the measured motion",
                    "一条主要动作到记录量的通道",
                    "只有一条从执行作用到被测运动的主要物理通道",
                ),
            ),
            (
                CouplingAssessment.WEAK_MIMO.value,
                (
                    "several recordings share internal motion",
                    "several readings describe shared internal motion",
                    "多个记录量共享内部运动",
                    "多个读数描述的是彼此共享的内部运动",
                ),
            ),
            (
                CouplingAssessment.SEVERE_MIMO.value,
                (
                    "changing any one of several actuators",
                    "moving any one of the actuators noticeably changes several outputs",
                    "改变任一执行器都会明显带动多个记录量",
                    "改变任一执行器都会明显改变多个输出",
                ),
            ),
            (
                CouplingAssessment.UNDERACTUATED.value,
                (
                    "fewer independent actuators than regulated coordinates",
                    "there are fewer independent actuators than controlled coordinates",
                    "独立执行器少于受控坐标",
                    "独立执行器的数量少于受控坐标",
                ),
            ),
            (
                CouplingAssessment.CASCADED.value,
                (
                    "outer response appears only through",
                    "outer motion is produced only through a separately stabilized inner loop",
                    "外层响应只能通过单独稳定的内层",
                    "外层运动只能通过一个单独稳定的内环产生",
                ),
            ),
        ],
        "uncertainty_magnitude": [
            (
                UncertaintyAssessment.SMALL.value,
                (
                    "motion direction, response timing, and final level remain almost unchanged",
                    "direction, response timing, and final level stay almost unchanged",
                    "运动方向、响应时机和最终水平几乎不变",
                    "运动方向、响应时机和最终水平都几乎不变",
                ),
            ),
            (
                UncertaintyAssessment.MODERATE.value,
                (
                    "shift the response rate and final level modestly",
                    "change the response rate and final level by a modest amount",
                    "只会适度改变响应速度和最终水平",
                    "会使响应速度和最终水平发生适度变化",
                ),
            ),
            (
                UncertaintyAssessment.LARGE.value,
                (
                    "can materially alter",
                    "can materially change",
                    "can substantially change the response rate, final level, or safe excursion",
                    "都可能明显改变",
                    "可能大幅改变响应速度、最终水平或安全活动范围",
                ),
            ),
        ],
    }
    resolved: dict[str, str] = {}
    for field_name, choices in patterns.items():
        matches = [
            assessment
            for assessment, phrases in choices
            if any(phrase in text for phrase in phrases)
        ]
        if len(matches) == 1:
            resolved[field_name] = matches[0]
    if "只有一个主要控制输入" in text and "一个被测输出" in text:
        resolved["coupling_severity"] = CouplingAssessment.SISO.value
    if (
        "稳态增益保持在" in text
        and "响应时间保持在" in text
        and "通道结构没有改变" in text
    ):
        resolved["uncertainty_magnitude"] = UncertaintyAssessment.SMALL.value
    return resolved


def infer_description_field_assessment(
    diagnostic_field_id: str,
    excerpt: str,
) -> str | None:
    """Parse one checklist excerpt only for the field it is claimed to answer.

    The general benchmark diagnosis intentionally uses cross-field context.  A
    description checklist excerpt has a stricter trust boundary: a sentence about
    record reconstruction, for example, must not also prove stability, delay, or
    coupling merely because broad plant keywords happen to occur in it.
    """

    if diagnostic_field_id not in {
        "open_loop_stability",
        "minimum_phase",
        "significant_delay",
        "relative_degree",
        "controllability_observability",
        "nonlinearity_strength",
        "coupling_severity",
        "uncertainty_magnitude",
    }:
        raise ValueError(f"unsupported diagnostic field: {diagnostic_field_id}")
    text = excerpt.casefold()
    if re.search(
        r"(?:\b(?:unknown|unsupported|not known|cannot determine)\b|"
        r"未知|不知道|尚不清楚|不清楚|无法确定)",
        text,
    ):
        return None

    contradicted_affirmative = {
        "open_loop_stability": (
            r"(?:(?:does not|doesn't|will not|won't|cannot).{0,24}"
            r"(?:settle|stabili|remain bounded)|"
            r"(?:不会|不能|无法|未能).{0,18}(?:收敛|稳定|保持有界))"
        ),
        "minimum_phase": (
            r"(?:(?:does not|doesn't|will not|won't).{0,24}"
            r"(?:final|expected) direction|"
            r"(?:不会|不能|未).{0,18}(?:沿最终方向|与最终方向一致))"
        ),
        "significant_delay": (
            r"(?:(?:does not|doesn't|will not|won't).{0,30}"
            r"(?:start|begin).{0,18}(?:promptly|within one sample)|"
            r"(?:不会|不能|未).{0,28}(?:一个采样周期|及时|立即).{0,18}"
            r"(?:开始|变化))"
        ),
    }
    contradiction = contradicted_affirmative.get(diagnostic_field_id)
    if contradiction is not None and re.search(contradiction, text):
        return None

    direct = _direct_eight_segment_assessments(text).get(diagnostic_field_id)
    if direct is not None:
        return direct

    if diagnostic_field_id == "open_loop_stability":
        negated_growth = re.search(
            r"(?:(?:no|not|never|without|does not|doesn't).{0,25}"
            r"(?:grow|diverg|unbound)|(?:没有|不会|未).{0,20}"
            r"(?:增长|增大|发散|无界))",
            text,
        )
        if negated_growth is None and re.search(
            r"(?:grow|diverg|unbound|增长|增大|发散|无界)", text
        ):
            return StabilityAssessment.UNSTABLE.value
        if re.search(r"(?:drift|retain an offset|漂移|保留偏差)", text):
            return StabilityAssessment.MARGINAL.value
        if re.search(
            r"(?:settles?|stabilizes?|\bstable\b|becomes stable|remains stable|"
            r"remain bounded|decay|decrease|收敛|逐渐稳定|最终稳定|保持稳定|"
            r"保持有界|逐渐减小|衰减)",
            text,
        ):
            return StabilityAssessment.STABLE.value
        return None
    if diagnostic_field_id == "minimum_phase":
        if _has_nonminimum_phase_evidence(text):
            return PhaseAssessment.NONMINIMUM_PHASE.value
        if _has_explicit_minimum_phase_direction(text) or re.search(
            r"(?:initial|first|最初|首次|开始).{0,35}"
            r"(?:same as|aligned with|一致).{0,18}(?:final|最终)",
            text,
        ):
            return PhaseAssessment.MINIMUM_PHASE.value
        return None
    if diagnostic_field_id == "significant_delay":
        if _has_significant_dead_time_evidence(text):
            return DelayAssessment.SIGNIFICANT.value
        if _has_explicit_no_dead_time(text) or re.search(
            r"(?:within one sample|一个采样周期内).{0,24}(?:start|begin|开始|变化)",
            text,
        ):
            return DelayAssessment.NOT_SIGNIFICANT.value
        return None
    if diagnostic_field_id == "relative_degree":
        if re.search(
            r"(?:three or more|at least three|high(?:er)? order|至少三|高阶)",
            text,
        ):
            return RelativeDegreeAssessment.HIGH.value
        if re.search(
            r"(?:one or two|no more than two|single|first[- ]order|"
            r"一到两个|不超过两个|至多两个|一个明显|一阶)",
            text,
        ) and re.search(
            r"(?:storage|integration|stage|order|time scale|"
            r"储能|积分|阶段|阶|快慢)",
            text,
        ):
            return RelativeDegreeAssessment.LOW.value
        return None
    if diagnostic_field_id == "controllability_observability":
        if re.search(
            r"(?:unreachable|unobservable|cannot be (?:excited|recorded|reconstructed)|"
            r"insufficient to reconstruct|无法(?:激发|记录|重建)|"
            r"不足以重建|不可控|不可观)",
            text,
        ):
            return ControllabilityObservabilityAssessment.INADEQUATE.value
        if re.search(
            r"(?:(?:synchron|record|sensor).{0,55}"
            r"(?:sufficient|reconstruct|all relevant motion)|"
            r"(?:sufficient|reconstruct|all relevant motion).{0,55}"
            r"(?:synchron|record|sensor)|"
            r"(?:同步|记录|传感).{0,55}(?:足以|重建所有相关运动)|"
            r"(?:输入|执行).{0,45}(?:带动|激发).{0,30}(?:输出|运动))",
            text,
        ):
            return ControllabilityObservabilityAssessment.ADEQUATE.value
        return None
    if diagnostic_field_id == "nonlinearity_strength":
        if re.search(r"(?:state-dependent|state evolves|状态相关|随状态演化)", text):
            return NonlinearityAssessment.STRONG_DYNAMIC.value
        if re.search(r"(?:hysteresis|dead zone|relay|滞回|死区|继电)", text):
            return NonlinearityAssessment.STATIC_COMPENSABLE.value
        if re.search(
            r"(?:smooth|reversible|proportional|symmetric|平滑|可逆|成比例|对称)",
            text,
        ) and re.search(r"(?:positive|negative|正向|反向|正反)", text):
            return NonlinearityAssessment.WEAK.value
        return None
    if diagnostic_field_id == "coupling_severity":
        if re.search(r"(?:underactuat|fewer independent|欠驱动|少于受控)", text):
            return CouplingAssessment.UNDERACTUATED.value
        if re.search(r"(?:inner loop|cascade|内环|串级)", text):
            return CouplingAssessment.CASCADED.value
        if re.search(
            r"(?:several|multiple|多个).{0,28}(?:outputs|readings|输出|读数)",
            text,
        ):
            return CouplingAssessment.SEVERE_MIMO.value
        if re.search(
            r"(?:one (?:main|principal).{0,25}(?:path|route|channel)|"
            r"one (?:control )?input.{0,30}one (?:measured )?output|"
            r"一条.{0,20}(?:路径|通道)|一个主要控制输入.{0,30}一个被测输出)",
            text,
        ):
            return CouplingAssessment.SISO.value
        return None
    if re.search(r"(?:material|substantial|large|大幅|明显)", text):
        return UncertaintyAssessment.LARGE.value
    if re.search(r"(?:modest|moderate|适度|中等)", text):
        return UncertaintyAssessment.MODERATE.value
    if re.search(
        r"(?:almost unchanged|nearly unchanged|small range|narrow range|"
        r"几乎不变|变化很小|小范围|窄范围)",
        text,
    ):
        return UncertaintyAssessment.SMALL.value
    return None


def infer_structural_field_from_excerpt(diagnostic_field_id: str, excerpt: str):
    """Return one typed field using only its field-specific excerpt semantics."""

    diagnosis = infer_structural_diagnosis(SystemDescription(text=excerpt))
    field = getattr(diagnosis, diagnostic_field_id)
    assessment = infer_description_field_assessment(diagnostic_field_id, excerpt)
    if assessment is None:
        return field.model_copy(
            update={
                "status": "unknown",
                "value": "field-specific excerpt was not deterministically resolved",
                "assessment": type(field.assessment)("unknown"),
                "confidence": 0.2,
                "evidence": [],
            }
        )
    updates = {
        "status": "inferred",
        "value": "field-specific deterministic excerpt inference",
        "assessment": type(field.assessment)(assessment),
        "confidence": max(field.confidence, 0.9),
        "evidence": [excerpt],
    }
    if diagnostic_field_id == "relative_degree":
        if assessment == RelativeDegreeAssessment.HIGH.value:
            updates["estimated_order"] = 4
        else:
            updates["estimated_order"] = (
                2 if _has_explicit_oscillation_evidence(excerpt.casefold()) else 1
            )
    return field.model_copy(update=updates)


def _reconcile_explicit_description(
    description: SystemDescription,
    diagnosis: StructuralDiagnosis,
) -> StructuralDiagnosis:
    """Correct structured-adapter outputs that contradict direct user statements."""

    text = description.text.lower()
    updates = {}
    direct = _direct_eight_segment_assessments(text)
    field_enums = {
        "open_loop_stability": StabilityAssessment,
        "minimum_phase": PhaseAssessment,
        "significant_delay": DelayAssessment,
        "relative_degree": RelativeDegreeAssessment,
        "controllability_observability": ControllabilityObservabilityAssessment,
        "nonlinearity_strength": NonlinearityAssessment,
        "coupling_severity": CouplingAssessment,
        "uncertainty_magnitude": UncertaintyAssessment,
    }
    for field_name, assessment in direct.items():
        field = getattr(diagnosis, field_name)
        field_update = {
            "status": "inferred",
            "value": "explicit eight-segment behavioral statement",
            "assessment": field_enums[field_name](assessment),
            "confidence": max(field.confidence, 0.95),
            "evidence": list(
                dict.fromkeys(
                    [
                        *field.evidence,
                        "direct behavioral statement in the submitted description",
                    ]
                )
            ),
        }
        if field_name == "relative_degree":
            field_update["estimated_order"] = (
                4
                if assessment == RelativeDegreeAssessment.HIGH.value
                else 2
                if _has_explicit_oscillation_evidence(text)
                else 1
            )
        updates[field_name] = field.model_copy(update=field_update)
    if _has_explicit_minimum_phase_direction(
        text
    ) and not _has_nonminimum_phase_evidence(text):
        field = diagnosis.minimum_phase
        updates["minimum_phase"] = field.model_copy(
            update={
                "status": "inferred",
                "value": "explicit initial motion follows the final direction",
                "assessment": PhaseAssessment.MINIMUM_PHASE,
                "confidence": max(field.confidence, 0.9),
                "evidence": list(
                    dict.fromkeys(
                        [*field.evidence, "explicitly no initial opposite motion"]
                    )
                ),
            }
        )
    if _has_explicit_no_dead_time(text) and not _has_significant_dead_time_evidence(
        text
    ):
        field = diagnosis.significant_delay
        updates["significant_delay"] = field.model_copy(
            update={
                "status": "inferred",
                "value": "explicitly no independent silent interval before response",
                "assessment": DelayAssessment.NOT_SIGNIFICANT,
                "confidence": max(field.confidence, 0.9),
                "evidence": list(
                    dict.fromkeys(
                        [
                            *field.evidence,
                            "response starts without independent dead time",
                        ]
                    )
                ),
            }
        )

    thermal = _contains(
        text, ["temperature", "thermal", "thermostat", "室温", "温度", "恒温器"]
    )
    upper_bound = _contains(
        text,
        ["at most two", "no more than two", "up to two", "至多两个", "至多经过两个"],
    )
    if thermal and upper_bound and not _has_explicit_oscillation_evidence(text):
        field = diagnosis.relative_degree
        updates["relative_degree"] = field.model_copy(
            update={
                "status": "inferred",
                "value": "thermal response with a stated order upper bound and no oscillation evidence",
                "assessment": RelativeDegreeAssessment.LOW,
                "estimated_order": 1,
                "confidence": max(field.confidence, 0.85),
                "evidence": list(
                    dict.fromkeys(
                        [
                            *field.evidence,
                            "order statement is an upper bound, not an oscillatory mode",
                        ]
                    )
                ),
            }
        )
    fixed_hysteresis = _contains(
        text,
        ["fixed hysteresis", "fixed hysteresis band", "固定滞环", "固定滞环带"],
    )
    if thermal and fixed_hysteresis:
        field = diagnosis.nonlinearity_strength
        updates["nonlinearity_strength"] = field.model_copy(
            update={
                "status": "inferred",
                "value": "fixed thermostat hysteresis is a static switching law",
                "assessment": NonlinearityAssessment.STATIC_COMPENSABLE,
                "confidence": max(field.confidence, 0.9),
                "evidence": list(
                    dict.fromkeys(
                        [
                            *field.evidence,
                            "fixed hysteresis does not add a dynamic state",
                        ]
                    )
                ),
            }
        )
    return diagnosis.model_copy(update=updates) if updates else diagnosis


def _question_pool(
    description: SystemDescription, diagnosis: StructuralDiagnosis
) -> list[str]:
    questions: list[str] = []
    if not description.observed_outputs:
        questions.append("Which quantities can you watch or record during motion?")
    if not description.actuators:
        questions.append("What physical action or device can change the system?")
    if diagnosis.minimum_phase.assessment == PhaseAssessment.UNKNOWN.value:
        questions.append(
            "After a small change, does the output first move the expected way or briefly the opposite way?"
        )
    if diagnosis.significant_delay.assessment == DelayAssessment.UNKNOWN.value:
        questions.append(
            "After a small change, is there a noticeable pause before anything moves?"
        )
    if diagnosis.coupling_severity.assessment == CouplingAssessment.UNKNOWN.value:
        questions.append("Does one input strongly move more than one measured output?")
    if (
        diagnosis.uncertainty_magnitude.assessment
        == UncertaintyAssessment.UNKNOWN.value
    ):
        questions.append(
            "Do load, wear, or operating conditions change the behavior noticeably?"
        )
    return questions[:4]


def _status(assessment: str) -> str:
    return "unknown" if assessment == "unknown" else "inferred"


def infer_structural_diagnosis(description: SystemDescription) -> StructuralDiagnosis:
    """Deterministic fixture adapter for tests and registered benchmark descriptions."""

    text = description.text.lower()
    pendulum = _contains(text, ["pendulum", "cart-pole", "cartpole"]) or bool(
        re.search(r"\brod\b", text)
    )
    underactuated = pendulum or _contains(
        text,
        ["acrobot", "unactuated link", "unactuated joint", "only one actuated joint"],
    )
    vtol = _contains(text, ["vtol", "vertical take", "two rotors", "hover", "aircraft"])
    oscillator = _has_explicit_oscillation_evidence(text)
    first_order = _contains(
        text,
        [
            "first-order",
            "first order",
            "temperature",
            "tank",
            "lag",
            "self-regulating",
            "settles",
            "室温",
            "温度",
            "热过程",
            "水箱",
            "液位",
            "收敛",
        ],
    )
    integrator = _contains(
        text,
        [
            "integrator",
            "drift",
            "low-friction",
            "position keeps moving",
            "持续漂移",
            "低摩擦",
            "位置继续移动",
        ],
    )
    mimo = _contains(
        text,
        [
            "mimo",
            "multi-input",
            "multiple inputs",
            "multiple outputs",
            "strongly coupled",
            "two pump inputs",
            "both controlled lower levels",
            "interconnected tank levels",
            "多输入",
            "多输出",
            "强耦合",
            "多个执行器",
        ],
    )
    mimo_dynamics = mimo and _contains(
        text,
        [
            "mimo",
            "multiple inputs",
            "strongly coupled",
            "settle",
            "response",
            "respond",
            "收敛",
            "有界",
            "首次有效",
            "及时开始",
            "响应速度",
        ],
    )
    operating_dependent = _contains(
        text,
        [
            "operating point",
            "operating points",
            "vary strongly with temperature",
            "vary strongly with conversion",
            "gain and time constant vary",
            "工作点",
            "随温度强烈变化",
            "增益和时间常数变化",
        ],
    )
    nmp = _has_nonminimum_phase_evidence(text) or underactuated or vtol
    delay_unknown = _contains(
        text,
        [
            "timing has not been observed",
            "delay is unknown",
            "unknown delay",
            "dead time is unknown",
            "时延未知",
            "尚未观察响应时机",
        ],
    )
    significant_delay = _has_significant_dead_time_evidence(text)
    direct = _direct_eight_segment_assessments(text)

    stability = (
        StabilityAssessment.UNSTABLE
        if underactuated
        or vtol
        or _contains(text, ["unstable", "falls over", "diverge", "upright"])
        else StabilityAssessment.MARGINAL
        if integrator
        else StabilityAssessment.STABLE
        if first_order
        or oscillator
        or mimo_dynamics
        or operating_dependent
        or _contains(text, ["settle", "returns", "decay", "有界", "返回", "衰减"])
        else StabilityAssessment.UNKNOWN
    )
    phase = (
        PhaseAssessment.NONMINIMUM_PHASE
        if nmp
        else PhaseAssessment.MINIMUM_PHASE
        if first_order
        or oscillator
        or integrator
        or mimo_dynamics
        or operating_dependent
        else PhaseAssessment.UNKNOWN
    )
    delay = (
        DelayAssessment.UNKNOWN
        if delay_unknown
        else DelayAssessment.SIGNIFICANT
        if significant_delay
        else DelayAssessment.NOT_SIGNIFICANT
        if underactuated
        or vtol
        or first_order
        or oscillator
        or integrator
        or mimo_dynamics
        or operating_dependent
        or _contains(text, ["starts promptly", "及时开始", "不会出现独立静默区间"])
        else DelayAssessment.UNKNOWN
    )
    degree = (
        RelativeDegreeAssessment.HIGH
        if underactuated
        or vtol
        or operating_dependent
        or _contains(
            text, ["higher order", "high relative degree", "高相对阶次", "至少经过三个"]
        )
        else RelativeDegreeAssessment.LOW
        if first_order
        or oscillator
        or integrator
        or mimo_dynamics
        or _contains(text, ["at most two", "no more than two", "至多经过两个"])
        else RelativeDegreeAssessment.UNKNOWN
    )
    co = (
        ControllabilityObservabilityAssessment.ADEQUATE
        if description.observed_outputs and description.actuators
        else ControllabilityObservabilityAssessment.UNKNOWN
    )
    nonlinear = (
        NonlinearityAssessment.STRONG_DYNAMIC
        if underactuated
        or operating_dependent
        or _contains(
            text,
            [
                "large angle",
                "limit cycle",
                "state-dependent",
                "大角度",
                "状态相关",
                "响应规律会随状态演化",
            ],
        )
        else NonlinearityAssessment.STATIC_COMPENSABLE
        if _contains(
            text,
            [
                "hysteresis",
                "dead zone",
                "deadzone",
                "backlash",
                "滞环",
                "死区",
                "回差",
                "固定输入输出规律",
            ],
        )
        else NonlinearityAssessment.WEAK
        if vtol or first_order or oscillator or integrator or mimo_dynamics
        else NonlinearityAssessment.UNKNOWN
    )
    coupling = (
        CouplingAssessment.SEVERE_MIMO
        if mimo
        else CouplingAssessment.CASCADED
        if vtol
        else CouplingAssessment.UNDERACTUATED
        if underactuated
        else CouplingAssessment.WEAK_MIMO
        if operating_dependent and len(description.actuators) > 1
        else CouplingAssessment.SISO
        if first_order
        or oscillator
        or integrator
        or _contains(text, ["one principal", "一条主要动作到记录量的通道"])
        else CouplingAssessment.UNKNOWN
    )
    uncertainty = (
        UncertaintyAssessment.LARGE
        if underactuated
        or vtol
        or operating_dependent
        or mimo_dynamics
        or _contains(
            text,
            [
                "unknown parameters",
                "payload",
                "wear",
                "varies",
                "load change",
                "明显改变",
                "大幅变化",
            ],
        )
        else UncertaintyAssessment.MODERATE
        if first_order
        or oscillator
        or integrator
        or _contains(text, ["适度改变", "modestly change"])
        else UncertaintyAssessment.UNKNOWN
    )

    stability = StabilityAssessment(direct.get("open_loop_stability", stability.value))
    phase = PhaseAssessment(direct.get("minimum_phase", phase.value))
    delay = DelayAssessment(direct.get("significant_delay", delay.value))
    degree = RelativeDegreeAssessment(direct.get("relative_degree", degree.value))
    co = ControllabilityObservabilityAssessment(
        direct.get("controllability_observability", co.value)
    )
    nonlinear = NonlinearityAssessment(
        direct.get("nonlinearity_strength", nonlinear.value)
    )
    coupling = CouplingAssessment(direct.get("coupling_severity", coupling.value))
    uncertainty = UncertaintyAssessment(
        direct.get("uncertainty_magnitude", uncertainty.value)
    )
    estimated_order = (
        4
        if degree == RelativeDegreeAssessment.HIGH
        else 2
        if oscillator or integrator
        else 1
        if degree == RelativeDegreeAssessment.LOW
        else None
    )

    def evidence(resolved: bool, message: str) -> list[str]:
        return [message] if resolved else []

    diagnosis = StructuralDiagnosis(
        open_loop_stability=StabilityField(
            status=_status(stability.value),
            value="deterministic benchmark inference",
            assessment=stability,
            confidence=0.8 if stability != StabilityAssessment.UNKNOWN else 0.2,
            evidence=evidence(
                stability != StabilityAssessment.UNKNOWN,
                "observable settling, drift, or divergence pattern",
            ),
        ),
        minimum_phase=PhaseField(
            status=_status(phase.value),
            value="deterministic benchmark inference",
            assessment=phase,
            confidence=0.75 if phase != PhaseAssessment.UNKNOWN else 0.2,
            evidence=evidence(
                phase != PhaseAssessment.UNKNOWN,
                "reported initial motion direction and actuation geometry",
            ),
        ),
        significant_delay=SignificantDelayField(
            status=_status(delay.value),
            value="deterministic benchmark inference",
            assessment=delay,
            confidence=0.72 if delay != DelayAssessment.UNKNOWN else 0.2,
            evidence=evidence(
                delay != DelayAssessment.UNKNOWN, "reported response timing"
            ),
        ),
        relative_degree=RelativeDegreeField(
            status=_status(degree.value),
            value="deterministic benchmark inference",
            assessment=degree,
            estimated_order=estimated_order,
            confidence=0.75 if degree != RelativeDegreeAssessment.UNKNOWN else 0.2,
            evidence=evidence(
                degree != RelativeDegreeAssessment.UNKNOWN,
                "input-to-output motion chain",
            ),
        ),
        controllability_observability=ControllabilityObservabilityField(
            status=_status(co.value),
            value="deterministic benchmark inference",
            assessment=co,
            confidence=0.72
            if co != ControllabilityObservabilityAssessment.UNKNOWN
            else 0.2,
            evidence=evidence(
                co != ControllabilityObservabilityAssessment.UNKNOWN,
                "declared measured outputs and actuators",
            ),
        ),
        nonlinearity_strength=NonlinearityField(
            status=_status(nonlinear.value),
            value="deterministic benchmark inference",
            assessment=nonlinear,
            confidence=0.72 if nonlinear != NonlinearityAssessment.UNKNOWN else 0.2,
            evidence=evidence(
                nonlinear != NonlinearityAssessment.UNKNOWN,
                "reported operating geometry and nonlinear effects",
            ),
        ),
        coupling_severity=CouplingField(
            status=_status(coupling.value),
            value="deterministic benchmark inference",
            assessment=coupling,
            confidence=0.75 if coupling != CouplingAssessment.UNKNOWN else 0.2,
            evidence=evidence(
                coupling != CouplingAssessment.UNKNOWN,
                "declared input-output interaction pattern",
            ),
        ),
        uncertainty_magnitude=UncertaintyField(
            status=_status(uncertainty.value),
            value="deterministic benchmark inference",
            assessment=uncertainty,
            confidence=0.7 if uncertainty != UncertaintyAssessment.UNKNOWN else 0.2,
            evidence=evidence(
                uncertainty != UncertaintyAssessment.UNKNOWN,
                "reported parameter or load variability",
            ),
        ),
        clarification_questions=["placeholder", "placeholder"],
        complete=False,
    )
    complete = all(field.status != "unknown" for field in diagnosis.fields)
    questions = [] if complete else _question_pool(description, diagnosis)
    if not complete:
        while len(questions) < 2:
            questions.append(
                "What safe motion can be observed after the smallest input change?"
            )
    return diagnosis.model_copy(
        update={"complete": complete, "clarification_questions": questions[:4]}
    )


def classify_archetype(
    diagnosis: StructuralDiagnosis,
    description: SystemDescription | None = None,
) -> ArchetypeClassification:
    """Classify order-two responses as oscillators only with oscillation evidence."""

    stability = diagnosis.open_loop_stability.assessment
    phase = diagnosis.minimum_phase.assessment
    degree = diagnosis.relative_degree.assessment
    nonlinear = diagnosis.nonlinearity_strength.assessment
    coupling = diagnosis.coupling_severity.assessment

    if coupling == CouplingAssessment.SEVERE_MIMO.value:
        return ArchetypeClassification(
            primary_class=ArchetypeClass.CLASS_V_MULTIVARIABLE_SIGNIFICANT_COUPLING,
            control_architecture="conservative decentralized MIMO control with half-strength static decoupling",
            required_core_features=[
                "local_gain_matrix",
                "local_time_constant",
                "pairing_indicator",
            ],
            safety_constraints=[
                "bound each input separately",
                "freeze on unexpected cross-channel motion",
            ],
            rationale="The normalized diagnosis reports severe multivariable coupling.",
        )
    if (
        stability == StabilityAssessment.UNSTABLE.value
        or phase == PhaseAssessment.NONMINIMUM_PHASE.value
        or degree == RelativeDegreeAssessment.HIGH.value
        or nonlinear == NonlinearityAssessment.STRONG_DYNAMIC.value
        or coupling
        in {CouplingAssessment.UNDERACTUATED.value, CouplingAssessment.CASCADED.value}
    ):
        return ArchetypeClassification(
            primary_class=ArchetypeClass.CLASS_IV_HIGHER_ORDER_UNSTABLE_NONLINEAR_OR_NMP,
            control_architecture="profile-selected cascaded or nonlinear conservative control",
            required_core_features=["natural_frequency", "input_gain"],
            safety_constraints=[
                "start from the safest simulated configuration",
                "use reversible five-percent gain increments",
                "rollback on structural or safety limits",
            ],
            rationale="At least one normalized Class IV condition is present.",
        )
    if stability == StabilityAssessment.MARGINAL.value:
        return ArchetypeClassification(
            primary_class=ArchetypeClass.CLASS_III_DOUBLE_OR_PURE_INTEGRATOR,
            control_architecture="small saturated PD controller",
            required_core_features=["input_gain"],
            safety_constraints=["hard output saturation", "short bounded pulse"],
            rationale="The normalized diagnosis reports marginal non-restoring dynamics.",
        )
    order_two_is_oscillatory = diagnosis.relative_degree.estimated_order == 2 and (
        description is None
        or _has_explicit_oscillation_evidence(description.text.lower())
    )
    if order_two_is_oscillatory:
        return ArchetypeClassification(
            primary_class=ArchetypeClass.CLASS_II_SECOND_ORDER_OSCILLATOR,
            control_architecture="low-bandwidth damping-enhancing PD controller",
            required_core_features=["natural_frequency", "damping_ratio", "input_gain"],
            safety_constraints=["free response stays in the normalized safe range"],
            rationale="A stable second-order dominant mode is diagnosed.",
        )
    features = ["static_gain", "time_constant"]
    if diagnosis.significant_delay.assessment == DelayAssessment.SIGNIFICANT.value:
        features.append("dead_time")
    return ArchetypeClassification(
        primary_class=ArchetypeClass.CLASS_I_FIRST_ORDER_LAG,
        control_architecture="detuned PI controller",
        required_core_features=features,
        safety_constraints=[
            "small normalized step",
            "stop at the configured output bound",
        ],
        rationale="The remaining normalized signature is a stable first-order dominant response.",
    )


class DiagnosticEngine:
    def __init__(
        self,
        adapter: DiagnosticAdapter | None = None,
        use_mechanism_cards: bool = False,
    ):
        self.adapter = adapter or DeterministicDiagnosticAdapter()
        self.use_mechanism_cards = use_mechanism_cards

    def diagnose(self, description: SystemDescription) -> StructuralDiagnosis:
        diagnosis = validate_agent_payload(self.adapter.diagnose(description))
        return _reconcile_explicit_description(description, diagnosis)

    def classify(
        self,
        diagnosis: StructuralDiagnosis,
        description: SystemDescription | None = None,
        use_mechanism_cards: bool | None = None,
    ) -> ArchetypeClassification:
        classification = classify_archetype(diagnosis, description)
        enabled = (
            self.use_mechanism_cards
            if use_mechanism_cards is None
            else use_mechanism_cards
        )
        if not enabled:
            return classification
        from cfdc.diagnosis.mechanism_cards import supplement_with_mechanism_cards

        return supplement_with_mechanism_cards(description, diagnosis, classification)

    def run(
        self, description: SystemDescription
    ) -> tuple[StructuralDiagnosis, ArchetypeClassification | None]:
        diagnosis = self.diagnose(description)
        return diagnosis, self.classify(
            diagnosis, description
        ) if diagnosis.complete else None
