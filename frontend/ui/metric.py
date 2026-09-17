from __future__ import annotations

import html

import streamlit as st


def metrics(items: list[dict]) -> None:
    tiles = []
    for item in items:
        label = item["label"]
        value = item["value"]
        tone = item.get("tone", "")
        delta = item.get("delta")

        tone_class = f" ag-metric--{tone}" if tone else ""
        delta_html = f'<div class="ag-metric-delta">{html.escape(str(delta))}</div>' if delta is not None else ""

        tiles.append(
            f'<div class="ag-metric{tone_class}">'
            f'<div class="ag-metric-label">{html.escape(str(label))}</div>'
            f'<div class="ag-metric-value">{html.escape(str(value))}</div>'
            f"{delta_html}"
            "</div>"
        )

    st.markdown(f'<div class="ag-metrics">{"".join(tiles)}</div>', unsafe_allow_html=True)
