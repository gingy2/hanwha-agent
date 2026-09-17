from __future__ import annotations

import html

import streamlit as st

_MARKS = {"ok": "✓", "wait": "◐", "no": "✕", "todo": "·"}


def steps_html(items: list[dict]) -> str:
    rows = []
    for item in items:
        name = item["name"]
        state = item.get("state", "todo")
        time = item.get("time")
        if time is None and state in ("no", "todo"):
            time = "—"

        mark = _MARKS.get(state, _MARKS["todo"])
        time_html = f'<div class="ag-step-time">{html.escape(time)}</div>' if time else ""

        rows.append(
            f'<div class="ag-step ag-step--{state}">'
            f'<div class="ag-step-mark">{mark}</div>'
            f'<div class="ag-step-name">{html.escape(str(name))}</div>'
            f"{time_html}"
            "</div>"
        )
    return f'<div class="ag-steps">{"".join(rows)}</div>'


def steps(items: list[dict]) -> None:
    st.markdown(steps_html(items), unsafe_allow_html=True)


def progress(pct: int) -> None:
    clamped = max(0, min(100, pct))
    st.markdown(
        f'<div class="ag-progress"><div class="ag-progress-fill" style="width:{clamped}%"></div></div>'
        f'<div class="ag-meta" style="text-align:right">{clamped}%</div>',
        unsafe_allow_html=True,
    )
