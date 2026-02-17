"""
Dashboard Page — the main 3-column view matching the PDF UI mockup:

  ┌──────────────┬──────────────────────────┬──────────────────┐
  │  INPUT PANEL │  PERSONALIZED DIET PLAN  │  INSIGHTS PANEL  │
  │  (left col)  │     (center col)         │   (right col)    │
  └──────────────┴──────────────────────────┴──────────────────┘

This page only wires together the three panel components.
All rendering logic lives in app/ui/components/.
"""

import streamlit as st
from typing import Optional
from uuid import UUID

from app.db.connection import check_connection
from app.db.models import MedicalReport, ReportStatus
from app.services.report_service import (
    get_reports_for_patient,
    get_all_patients,
)
from app.controllers.report_controller import handle_report_upload
from app.ui.styles import inject_styles
from app.ui.components.sidebar import render_sidebar
from app.ui.components.upload_panel import render_upload_panel
from app.ui.components.diet_plan_panel import render_diet_plan_panel
from app.ui.components.insights_panel import render_insights_panel


# ── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Dashboard | AI-NutriCare",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_styles()
render_sidebar(active_page="Dashboard")

# ── Guard: DB must be connected ───────────────────────────────────────────────
if not check_connection():
    st.error("⚠️ Database is not connected. Configure `.env` and restart.")
    st.stop()

# ── Page Header ───────────────────────────────────────────────────────────────
st.markdown(
    """
    <div class="nutricare-header">
        <h1>🥗 AI-NUTRICARE: PERSONALIZED DIET PLAN GENERATOR</h1>
        <p>Your Health, Your Plate, Tailored by AI</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── Report Selector (above panels) ───────────────────────────────────────────
# Let the user pick which completed report drives the insights + diet plan panels.
patients = get_all_patients()
patient_name_map = {p.id: p.full_name for p in patients}

# Gather all completed reports across all patients for the selector
all_completed: list[MedicalReport] = []
for p in patients:
    all_completed.extend(
        [r for r in get_reports_for_patient(p.id) if r.status == ReportStatus.COMPLETED]
    )

selected_report: Optional[MedicalReport] = None

if all_completed:
    report_options = {
        f"{r.original_filename}  ·  {patient_name_map.get(r.patient_id, '?')}  "
        f"·  {r.created_at.strftime('%b %d') if r.created_at else ''}": r
        for r in all_completed
    }
    sel_label = st.selectbox(
        "Active Report",
        options=list(report_options.keys()),
        key="dashboard_report_selector",
        help="Select a processed report to populate the insights and diet plan panels",
    )
    selected_report = report_options[sel_label]
else:
    st.info("No processed reports yet — upload one below to populate the dashboard.")

st.divider()

# ── 3-Column Layout ───────────────────────────────────────────────────────────
col_left, col_center, col_right = st.columns([2, 3, 2], gap="medium")


# ── LEFT: Input Panel ─────────────────────────────────────────────────────────
with col_left:
    with st.container(border=True):

        def _handle_upload(patient_id: UUID, uploaded_file) -> None:
            """Callback wired to the upload panel's upload button."""
            with st.spinner("Processing report…"):
                result = handle_report_upload(
                    patient_id=patient_id,
                    file_bytes=uploaded_file.getvalue(),
                    original_filename=uploaded_file.name,
                )
            if result.success:
                st.success(
                    f"✅ Processed! Found **{result.metrics_count}** metrics "
                    f"and **{result.notes_count}** notes."
                )
                st.rerun()
            else:
                st.error(f"❌ {result.message}")

        render_upload_panel(
            on_upload=_handle_upload,
            selected_report=selected_report,
        )


# ── CENTER: Diet Plan Panel ───────────────────────────────────────────────────
with col_center:
    with st.container(border=True):
        render_diet_plan_panel(
            report=selected_report,
            diet_plan=None,   # populated in Week 7–8
        )


# ── RIGHT: Insights Panel ─────────────────────────────────────────────────────
with col_right:
    with st.container(border=True):
        render_insights_panel(report=selected_report)