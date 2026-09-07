"""Guidance projected from the current Kernel step; never execution authority."""

from pathlib import Path


def upload_requirements(report):
    external = report.get("external_workflow") or {}
    active = external.get("active_request") or {}
    if active:
        request = active.get("execution_request") or {}
        manifest = active.get("manifest") or {}
        trials = manifest.get("trials") or request.get("trials") or []
        task = report.get("task") or {}
        units = {
            **(task.get("signal_units") or {}),
            **{
                name: task.get("input_units") or "按任务约定"
                for name in request.get("control_inputs", [])
            },
        }
        columns = [{"name": "trajectory.time_s", "unit": "s"}]
        for field, names in (
            ("outputs", request.get("tracked_signals", [])),
            ("measurements", request.get("measured_signals", [])),
            ("references", request.get("tracked_signals", [])),
            ("control_inputs", request.get("control_inputs", [])),
            ("raw_control_inputs", request.get("control_inputs", [])),
        ):
            columns.extend(
                {
                    "name": f"trajectory.{field}.{name}",
                    "unit": str(units.get(name, "按任务约定")),
                }
                for name in names
            )
        columns.extend(
            {"name": name, "unit": ""}
            for name in (
                "trajectory.controller_states",
                "trajectory.phase_ids",
                "events",
                "stop_event",
            )
        )
        return {
            "expected_format": "一个评价结果 ZIP，根目录包含原始 manifest.json 和下列逐试次 JSON（不是待执行包）",
            "stage": active.get("stage"),
            "file_count": len(trials),
            "repeats": len(trials),
            "files": [
                {
                    "filename": "manifest.json",
                    "columns": [{"name": "保持待执行包中的绑定字段原样", "unit": ""}],
                },
                *[
                    {"filename": row.get("file", ""), "columns": columns}
                    for row in trials
                ],
            ],
        }

    handoffs = report.get("operator_handoffs") or []
    if not handoffs:
        return None
    card = handoffs[-1]
    units = card.get("units") or {}
    names = [
        "session_id",
        "protocol_fingerprint",
        "repeat",
        "time_s",
        *card.get("control_inputs", []),
        *card.get("requested_signals", []),
    ]
    columns = [
        {
            "name": name,
            "unit": (
                "s"
                if name == "time_s"
                else str(
                    (units.get("outputs") or {}).get(name)
                    or (
                        units.get("input", "")
                        if name in card.get("control_inputs", [])
                        else ""
                    )
                )
            ),
        }
        for name in names
    ]
    return {
        "expected_format": "完整重复试验 CSV / JSON",
        "stage": "identification",
        "file_count": card.get("repeats", 0),
        "repeats": card.get("repeats", 0),
        "files": [
            {"filename": Path(path).name, "columns": columns}
            for path in card.get("template_paths", [])
        ],
    }


def workflow_guide(report):
    if report.get("registered_case_binding"):
        return None
    action = (report.get("input_contract") or {}).get("action", "")
    status = report.get("status", "")
    if report.get("managed_execution"):
        title, purpose, actor, next_step, rows = (
            "从历史记录重新建立任务",
            "旧自动实验记录仅供查看，不能继续自动运行或转用为新证据。",
            "用户",
            "重新确认任务边界与外部数据来源",
            [
                ("保留原记录", "原任务、已保存文件和审查回执继续可查看和下载。"),
                ("派生新任务", "只携带任务与人工诊断信息；重新确认后按通用流程采集。"),
            ],
        )
    elif status in {"performance_met", "capability_gap", "cancelled"}:
        title, purpose, actor, next_step, rows = (
            "查看结果与过程记录",
            "依据已接受的数据、独立判定与重放查看结论。",
            "用户",
            "导出记录，或建立新的任务",
            [
                ("查看结果", "在结果与曲线中查看达标情况、失败原因及能力缺口。"),
                ("下载记录", "可导出完整公开包；下载不会改变任务结论。"),
            ],
        )
    elif action in {"answer", "submit_answer", "revise_diagnostic"}:
        title, purpose, actor, next_step, rows = (
            "描述实际观察到的现象",
            "用观察到的输入输出变化帮助确定可执行的采集协议。",
            "用户填写，系统解析与校验",
            "选择数据来源并生成采集协议",
            [
                (
                    "回答当前问题",
                    "结合页面中的具体诊断问题，用自然语言描述现象；不确定的内容写“不知道”。",
                ),
                (
                    "提交诊断",
                    "系统保存原文并检查诊断依据；若需补充，页面会显示下一个具体问题。",
                ),
            ],
        )
    elif action in {"select_external_source", "set_provider"}:
        title, purpose, actor, next_step, rows = (
            "确认外部数据来源",
            "为自定义任务绑定辨识和评价的数据来源。",
            "用户确认，系统编译协议",
            "下载采集包并核对检查清单",
            [
                ("选择来源", "选择软件实验或实际测量，与实际数据的来源保持一致。"),
                (
                    "确认来源",
                    "系统生成当前任务的协议、检查说明和记录模板；不会选择设备模型或执行外部实验。",
                ),
            ],
        )
    elif action in {
        "compile_protocol",
        "prepare_operator_handoff",
        "record_operator_report",
        "ingest_upload",
        "evidence",
    }:
        title, purpose, actor, next_step, rows = (
            "按协议采集并上传证据",
            "采集足够的原始输入输出记录，用于特征提取和控制器资格审查。",
            "用户在外部采集，系统审查上传",
            "系统提取特征、合成控制器并进行资格审查",
            [
                (
                    "下载采集包",
                    "下载当前任务的采集协议、操作说明和 CSV/JSON 模板；核对通道、单位、采样周期、重复次数及停止条件。",
                ),
                (
                    "逐项确认检查",
                    "在自己的软件实验环境或实际实验环境完成检查后，按真实情况提交检查清单。",
                ),
                (
                    "在外部执行采集",
                    "按协议规定的输入序列和重复次数实验，保存所有原始记录；不得修改任务和协议绑定。",
                ),
                (
                    "上传采集结果",
                    "回到本页选择填写完成的 CSV/JSON；查看文件要求和审查回执。只有接受的证据才会推进，下载不表示实验已完成。",
                ),
            ],
        )
    elif action in {"freeze", "freeze_controller"}:
        title, purpose, actor, next_step, rows = (
            "确认并冻结评价条件",
            "固定控制器、工作区域、性能要求和试次预算。",
            "用户确认",
            "生成并下载开发评价待执行包",
            [
                (
                    "核对方案",
                    "查看自动生成的特征、控制器与资格审查结果，不需要手写中间 JSON。",
                ),
                (
                    "确认冻结",
                    "核对参考值、边界、性能指标和重复次数后确认；后续上传不得改变冻结条件。",
                ),
            ],
        )
    elif action in {"run_tuning", "run_feedback_iteration", "start_external_tuning"}:
        title, purpose, actor, next_step, rows = (
            "确认有界调优预算",
            "初评不足时，按固定候选顺序在既有预算内尝试改善。",
            "用户确认，系统生成候选",
            "下载当前候选待执行包并在外部实验",
            [
                ("查看预算", "核对候选上限、每轮重复次数、最低改善要求和结束条件。"),
                (
                    "确认调优",
                    "每轮都按页面要求下载候选包、在外部执行并上传结果；选优后还需独立的全新确认数据。",
                ),
            ],
        )
    elif action in {
        "prepare_external_run",
        "submit_external_results",
        "evaluation",
        "confirmation",
        "run_evaluation",
        "run_confirmation",
    }:
        pending = (report.get("pending_actions") or [{}])[0]
        stage = (
            ((report.get("external_workflow") or {}).get("active_request") or {}).get(
                "stage"
            )
            or pending.get("stage")
            or (
                "fresh_confirmation"
                if pending.get("action") == "record_fresh_confirmation"
                or action in {"confirmation", "run_confirmation"}
                else "development"
            )
        )
        label = {
            "development": "开发评价",
            "tuning_probe": "候选调优",
            "fresh_confirmation": "全新确认",
        }.get(stage, "闭环评价")
        title, purpose, actor, next_step, rows = (
            f"完成{label}实验",
            "使用冻结的控制器与固定试次安排收集完整闭环轨迹。",
            "用户在外部执行，系统判定与重放",
            "查看结论，或按页面进入下一候选与全新确认",
            [
                (
                    "下载待执行实验包",
                    "包内含控制器、执行配置、固定试次清单、说明和结果模板。将其交给能够执行该控制任务的外部实验环境。",
                ),
                (
                    "按试次执行",
                    "逐试次记录输出、参考、实际与原始控制输入、控制器状态、阶段和事件；达到停止条件时如实记录。",
                ),
                (
                    "上传执行后的结果",
                    "将原始 manifest.json 与本轮全部逐试次 JSON 打包为结果 ZIP 上传；不能上传待执行包或仅填写达标标记。",
                ),
                (
                    "查看审查结果",
                    "系统校验绑定与轨迹，独立判定后从保存数据重放；拒绝时按回执说明准备新的文件，原记录保持不变。",
                ),
            ],
        )
    else:
        title, purpose, actor, next_step, rows = (
            "完成当前任务步骤",
            "按当前 Kernel 状态处理任务。",
            "用户按页面提示操作，系统校验",
            "以完成后页面显示的当前步骤为准",
            [
                (
                    "核对当前步骤",
                    "查看任务边界、当前要求及缺失信息；使用当前步骤的主按钮继续。",
                )
            ],
        )
    return {
        "title": title,
        "purpose": purpose,
        "actor": actor,
        "next_step": next_step,
        "steps": [
            {"title": title, "description": description} for title, description in rows
        ],
    }
