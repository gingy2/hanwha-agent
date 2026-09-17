from __future__ import annotations

import html
import re
from collections.abc import Iterable
from contextlib import contextmanager

import streamlit as st

from ui.badge import badge_html

_BOLD_RE = re.compile(r"\*\*(.+?)\*\*")


def inline_md(text: str) -> str:
    escaped = html.escape(text)
    escaped = _BOLD_RE.sub(r"<b>\1</b>", escaped)
    return escaped.replace("\n", "<br>")


def card_html(body: str, *, label: str | None = None, title: str | None = None) -> str:
    parts = []
    if label is not None:
        parts.append(f'<div class="ag-card-label">{html.escape(label)}</div>')
    if title is not None:
        parts.append(f'<div class="ag-card-title">{html.escape(title)}</div>')
    parts.append(body)
    return f'<div class="ag-card">{"".join(parts)}</div>'


def card(body: str, *, label: str | None = None, title: str | None = None) -> None:
    st.markdown(card_html(body, label=label, title=title), unsafe_allow_html=True)


@contextmanager
def bordered(label: str | None = None):
    container = st.container(border=True)
    with container:
        if label is not None:
            st.markdown(f'<div class="ag-card-label">{html.escape(label)}</div>', unsafe_allow_html=True)
        yield container


def note(text: str, tone: str = "", *, markdown: bool = False) -> None:
    content = inline_md(text) if markdown else text
    tone_class = f" ag-note--{tone}" if tone else ""
    st.markdown(f'<div class="ag-note{tone_class}">{content}</div>', unsafe_allow_html=True)


def message_block(text: str) -> None:
    st.markdown(f'<div class="ag-msg">{html.escape(text)}</div>', unsafe_allow_html=True)


def log_block(lines: list[str]) -> None:
    joined = "\n".join(lines)
    st.markdown(f'<div class="ag-log">{html.escape(joined)}</div>', unsafe_allow_html=True)


def meta_footer(text: str) -> None:
    st.markdown(f'<div class="ag-meta">{html.escape(text)}</div>', unsafe_allow_html=True)


def page_header(
    title: str,
    *,
    crumb: str | None = None,
    subtitle: str | None = None,
    badges: Iterable[tuple[str, str | None]] | None = None,
) -> None:
    parts = []
    if crumb is not None:
        parts.append(f'<div class="ag-crumb">{html.escape(crumb)}</div>')

    head_parts = [f'<span class="ag-head">{html.escape(title)}</span>']
    if badges is not None:
        for text, tone in badges:
            head_parts.append(" " + badge_html(text, tone))
    parts.append("".join(head_parts))

    if subtitle is not None:
        parts.append(f'<div class="ag-sub">{html.escape(subtitle)}</div>')

    st.markdown("".join(parts), unsafe_allow_html=True)
