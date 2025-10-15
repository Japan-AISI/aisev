export interface PerspectiveMapping {
  ja: string;
  en: string;
}

export const TEN_PERSPECTIVE_MAPPINGS: PerspectiveMapping[] = [
  { ja: "有害情報の出力制御", en: "Control of Toxic Output" },
  {
    ja: "偽誤情報の出力・誘導の防止",
    en: "Prevention of Misinformation, Disinformation and Manipulation",
  },
  { ja: "公平性と包摂性", en: "Fairness and Inclusion" },
  {
    ja: "ハイリスク利用・目的外利用への対処",
    en: "Addressing High-risk Use and Unintended Us",
  },
  { ja: "プライバシー保護", en: "Privacy Protection" },
  { ja: "セキュリティ確保", en: "Ensuring Security" },
  { ja: "説明可能性", en: "Explainability" },
  { ja: "ロバスト性", en: "Robustness" },
  { ja: "データ品質", en: "Data Quality" },
  { ja: "検証可能性", en: "Verifiability" },
];

export const TEN_PERSPECTIVES_JA = TEN_PERSPECTIVE_MAPPINGS.map(
  (item) => item.ja
);
export const TEN_PERSPECTIVES_EN = TEN_PERSPECTIVE_MAPPINGS.map(
  (item) => item.en
);

function findMapping(value: string | null | undefined) {
  if (!value && value !== "") return undefined;
  const normalized = String(value).trim();
  return TEN_PERSPECTIVE_MAPPINGS.find(
    (mapping) => mapping.ja === normalized || mapping.en === normalized
  );
}

export function toJapanesePerspective<T extends string | null | undefined>(
  value: T
): T {
  const mapping = findMapping(value);
  if (!mapping) return value;
  return mapping.ja as T;
}

export function toEnglishPerspective<T extends string | null | undefined>(
  value: T
): T {
  const mapping = findMapping(value);
  if (!mapping) return value;
  return mapping.en as T;
}

export function getPerspectiveListByLocale(locale: string): string[] {
  return locale.startsWith("en") ? TEN_PERSPECTIVES_EN : TEN_PERSPECTIVES_JA;
}

