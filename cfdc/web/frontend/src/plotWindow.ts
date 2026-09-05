export type WindowRange = [number | null, number | null];
export function plotWindow(
  event: Record<string, unknown>,
  current: WindowRange,
): WindowRange | undefined {
  let next: WindowRange;
  if (event["xaxis.autorange"] === true) next = [null, null];
  else {
    const range = event["xaxis.range"];
    const start = Array.isArray(range) ? range[0] : event["xaxis.range[0]"];
    const end = Array.isArray(range) ? range[1] : event["xaxis.range[1]"];
    if (start === undefined || end === undefined) return;
    const a = Number(start),
      b = Number(end);
    if (!Number.isFinite(a) || !Number.isFinite(b) || a >= b) return;
    next = [a, b];
  }
  return next[0] === current[0] && next[1] === current[1] ? undefined : next;
}
