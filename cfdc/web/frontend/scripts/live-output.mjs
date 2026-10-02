// Shared by Playwright error handling and local auxiliary acceptance scripts.
export function redactLiveText(text, key = process.env.CFDC_LLM_API_KEY ?? "") {
  if (!key) return text;
  const variants = [
    key,
    JSON.stringify(key).slice(1, -1),
    encodeURIComponent(key),
  ];
  for (const value of variants.sort((a, b) => b.length - a.length)) {
    text = text.replaceAll(value, "[REDACTED]");
  }
  return text;
}

export function publicJSON(value) {
  const text = JSON.stringify(value, null, 2);
  if (redactLiveText(text) !== text) {
    throw new Error(
      "Acceptance artifact contained credentials; nothing was saved.",
    );
  }
  return `${text}\n`;
}
