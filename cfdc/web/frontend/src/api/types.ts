import type { components } from "./schema";
export type Obj = Record<string, unknown>;
export type Credentials = Required<components["schemas"]["Credentials"]>;
export type Operation = components["schemas"]["Operation"];
export type Summary = components["schemas"]["TaskSummary"];
export type CaseCard = components["schemas"]["CaseCard"];
export type CaseDetail = components["schemas"]["CaseDetail"];
export type Config = components["schemas"]["ConfigResponse"];
export type Evaluations = components["schemas"]["EvaluationsView"];
export type Curve = components["schemas"]["CurveView"];
export type NodePage = components["schemas"]["NodePage"];

export type DTO<K extends keyof components["schemas"]> =
  components["schemas"][K];
