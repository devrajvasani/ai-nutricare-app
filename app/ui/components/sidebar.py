"""
Sidebar Component.
Renders the shared sidebar with branding, DB status, and navigation context.
Import and call render_sidebar() at the top of each page.
"""

import streamlit as st
from app.db.connection import check_connection


def render_sidebar(active_page: str = "") -> None:
    """
    Render the standard sidebar for all pages.

    Args:
        active_page: Name of the current page (for contextual hints).
    """
    with st.sidebar:
        # ── Branding ─────────────────────────────────────────────────
        st.markdown(
            """
            <div style="text-align:center; padding: 8px 0 16px;">
                <div style="font-size:2.5rem;">🥗</div>
                <div style="font-weight:700; font-size:1.15rem; color:#2E7D32;">AI-NutriCare</div>
                <div style="font-size:0.75rem; color:#757575; margin-top:2px;">
                    Personalized Nutrition from Medical Reports
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.divider()

        # ── Database Status ───────────────────────────────────────────
        db_ok = check_connection()
        if db_ok:
            st.markdown(
                '<div style="background:#E8F5E9;border-radius:8px;padding:8px 12px;'
                'font-size:0.82rem;color:#2E7D32;font-weight:500;">🟢 &nbsp;Database Connected</div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                '<div style="background:#FFEBEE;border-radius:8px;padding:8px 12px;'
                'font-size:0.82rem;color:#B71C1C;font-weight:500;">🔴 &nbsp;Database Offline</div>',
                unsafe_allow_html=True,
            )
            st.caption("Configure `.env` with PostgreSQL credentials and restart.")

        st.divider()

        # ── Navigation Guide ──────────────────────────────────────────
        nav_items = {
            "🏠 Dashboard":         ("Dashboard", "Main overview & diet plan"),
            "📤 Upload Report":     ("Upload_Report", "Add new medical report"),
            "📋 View Reports":      ("View_Reports", "Browse all uploaded reports"),
            "🔬 Extracted Data":    ("Extracted_Data", "Inspect parsed metrics & notes"),
        }

        st.caption("NAVIGATION")
        for label, (page_key, desc) in nav_items.items():
            is_active = active_page == page_key
            style = (
                "background:#E8F5E9;border-radius:6px;padding:6px 10px;"
                "font-weight:600;color:#2E7D32;"
            ) if is_active else "padding:6px 10px;color:#424242;"

            st.markdown(
                f'<div style="{style}font-size:0.85rem;">{label}</div>'
                f'<div style="font-size:0.73rem;color:#9E9E9E;padding:0 10px 4px;">{desc}</div>',
                unsafe_allow_html=True,
            )

        st.divider()

        # ── Project Progress ──────────────────────────────────────────
        st.caption("SPRINT PROGRESS")
        phases = [
            ("Week 1–2: Preprocessing", 100),
            ("Week 3–4: ML Analysis",     0),
            ("Week 5–6: NLP/AI Notes",    0),
            ("Week 7–8: Diet Generator",  0),
        ]
        for label, pct in phases:
            col_l, col_p = st.columns([6, 4])
            col_l.caption(label)
            col_p.caption(f"{pct}%")
            st.progress(pct / 100)

        st.divider()
        st.caption("AI-NutriCare · Week 1–2 Build")