"""A local Streamlit v2 component: no CDN or signature service."""

from pathlib import Path

import streamlit as st

ASSETS = Path(__file__).parent / "static"

signature_pad = st.components.v2.component(
    "signature_pad",
    html=(ASSETS / "signature_pad.html").read_text(encoding="utf-8"),
    css=(ASSETS / "signature_pad.css").read_text(encoding="utf-8"),
    js=(ASSETS / "signature_pad.js").read_text(encoding="utf-8"),
)
