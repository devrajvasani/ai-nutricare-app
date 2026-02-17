"""
Upload Panel Component.
Renders the left "Input Panel" from the PDF UI mockup:
  - File upload widget
  - Extracted patient info display
  - "Generate Diet Plan" action button
"""

import streamlit as st
from typing import Optional, Callable
from uuid import UUID

from app.db.models import MedicalReport, Patient
from app.services.report_service import get_all_patients
from app.ui.styles import COLORS


def render_upload_panel(
    on_upload: Optional[Callable] = None,
    selected_report: Optional[MedicalReport] = None,
    selected_patient: Optional[Patient] = None,
) -> dict:
    """
    Render the left Input Panel.

    Returns a dict with keys:
        uploaded_file, patient_id, trigger_generate
    """
    result = {
        "uploaded_file": None,
        "patient_id": None,
        "trigger_generate": False,
    }

    st.markdown('<div class="panel-title">📥 INPUT PANEL</div>', unsafe_allow_html=True)

    # ── Patient Selector ──────────────────────────────────────────────
    patients = get_all_patients()

    if not patients:
        st.warning("No patients registered yet.")
        st.page_link("pages/2_Upload_Report.py", label="→ Register a patient first", icon="👤")
        return result

    patient_map = {f"{p.full_name}": p for p in patients}
    selected_name = st.selectbox(
        "Patient",
        options=list(patient_map.keys()),
        label_visibility="collapsed",
        key="upload_panel_patient",
    )
    patient = patient_map[selected_name]
    result["patient_id"] = patient.id

    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

    # ── File Uploader ─────────────────────────────────────────────────
    st.markdown(
        """
        <div class="upload-hint">
            <span class="icon">☁️</span>
            Upload Medical Report
        </div>
        """,
        unsafe_allow_html=True,
    )

    uploaded = st.file_uploader(
        "Choose file",
        type=["pdf", "png", "jpg", "jpeg", "tiff", "bmp", "txt"],
        label_visibility="collapsed",
        key="upload_panel_file",
        help="PDF, image (PNG/JPG/TIFF), or plain text · Max 20 MB",
    )
    result["uploaded_file"] = uploaded

    if uploaded:
        from app.utils.file_utils import get_human_readable_size
        size_str = get_human_readable_size(len(uploaded.getvalue()))
        st.caption(f"📄 `{uploaded.name}`  ·  {size_str}")

        if st.button(
            "🚀 Upload & Process",
            type="primary",
            use_container_width=True,
            key="btn_upload_process",
        ):
            if on_upload:
                on_upload(patient.id, uploaded)

    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

    # ── Extracted Patient Info ────────────────────────────────────────
    st.markdown(
        '<div style="font-size:0.78rem;font-weight:600;color:#757575;'
        'letter-spacing:0.8px;margin-bottom:10px;">PATIENT INFORMATION</div>',
        unsafe_allow_html=True,
    )

    dob_str = (
        patient.date_of_birth.strftime("%d/%m/%Y")
        if patient.date_of_birth else "—"
    )
    gender_str = patient.gender or "—"
    email_str = patient.email or "—"

    rows = [
        ("Name",   patient.full_name),
        ("DOB",    dob_str),
        ("Gender", gender_str),
        ("Email",  email_str),
    ]
    for label, value in rows:
        st.markdown(
            f"""
            <div class="patient-info-row">
                <span class="patient-info-label">{label}</span>
                <span class="patient-info-value">{value}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

    # ── Generate Diet Plan CTA ────────────────────────────────────────
    if selected_report:
        if st.button(
            "🥦 GENERATE DIET PLAN",
            type="primary",
            use_container_width=True,
            key="btn_generate_plan",
            help="AI diet plan generation is available in Week 7–8",
        ):
            result["trigger_generate"] = True
    else:
        st.button(
            "🥦 GENERATE DIET PLAN",
            use_container_width=True,
            disabled=True,
            help="Upload and process a report first",
            key="btn_generate_plan_disabled",
        )
        st.caption("Upload a report above to enable.")

    return result