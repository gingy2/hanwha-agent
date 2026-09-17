from __future__ import annotations

import html
from collections.abc import Iterable, Sequence

import streamlit as st

Cell = str | int | float | None


def _cell_str(value: Cell, *, raw_html: bool) -> str:
    if value is None:
        return ""
    text = str(value)
    return text if raw_html else html.escape(text)


def table_html(
    headers: Sequence[str],
    rows: Iterable[Sequence[Cell]],
    *,
    row_classes: Sequence[str] | None = None,
    align: Sequence[str] | None = None,
    raw_html: bool = True,
) -> str:
    rows = list(rows)
    thead = "".join(f"<th>{html.escape(h)}</th>" for h in headers)

    body_rows = []
    for r_idx, row in enumerate(rows):
        row_class = row_classes[r_idx] if row_classes and r_idx < len(row_classes) else ""
        cells = []
        for c_idx, value in enumerate(row):
            col_class = align[c_idx] if align and c_idx < len(align) else ""
            cls = f' class="{col_class}"' if col_class else ""
            cells.append(f"<td{cls}>{_cell_str(value, raw_html=raw_html)}</td>")
        tr_cls = f' class="{row_class}"' if row_class else ""
        body_rows.append(f"<tr{tr_cls}>{''.join(cells)}</tr>")

    return (
        '<div class="ag-tbl-wrap"><table class="ag-tbl">'
        f"<thead><tr>{thead}</tr></thead><tbody>{''.join(body_rows)}</tbody>"
        "</table></div>"
    )


def table(
    headers: Sequence[str],
    rows: Iterable[Sequence[Cell]],
    **kwargs,
) -> None:
    st.markdown(table_html(headers, rows, **kwargs), unsafe_allow_html=True)


def kv_html(pairs: Iterable[tuple[str, Cell]], *, raw_html: bool = True) -> str:
    rows = "".join(
        f'<tr><td class="ag-kv-k">{html.escape(k)}</td>'
        f'<td class="ag-kv-v">{_cell_str(v, raw_html=raw_html)}</td></tr>'
        for k, v in pairs
    )
    return f'<table class="ag-kv"><tbody>{rows}</tbody></table>'


def kv(pairs: Iterable[tuple[str, Cell]], **kwargs) -> None:
    st.markdown(kv_html(pairs, **kwargs), unsafe_allow_html=True)
