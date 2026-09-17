from __future__ import annotations

import html

import streamlit as st


def bars(
    items: list[tuple[str, float]],
    *,
    max_value: float = 100,
    unit: str = "%",
    strong_last: bool = True,
    ticks: list[float] | None = None,
) -> None:
    if ticks is None:
        ticks = [max_value * f / 4 for f in range(5)]

    rows = []
    last_idx = len(items) - 1
    for idx, (label, value) in enumerate(items):
        pct = max(0.0, min(100.0, (value / max_value) * 100 if max_value else 0))
        strong = strong_last and idx == last_idx
        fill_style = ""
        weight = 'font-weight:700' if strong else ""
        rows.append(
            f'<div class="ag-bar-row">'
            f'<div class="ag-bar-row-label">{html.escape(str(label))}</div>'
            f'<div class="ag-bar-row-track"><div class="ag-bar-row-fill" style="width:{pct:g}%"></div></div>'
            f'<div class="ag-bar-row-value" style="{weight}">{value:g}{unit}</div>'
            "</div>"
        )

    tick_html = "".join(f'<span class="ag-bar-row-tick">{t:g}{unit}</span>' for t in ticks)
    rows.append(f'<div class="ag-bar-row"><div class="ag-bar-row-label"></div><div style="flex:1;display:flex;justify-content:space-between">{tick_html}</div><div class="ag-bar-row-value"></div></div>')

    st.markdown(f'<div class="ag-bars">{"".join(rows)}</div>', unsafe_allow_html=True)


def line(
    values: list[float],
    labels: list[str],
    *,
    y_ticks: list[float],
    last_label: str | None = None,
    height: int = 190,
) -> None:
    if not values:
        return

    width = 600
    y_max = max(y_ticks) if y_ticks else max(values)
    pad = 24
    plot_w = width - 2 * pad
    plot_h = height - 2 * pad

    n = len(values)
    step = plot_w / max(1, n - 1)
    points = []
    for i, v in enumerate(values):
        x = pad + i * step
        clipped = max(0.0, min(v, y_max))
        y = pad + plot_h - (clipped / y_max * plot_h if y_max else 0)
        points.append((x, y))

    path = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)

    # x축 라벨 7~8개로 솎기, 마지막은 항상 포함
    if n > 8:
        keep = set(range(0, n, max(1, n // 7)))
        keep.add(n - 1)
    else:
        keep = set(range(n))

    label_svg = []
    for i, lab in enumerate(labels):
        if i not in keep:
            continue
        x, _ = points[i]
        label_svg.append(f'<text x="{x:.1f}" y="{height - 4}" font-size="10" fill="var(--ag-muted)" text-anchor="middle">{html.escape(lab)}</text>')

    circle = f'<circle cx="{points[-1][0]:.1f}" cy="{points[-1][1]:.1f}" r="3" fill="#0E6E62" />'
    last_label_svg = ""
    if last_label is not None:
        lx, ly = points[-1]
        last_label_svg = f'<text x="{lx:.1f}" y="{ly - 8:.1f}" font-size="11" fill="#0E6E62" text-anchor="middle">{html.escape(last_label)}</text>'

    svg = (
        f'<svg width="100%" viewBox="0 0 {width} {height}" preserveAspectRatio="xMidYMid meet">'
        f'<polyline points="{path}" fill="none" stroke="#0E6E62" stroke-width="2" />'
        f"{circle}{last_label_svg}"
        f"{''.join(label_svg)}"
        "</svg>"
    )
    st.markdown(svg, unsafe_allow_html=True)


def timeline(items: list[str]) -> None:
    rows = []
    for idx, item in enumerate(items):
        now_class = " ag-tl-item--now" if idx == 0 else ""
        rows.append(f'<div class="ag-tl-item{now_class}">{item}</div>')
    st.markdown(f'<div class="ag-tl">{"".join(rows)}</div>', unsafe_allow_html=True)
