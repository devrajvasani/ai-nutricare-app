"""
AI-NutriCare – Streamlit Entry Point.
Run with:  streamlit run main.py

This file is intentionally thin. All UI lives in pages/ and app/ui/components/.
"""

import streamlit as st

from app.config.settings import app_settings
from app.db.connection import check_connection, create_all_tables
from app.ui.styles import inject_styles
from app.ui.components.sidebar import render_sidebar
from app.utils.logger import logger


st.set_page_config(
    page_title="AI-NutriCare",
    page_icon="🥗",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_styles()
render_sidebar(active_page="Home")

# ── App Header ────────────────────────────────────────────────────────────────
st.markdown(
    """
    <div class="nutricare-header">
        <h1>🥗 AI-NUTRICARE</h1>
        <p>Personalized Diet Plan Generator from Medical Reports
           &nbsp;·&nbsp; Your Health, Your Plate, Tailored by AI</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── Feature Overview Cards ────────────────────────────────────────────────────
col1, col2, col3, col4 = st.columns(4)

cards = [
    ("📤", "Upload Report",  "PDF, image, or text medical reports"),
    ("🔬", "Extract Data",   "OCR + regex extracts health metrics"),
    ("📊", "View Insights",  "Visualize lab results & doctor notes"),
    ("🥦", "Diet Plan",      "Personalized plan · Week 7–8"),
]

for col, (icon, title, desc) in zip([col1, col2, col3, col4], cards):
    col.markdown(
        f"""
        <div class="panel-card" style="text-align:center;padding:20px 14px;">
            <div style="font-size:2rem;">{icon}</div>
            <div style="font-weight:600;margin:8px 0 4px;">{title}</div>
            <div style="font-size:0.8rem;color:#757575;">{desc}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.divider()
st.caption("👈 Use the sidebar to navigate between pages.")

# ── DB Init (once on startup) ─────────────────────────────────────────────────
if check_connection():
    try:
        create_all_tables()
    except Exception as exc:
        logger.debug(f"Table init skipped: {exc}")