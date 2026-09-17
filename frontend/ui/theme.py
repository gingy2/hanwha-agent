from __future__ import annotations

import pathlib
from functools import lru_cache

import streamlit as st

_ASSETS = pathlib.Path(__file__).parent.parent / "assets"


@lru_cache
def load_css() -> str:
    parts = []
    for name in ("tokens.css", "base.css", "components.css"):
        path = _ASSETS / name
        if path.exists():
            parts.append(path.read_text(encoding="utf-8"))
    return "\n".join(parts)


def inject_css() -> None:
    css = load_css()
    if css:
        st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
