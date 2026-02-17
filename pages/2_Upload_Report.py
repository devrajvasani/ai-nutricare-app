"""
Upload Report Page.
Handles patient registration and medical report upload.
UI logic uses shared components; business logic stays in controllers.
"""

import streamlit as st
from datetime import date

from app.db.connection import check_connection
from app.controllers.report_controller import handle_create_patient, handle_report_upload
from app.services.report_service import get_all_patients
from app.ui.styles import inject_styles
from app.ui.components.sidebar import render_sidebar
from app.utils.file_utils import get_human_readable_size


st.set_page_config(
    page_title="Upload Report | AI-NutriCare",
    page_icon="📤",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_styles()
render_sidebar(active_page="Upload_Report")

st.markdown(
    """
    <div class="nutricare-header">
        <h1>📤 Upload Medical Report</h1>
        <p>Register a patient and upload their medical report for AI-powered extraction</p>
    </div>
    """,
    unsafe_allow_html=True,
)

if not check_connection():
    st.error("⚠️ Database is not connected. Configure `.env` and restart.")
    st.stop()


# ─── Tabs ─────────────────────────────────────────────────────────────────────
tab_upload, tab_register = st.tabs(["📁  Upload Report", "👤  Register New Patient"])


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 1 — Upload Report
# ═══════════════════════════════════════════════════════════════════════════════
with tab_upload:
    patients = get_all_patients()

    if not patients:
        st.warning("No patients found. Switch to the **Register New Patient** tab first.")
    else:
        with st.container(border=True):
            # Patient selector
            patient_map = {f"{p.full_name}": p for p in patients}
            sel_name = st.selectbox("Select Patient", options=list(patient_map.keys()))
            patient = patient_map[sel_name]

            st.divider()

            # File uploader
            uploaded = st.file_uploader(
                "Choose a medical report file",
                type=["pdf", "png", "jpg", "jpeg", "tiff", "bmp", "txt"],
                help="Max 20 MB · PDF, PNG, JPG, JPEG, TIFF, BMP, TXT",
            )

            if uploaded:
                file_bytes = uploaded.getvalue()
                c1, c2, c3 = st.columns(3)
                c1.metric("📄 File",      uploaded.name)
                c2.metric("📦 Size",      get_human_readable_size(len(file_bytes)))
                c3.metric("🗂 Type",      (uploaded.type or "—").split("/")[-1].upper())

                st.divider()

                if st.button("🚀 Upload & Process", type="primary", use_container_width=True):
                    with st.spinner("Extracting data from your report…"):
                        result = handle_report_upload(
                            patient_id=patient.id,
                            file_bytes=file_bytes,
                            original_filename=uploaded.name,
                        )
                    if result.success:
                        st.success(f"✅ {result.message}")
                        col_m1, col_m2 = st.columns(2)
                        col_m1.metric("🔬 Metrics Found", result.metrics_count)
                        col_m2.metric("📝 Notes Found",   result.notes_count)
                        st.info(f"Report ID: `{result.report_id}`  — go to **View Reports** to inspect.")
                    else:
                        st.error(f"❌ {result.message}")


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 2 — Register New Patient
# ═══════════════════════════════════════════════════════════════════════════════
with tab_register:
    with st.container(border=True):
        with st.form("patient_registration_form", clear_on_submit=True):

            # ── Basic Info ────────────────────────────────────────────
            st.markdown("#### 👤 Basic Information")
            col_name, col_gender = st.columns([3, 1])
            full_name = col_name.text_input("Full Name *", placeholder="e.g. John Doe")
            gender    = col_gender.selectbox("Gender", ["", "Male", "Female", "Other"])

            col_dob, col_phone = st.columns(2)
            dob   = col_dob.date_input("Date of Birth", value=None,
                                        min_value=date(1900, 1, 1), max_value=date.today())
            phone = col_phone.text_input("Phone", placeholder="+1 234 567 8900")
            email = st.text_input("Email", placeholder="patient@example.com")

            st.divider()

            # ── Allergies ─────────────────────────────────────────────
            st.markdown("#### 🚫 Allergies *(one per line)*")
            allergies_raw = st.text_area(
                "Allergies",
                placeholder="Peanuts\nGluten\nDairy",
                height=90,
                label_visibility="collapsed",
            )

            # ── Dietary Preferences ───────────────────────────────────
            st.markdown("#### 🥗 Dietary Preferences")
            pref_options = [
                "Vegetarian", "Vegan", "Keto", "Gluten-Free",
                "Dairy-Free", "Halal", "Kosher", "Low-Sodium",
            ]
            selected_prefs = st.multiselect(
                "Preferences", options=pref_options, label_visibility="collapsed"
            )

            submitted = st.form_submit_button(
                "✅ Register Patient", type="primary", use_container_width=True
            )

        if submitted:
            allergies = [a.strip() for a in allergies_raw.splitlines() if a.strip()]
            result = handle_create_patient(
                full_name=full_name,
                date_of_birth=dob,
                gender=gender or None,
                email=email or None,
                phone=phone or None,
                allergies=allergies,
                preferences=selected_prefs,
            )
            if result.success:
                st.success(f"✅ {result.message}")
                st.info(f"Patient ID: `{result.patient_id}`")
                st.rerun()
            else:
                st.error(f"❌ {result.message}")