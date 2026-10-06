import {
  createContext,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";
import frontendEn from "../../../resources/locales/en/frontend.json";
import frontendZh from "../../../resources/locales/zh-CN/frontend.json";
import webEn from "../../../resources/locales/en/web.json";
import webZh from "../../../resources/locales/zh-CN/web.json";
import presentationEn from "../../../resources/locales/en/presentation.json";
import presentationZh from "../../../resources/locales/zh-CN/presentation.json";
import doctorEn from "../../../resources/locales/en/doctor.json";
import doctorZh from "../../../resources/locales/zh-CN/doctor.json";

export type Locale = "en" | "zh-CN";
export type MessageKey =
  | keyof typeof frontendEn
  | keyof typeof webEn
  | keyof typeof presentationEn
  | keyof typeof doctorEn;
export type MessageParams = Record<string, unknown>;
export type MessageRef = { key: string; params?: MessageParams | null };
export type Translator = (key: MessageKey, params?: MessageParams) => string;
const catalogs: Record<Locale, Record<string, string>> = {
  en: { ...frontendEn, ...webEn, ...presentationEn, ...doctorEn },
  "zh-CN": { ...frontendZh, ...webZh, ...presentationZh, ...doctorZh },
};
export function resolveLocale(
  saved: string | null,
  languages: readonly string[],
): Locale {
  if (saved === "en" || saved === "zh-CN") return saved;
  return /^zh(?:-|$)/i.test(languages[0] ?? "") ? "zh-CN" : "en";
}
function initialBrowserLocale(): Locale {
  let saved: string | null = null;
  try {
    saved = localStorage.getItem("cfdc:locale");
  } catch {
    /* Storage may be unavailable. */
  }
  return resolveLocale(
    saved,
    navigator.languages?.length ? navigator.languages : [navigator.language],
  );
}
export function translateMessage(
  locale: Locale,
  ref: MessageRef | null | undefined,
  fallback = "",
): string {
  const template = ref && catalogs[locale][ref.key];
  if (!ref || typeof template !== "string") return fallback;
  return template.replace(
    /\{([A-Za-z_][A-Za-z0-9_]*)\}/g,
    (match, name: string) => {
      const value = ref.params?.[name];
      if (value === undefined || value === null) return match;
      if (typeof value === "object" && "key" in value)
        return translateMessage(
          locale,
          value as MessageRef,
          String((value as MessageRef).key),
        );
      return String(value);
    },
  );
}
export const createTranslator =
  (locale: Locale): Translator =>
  (key, params) =>
    translateMessage(locale, { key, params }, key);
export class LocalizedError extends Error {
  constructor(
    public message_ref: MessageRef,
    fallback?: string,
  ) {
    super(fallback ?? translateMessage("zh-CN", message_ref, message_ref.key));
  }
}
function localeHelpers(locale: Locale) {
  return {
    t: createTranslator(locale),
    message: (ref: MessageRef | null | undefined, fallback = "") =>
      translateMessage(locale, ref, fallback),
    errorText: (error: unknown): string => {
      if (error && typeof error === "object") {
        const value = error as {
          detail?: { message_ref?: MessageRef; message?: string };
          message_ref?: MessageRef;
          message?: string;
        };
        return translateMessage(
          locale,
          value.detail?.message_ref ?? value.message_ref,
          value.detail?.message ?? String(error),
        );
      }
      return String(error);
    },
  };
}
const I18nContext = createContext({
  locale: "zh-CN" as Locale,
  setLocale: (() => {}) as (locale: Locale) => void,
  ...localeHelpers("zh-CN"),
});
export function I18nProvider({
  children,
  initialLocale,
}: {
  children: ReactNode;
  initialLocale?: Locale;
}) {
  const [locale, setLocale] = useState<Locale>(
    () => initialLocale ?? initialBrowserLocale(),
  );
  useEffect(() => {
    document.documentElement.lang = locale;
    document.title = `CFDC · ${createTranslator(locale)("frontend.app.brand")}`;
    try {
      localStorage.setItem("cfdc:locale", locale);
    } catch {
      /* In-memory switching still works. */
    }
  }, [locale]);
  const value = useMemo(
    () => ({ locale, setLocale, ...localeHelpers(locale) }),
    [locale],
  );
  return <I18nContext.Provider value={value}>{children}</I18nContext.Provider>;
}
export const useI18n = () => useContext(I18nContext);

// Retain mounted views only across a language change for the exact same data.
// A new revision, operation, signal, or time window must get its own evidence.
export function keepLocaleData(locale: Locale, key: readonly unknown[]) {
  const localeIndex = key[0] === "task" ? 2 : 1;
  const identity = (value: readonly unknown[]) =>
    JSON.stringify(value.filter((_, index) => index !== localeIndex));
  return <T,>(
    previous: T | undefined,
    query?: { queryKey: readonly unknown[] },
  ) =>
    query &&
    query.queryKey[localeIndex] !== locale &&
    identity(query.queryKey) === identity(key)
      ? previous
      : undefined;
}
