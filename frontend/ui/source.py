from __future__ import annotations

import html

import streamlit as st

from ui.badge import badge_html


def source_html(
    *,
    title: str,
    version: str,
    locator: str,
    score: float,
    quote: str | None = None,
    extra_badge: tuple[str, str] | None = None,
    weak: bool = False,
) -> str:
    score_tone = "no" if weak else "accent"
    badges = [badge_html(version, "accent"), badge_html(f"{score:.2f}", score_tone)]
    if extra_badge is not None:
        badges.append(badge_html(extra_badge[0], extra_badge[1]))

    quote_html = ""
    if quote is not None:
        weak_style = ' style="opacity:.6"' if weak else ""
        quote_html = f'<div class="ag-note"{weak_style}>{html.escape(quote)}</div>'

    weak_class = " ag-src--no" if weak else ""

    return (
        f'<div class="ag-src{weak_class}">'
        f'<div>{html.escape(title)} {"".join(badges)}</div>'
        f'<div class="ag-src-meta">{html.escape(locator)}</div>'
        f"{quote_html}"
        "</div>"
    )


def sources(items: list[dict], *, weak: bool = False) -> None:
    for item in items:
        st.markdown(source_html(**item, weak=weak), unsafe_allow_html=True)
