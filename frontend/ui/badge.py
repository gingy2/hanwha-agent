from __future__ import annotations

import html

import streamlit as st

_OK_PREFIXES = ("현행", "완료", "승인", "유효", "정상")
_WAIT_PREFIXES = ("대기", "진행 중", "진행중", "재임베딩")
_NO_PREFIXES = ("만료", "반려", "차단", "위험", "실패")

_VALID_TONES = {"ok", "wait", "no", "accent", "neutral", "count"}


def tone_for(text: str) -> str:
    if text.startswith(_OK_PREFIXES):
        return "ok"
    if text.startswith(_WAIT_PREFIXES):
        return "wait"
    if text.startswith(_NO_PREFIXES):
        return "no"
    return "neutral"


def badge_html(text: str, tone: str | None = None) -> str:
    resolved = tone if tone in _VALID_TONES else (tone_for(text) if tone is None else "neutral")
    return f'<span class="ag-badge ag-badge--{resolved}">{html.escape(text)}</span>'


def badge(text: str, tone: str | None = None) -> None:
    st.markdown(badge_html(text, tone), unsafe_allow_html=True)


def badges(items: list[tuple[str, str | None]]) -> None:
    parts = [badge_html(text, tone) for text, tone in items]
    st.markdown(" ".join(parts), unsafe_allow_html=True)
