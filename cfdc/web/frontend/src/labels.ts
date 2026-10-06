import { createTranslator, type Translator } from "./i18n";
export const statusLabel = (
  status: string,
  tr: Translator = createTranslator("zh-CN"),
) => {
  const labels: Record<string, string> = {
    queued: tr("frontend.labels.queued"),
    running: tr("frontend.labels.running"),
    completed: tr("frontend.labels.completed"),
    failed: tr("frontend.context.failed"),
    interrupted: tr("frontend.labels.interrupted"),
    intake: tr("frontend.labels.intake"),
    diagnostic: tr("frontend.labels.diagnostic"),
    awaiting_evidence: tr("frontend.labels.awaiting_evidence"),
    protocol_ready: tr("frontend.labels.protocol_ready"),
    awaiting_operator_report: tr("frontend.labels.awaiting_operator"),
    awaiting_provider: tr("frontend.labels.awaiting_provider"),
    route_ready: tr("frontend.labels.route_ready"),
    controller_pending: tr("frontend.labels.controller_pending"),
    controller_candidate_ready: tr("frontend.labels.candidate_ready"),
    controller_qualified: tr("frontend.labels.qualified"),
    controller_ready: tr("frontend.labels.controller_ready"),
    evaluation_recorded_pending_replay: tr("frontend.labels.evaluation_replay"),
    tuning_eligible: tr("frontend.labels.tuning_eligible"),
    awaiting_confirmation: tr("frontend.labels.awaiting_confirmation"),
    performance_met: tr("frontend.labels.performance_met"),
    capability_gap: tr("frontend.labels.capability_gap"),
    cancelled: tr("frontend.labels.cancelled"),
    known: tr("frontend.labels.known"),
    unknown: tr("frontend.labels.unknown"),
    needs_clarification: tr("frontend.workspace.clarification"),
    ok: tr("frontend.labels.ok"),
    warning: tr("frontend.labels.warning"),
    error: tr("frontend.context.failed"),
  };
  return labels[status] ?? status;
};
