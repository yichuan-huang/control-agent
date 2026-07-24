"""Minimal presentation model for the linked controller-tuning flow."""

from __future__ import annotations

from typing import Any

import pandas as pd

from cfdc.lab import SimulationSession, extract_tunable_parameters


def _empty_line_frame() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "time_s": pd.Series(dtype="float64"),
            "value": pd.Series(dtype="float64"),
            "series": pd.Series(dtype="str"),
        }
    )


def _latest_traces(session: SimulationSession):
    return session.trials[-1].traces if session.trials else []


def output_plot_frame(session: SimulationSession) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for scenario_index, trace in enumerate(_latest_traces(session), start=1):
        scenario = f"scenario-{scenario_index}"
        for group, channels in (
            ("reference", trace.reference),
            ("output", trace.outputs),
        ):
            for name, values in channels.items():
                rows.extend(
                    {
                        "time_s": time_s,
                        "value": value,
                        "series": f"{scenario} · {group} · {name}",
                    }
                    for time_s, value in zip(trace.time_s, values)
                )
    return pd.DataFrame(rows) if rows else _empty_line_frame()


def control_plot_frame(session: SimulationSession) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for scenario_index, trace in enumerate(_latest_traces(session), start=1):
        scenario = f"scenario-{scenario_index}"
        for group, channels in (
            ("requested", trace.requested_controls),
            ("applied", trace.applied_controls),
        ):
            for name, values in channels.items():
                rows.extend(
                    {
                        "time_s": time_s,
                        "value": value,
                        "series": f"{scenario} · {group} · {name}",
                    }
                    for time_s, value in zip(trace.time_s, values)
                )
    return pd.DataFrame(rows) if rows else _empty_line_frame()


def iteration_rows(session: SimulationSession) -> list[list[Any]]:
    return [
        [
            trial.iteration,
            trial.creation_source,
            trial.stability.status,
            f"{trial.stability_score:.6f}",
            f"{100 * trial.stability.saturation_fraction:.2f}%",
            "是" if trial.hard_violation else "否",
            "是" if trial.rolled_back else "否",
            trial.proposal.proposal_id if trial.proposal else "",
        ]
        for trial in session.trials
    ]


def empty_linked_tuning_view(reason: str) -> dict[str, Any]:
    """Render a locked inline region without inventing a session."""

    return {
        "available": False,
        "status": f"### 尚未进入控制器调试\n\n{reason}",
        "plant_id": "",
        "architecture": "",
        "parameter_rows": [],
        "derived_parameters": "",
        "output_frame": _empty_line_frame(),
        "control_frame": _empty_line_frame(),
        "stability_rows": [],
        "proposal_diff": [],
        "proposal_rationale": "",
        "iterations": [],
        "llm_audit": [],
        "controls": {
            "run_trial": False,
            "request_gain": False,
            "approve_and_run": False,
            "reject_gain": False,
            "restore_initial": False,
        },
    }


def _status_markdown(session: SimulationSession) -> str:
    if session.state == "trial_pending" and not session.trials:
        headline = "第五步控制器已载入，可直接运行第 1 轮"
    elif session.state == "trial_pending":
        headline = "下一轮参数已批准，可运行"
    elif session.state == "stable":
        headline = "当前软件模型首次满足稳定判据，调参已停止"
    elif session.state == "needs_adjustment":
        headline = "本轮尚未稳定，可请求 AI 建议下一组参数"
    elif session.state == "rolled_back":
        headline = "触发硬边界，已回滚；可从安全参数请求下一轮建议"
    else:
        headline = f"控制器调试状态：{session.state}"
    status = (
        f"### {headline}\n\n"
        f"对象：`{session.source_plant_id}`；"
        f"已完成 {len(session.trials)}/20 轮。\n\n"
        "**结论只针对当前软件模型，不代表真实对象或硬件安全。**"
    )
    latest_call = session.llm_calls[-1] if session.llm_calls else None
    if (
        latest_call is not None
        and latest_call.operation == "gain_proposal"
        and latest_call.validation_status in {"rejected", "error"}
        and session.pending_proposal is None
    ):
        status += (
            "\n\n**最近一次 AI 参数建议未通过后端校验，未生成可审批参数。**"
            " 请重新请求；系统不会接受参数不变、越界或改变控制器结构的建议。"
        )
    return status


def _stability_rows(session: SimulationSession) -> list[list[Any]]:
    if not session.trials:
        return []
    decision = session.trials[-1].stability
    dominant_value = (
        max((value.real for value in decision.poles), default=None)
        if decision.analysis_domain == "continuous"
        else decision.spectral_radius
    )
    return [
        ["判定", decision.status],
        [
            "最大极点实部"
            if decision.analysis_domain == "continuous"
            else "谱半径",
            dominant_value,
        ],
        ["末段误差收缩", decision.tail_error_envelope_contraction],
        ["饱和比例", decision.saturation_fraction],
        ["硬边界失败", decision.hard_failure],
    ]


def render_linked_tuning(session: SimulationSession) -> dict[str, Any]:
    """Render only controls and evidence used by the linear tuning journey."""

    parameters = (
        extract_tunable_parameters(
            session.trial_controller,
            session.tuning_profile,
        )
        if session.trial_controller is not None
        and session.tuning_profile is not None
        else {}
    )
    derived = ""
    if (
        session.trial_controller is not None
        and session.trial_controller.kind in {"pi", "filtered_pid"}
        and session.trial_controller.ki != 0.0
    ):
        integral_time = (
            session.trial_controller.kp / session.trial_controller.ki
        )
        derived = f"只读派生参数：`integral_time = {integral_time:.9g} s`"

    pending = session.pending_proposal
    proposal_diff = (
        [
            [
                name,
                pending.old_parameters[name],
                pending.new_parameters[name],
                pending.relative_change[name],
            ]
            for name in pending.whitelist
        ]
        if pending is not None
        else []
    )
    pending_llm = bool(
        pending
        and pending.source == "llm"
        and pending.approval_state == "pending"
    )
    terminal = session.state in {
        "stable",
        "frozen",
        "inconclusive",
        "budget_exhausted",
        "cancelled",
    }
    return {
        "available": True,
        "status": _status_markdown(session),
        "plant_id": session.source_plant_id or "",
        "architecture": session.source_controller_architecture or "",
        "parameter_rows": [[name, value] for name, value in parameters.items()],
        "derived_parameters": derived,
        "output_frame": output_plot_frame(session),
        "control_frame": control_plot_frame(session),
        "stability_rows": _stability_rows(session),
        "proposal_diff": proposal_diff,
        "proposal_rationale": pending.rationale if pending else "",
        "iterations": iteration_rows(session),
        "llm_audit": [
            record.model_dump(mode="json") for record in session.llm_calls
        ],
        "controls": {
            "run_trial": session.state == "trial_pending" and not terminal,
            "request_gain": (
                session.state in {"needs_adjustment", "rolled_back"}
                and not pending_llm
            ),
            "approve_and_run": pending_llm,
            "reject_gain": pending_llm,
            "restore_initial": session.state
            in {"trial_pending", "needs_adjustment", "rolled_back"}
            and bool(session.trials),
        },
    }


__all__ = [
    "empty_linked_tuning_view",
    "render_linked_tuning",
]
