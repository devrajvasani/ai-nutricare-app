"""
View Reports Page.
Lists all uploaded reports with status, filters, and navigation to extracted data.
Rendering delegated to the report_table component.
"""

import streamlit as st
from uuid import UUID

from app.db.connection import check_connection
from app.services.report_service import get_all_reports, get_all_patients
from app.ui.styles import inject_styles
from app.ui.components.sidebar import render_sidebar
from app.ui.components.report_table import render_report_row, render_report_summary_metrics


st.set_page_config(
    page_title="View Reports | AI-NutriCare",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_styles()
render_sidebar(active_page="View_Reports")

st.markdown(
    """
    <div class="nutricare-header">
        <h1>📋 Medical Reports</h1>
        <p>Browse all uploaded reports and their extraction status</p>
    </div>
    """,
    unsafe_allow_html=True,
)

if not check_connection():
    st.error("⚠️ Database is not connected.")
    st.stop()

# ── Filters ───────────────────────────────────────────────────────────────────
patients = get_all_patients()
patient_name_map = {p.id: p.full_name for p in patients}

col_f1, col_f2, col_refresh = st.columns([3, 2, 1])

with col_f1:
    patient_options = {"All Patients": None}
    patient_options.update({p.full_name: p.id for p in patients})
    sel_patient_label = st.selectbox("Patient", options=list(patient_options.keys()))
    filter_patient_id = patient_options[sel_patient_label]

with col_f2:
    filter_status = st.selectbox("Status", ["All", "completed", "pending", "processing", "failed"])

with col_refresh:
    st.write("")
    if st.button("🔄 Refresh", use_container_width=True):
        st.rerun()

st.divider()

# ── Fetch & Filter ────────────────────────────────────────────────────────────
all_reports = get_all_reports()

if filter_patient_id:
    all_reports = [r for r in all_reports if r.patient_id == filter_patient_id]
if filter_status != "All":
    all_reports = [r for r in all_reports if r.status.value == filter_status]

# ── Summary Metrics ───────────────────────────────────────────────────────────
render_report_summary_metrics(all_reports)
st.divider()

# ── Report Rows ───────────────────────────────────────────────────────────────
if not all_reports:
    st.info("No reports found. Upload one from the **Upload Report** page.")
else:

    def _go_to_extracted(report_id: UUID) -> None:
        st.session_state["view_report_id"] = str(report_id)
        st.switch_page("pages/4_Extracted_Data.py")

    for report in all_reports:
        name = patient_name_map.get(report.patient_id, "Unknown")
        render_report_row(report, patient_name=name, on_view=_go_to_extracted)