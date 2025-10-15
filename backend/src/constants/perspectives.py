"""Utility definitions for the 10 evaluation perspectives."""

from typing import Iterable


TEN_PERSPECTIVES = [
    {"ja": "有害情報の出力制御", "en": "Control of Toxic Output"},
    {
        "ja": "偽誤情報の出力・誘導の防止",
        "en": "Prevention of Misinformation, Disinformation and Manipulation",
    },
    {"ja": "公平性と包摂性", "en": "Fairness and Inclusion"},
    {"ja": "ハイリスク利用・目的外利用への対処", "en": "Addressing High-risk Use and Unintended Us"},
    {"ja": "プライバシー保護", "en": "Privacy Protection"},
    {"ja": "セキュリティ確保", "en": "Ensuring Security"},
    {"ja": "説明可能性", "en": "Explainability"},
    {"ja": "ロバスト性", "en": "Robustness"},
    {"ja": "データ品質", "en": "Data Quality"},
    {"ja": "検証可能性", "en": "Verifiability"},
]

TEN_PERSPECTIVES_JA: list[str] = [item["ja"] for item in TEN_PERSPECTIVES]
TEN_PERSPECTIVES_EN: list[str] = [item["en"] for item in TEN_PERSPECTIVES]

PERSPECTIVE_JA_TO_EN: dict[str, str] = {
    item["ja"]: item["en"] for item in TEN_PERSPECTIVES
}
PERSPECTIVE_EN_TO_JA: dict[str, str] = {
    item["en"]: item["ja"] for item in TEN_PERSPECTIVES
}


def _find_mapping(value: str | None) -> dict[str, str] | None:
    if value is None:
        return None
    normalized = value.strip()
    for mapping in TEN_PERSPECTIVES:
        if normalized in (mapping["ja"], mapping["en"]):
            return mapping
    return None


def to_japanese_perspective(value: str | None) -> str | None:
    """Return the Japanese perspective label for the given value if known."""

    mapping = _find_mapping(value)
    if mapping:
        return mapping["ja"]
    return value


def to_english_perspective(value: str | None) -> str | None:
    """Return the English perspective label for the given value if known."""

    mapping = _find_mapping(value)
    if mapping:
        return mapping["en"]
    return value


def normalize_perspective_sequence(
    values: Iterable[str | None], target_language: str
) -> list[str | None]:
    """Normalize an iterable of perspective labels into the requested language."""

    normalized: list[str | None] = []
    for value in values:
        if target_language.lower().startswith("en"):
            normalized.append(to_english_perspective(value))
        else:
            normalized.append(to_japanese_perspective(value))
    return normalized

