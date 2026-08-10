"""Channel-complete output-bound validation for linked tuning."""

from __future__ import annotations

from cfdc.lab import SimulationSession


def output_bound_gap(session: SimulationSession) -> str | None:
    """Describe any output channel that cannot be checked against a bound."""

    config = session.run_config
    if config is None or not config.output_bounds:
        return "缺少软件仿真输出边界，请返回测量阶段补充每个输出通道的数值上下限。"
    expected_channels = set(config.reference)
    expected_channels.update(
        name
        for trial in session.trials
        for trace in trial.traces
        for channels in (trace.reference, trace.outputs)
        for name in channels
    )
    missing = sorted(expected_channels - set(config.output_bounds))
    if missing:
        return (
            "以下输出通道缺少软件仿真边界："
            + "、".join(missing)
            + "。请返回测量阶段补充每个输出通道的数值上下限。"
        )
    return None


__all__ = ["output_bound_gap"]
