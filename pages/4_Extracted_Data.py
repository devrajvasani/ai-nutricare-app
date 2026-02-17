"""
Extracted Data Page.
Detailed inspector for health metrics, textual notes, and raw OCR text
from a selected processed report.
"""

import streamlit as st
import pandas as pd
from uuid import UUID

from app.db.connection import check_connection
from app.services.report_service import (
    get_report_by_id,
    get_extracted_data,
    get_health_metrics,
    get_textual_notes,
    get_all_reports,
    get_all_patients,
)
from app.ui.styles import inject_styles, METRIC_STATUS_COLORS, METRIC_STATUS_EMOJI
from app.ui.components.sidebar import render_sidebar
from app.ui.components.insights_panel import METRIC_DISPLAY


st.set_page_config(
    page_title="Extracted Data | AI-NutriCare",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_styles()
render_sidebar(active_page="Extracted_Data")

st.markdown(
    """
    <div class="nutricare-header">
        <h1>🔬 Extracted Data Viewer</h1>
        <p>Inspect health metrics and textual notes parsed from a medical report</p>
    </div>
    """,
    unsafe_allow_html=True,
)

if not check_connection():
    st.error("⚠️ Database is not connected.")
    st.stop()

# ── Report Selection ──────────────────────────────────────────────────────────
patients      = get_all_patients()
patient_map   = {p.id: p.full_name for p in patients}
all_reports   = get_all_reports()
done_reports  = [r for r in all_reports if r.status.value == "completed"]

if not done_reports:
    st.info("No completed reports yet. Upload and process a report first.")
    st.stop()

# Pre-select if navigated from View Reports
preselected_id = st.session_state.get("view_report_id", "")

report_options = {
    f"{r.original_filename}  ·  {patient_map.get(r.patient_id, '?')}"
    f"  ·  {r.created_at.strftime('%b %d, %Y') if r.created_at else ''}": str(r.id)
    for r in done_reports
}

default_idx = 0
if preselected_id in report_options.values():
    default_idx = list(report_options.values()).index(preselected_id)

sel_label   = st.selectbox("Select Report", options=list(report_options.keys()), index=default_idx)
sel_id      = UUID(report_options[sel_label])

st.divider()

# ── Load Data ─────────────────────────────────────────────────────────────────
report    = get_report_by_id(sel_id)
extracted = get_extracted_data(sel_id)
metrics   = get_health_metrics(sel_id)
notes     = get_textual_notes(sel_id)
patient_name = patient_map.get(report.patient_id, "Unknown") if report else "—"

# ── Summary Row ───────────────────────────────────────────────────────────────
c1, c2, c3, c4 = st.columns(4)
c1.metric("👤 Patient",     patient_name)
c2.metric("📄 File",        report.original_filename if report else "—")
c3.metric("🔬 Metrics",     len(metrics))
c4.metric("📝 Notes",       len(notes))

if extracted:
    st.caption(
        f"OCR Engine: **{extracted.ocr_engine.value if extracted.ocr_engine else '—'}**  ·  "
        f"Confidence: **{extracted.ocr_confidence:.1f}%**  ·  "
        f"Words: **{extracted.word_count:,}**"
        if extracted.ocr_confidence else
        f"OCR Engine: **{extracted.ocr_engine.value if extracted.ocr_engine else '—'}**  ·  "
        f"Words: **{extracted.word_count:,}**"
    )

st.divider()

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab_metrics, tab_notes, tab_raw = st.tabs([
    "🩺  Health Metrics",
    "📝  Textual Notes",
    "📄  Raw Text",
])


# ════════════════════════════════════════════════════════════════════════════
# TAB 1 — Health Metrics
# ════════════════════════════════════════════════════════════════════════════
with tab_metrics:
    if not metrics:
        st.info("No health metrics were extracted from this report.")
    else:
        # ── Flagged values row ────────────────────────────────────────
        abnormal = [m for m in metrics if m.status and m.status.value in ("critical", "high", "low")]
        if abnormal:
            st.subheader("⚠️ Flagged Values")
            cols = st.columns(min(len(abnormal), 3))
            for i, m in enumerate(abnormal):
                sv    = m.status.value
                color = METRIC_STATUS_COLORS.get(sv, "#78909C")
                emoji = METRIC_STATUS_EMOJI.get(sv, "⚪")
                _, label = METRIC_DISPLAY.get(m.metric_key, ("📋", m.metric_name))
                with cols[i % 3]:
                    st.markdown(
                        f"""
                        <div class="panel-card" style="border-left:4px solid {color};">
                            <div style="font-size:0.78rem;color:#757575;">{label}</div>
                            <div style="font-size:1.4rem;font-weight:700;color:{color};">
                                {m.value} {m.unit}
                            </div>
                            <div style="font-size:0.72rem;margin-top:4px;">
                                {emoji} {sv.capitalize()} &nbsp;·&nbsp;
                                Normal: {m.reference_min}–{m.reference_max} {m.unit}
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
            st.divider()

        # ── Full table ────────────────────────────────────────────────
        st.subheader("📊 All Extracted Metrics")
        rows = []
        for m in metrics:
            sv    = m.status.value if m.status else "unknown"
            emoji = METRIC_STATUS_EMOJI.get(sv, "⚪")
            rows.append({
                "Metric":       m.metric_name,
                "Value":        m.value,
                "Unit":         m.unit,
                "Normal Min":   m.reference_min,
                "Normal Max":   m.reference_max,
                "Status":       f"{emoji} {sv.capitalize()}",
                "Confidence":   f"{m.confidence * 100:.0f}%" if m.confidence else "—",
            })
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

        # ── Bar chart ─────────────────────────────────────────────────
        if len(metrics) > 1:
            st.subheader("📈 Values Overview")
            chart_df = pd.DataFrame({
                "Metric": [m.metric_name for m in metrics],
                "Value":  [m.value for m in metrics],
            }).set_index("Metric")
            st.bar_chart(chart_df)


# ════════════════════════════════════════════════════════════════════════════
# TAB 2 — Textual Notes
# ════════════════════════════════════════════════════════════════════════════
with tab_notes:
    if not notes:
        st.info("No textual notes were extracted from this report.")
    else:
        TYPE_EMOJI = {
            "doctor_note":  "👨‍⚕️",
            "prescription": "💊",
            "diagnosis":    "🏥",
            "general":      "📋",
        }
        for note in notes:
            nt      = note.note_type or "general"
            emoji   = TYPE_EMOJI.get(nt, "📋")
            heading = note.section_heading or nt.replace("_", " ").title()

            with st.expander(f"{emoji}  {heading}", expanded=True):
                st.text(note.content)
                if note.ai_interpretation:
                    st.divider()
                    st.markdown("**🤖 AI Interpretation** *(NLP — Week 5–6)*")
                    st.markdown(
                        f'<div class="doctor-notes-box">{note.ai_interpretation}'
                        '<div><span class="ai-badge">AI-powered · GPT/BERT</span></div></div>',
                        unsafe_allow_html=True,
                    )


# ════════════════════════════════════════════════════════════════════════════
# TAB 3 — Raw Text
# ════════════════════════════════════════════════════════════════════════════
with tab_raw:
    if not extracted or not extracted.raw_text:
        st.info("No raw text available for this report.")
    else:
        st.subheader("Raw OCR / Parsed Text")
        st.caption(
            f"Words: **{extracted.word_count:,}**  ·  "
            f"Pages: **{len(extracted.page_texts) if extracted.page_texts else 1}**"
        )

        if extracted.page_texts and len(extracted.page_texts) > 1:
            sel_page = st.selectbox("Page", sorted(extracted.page_texts.keys()))
            content  = extracted.page_texts.get(sel_page, "")
        else:
            content  = extracted.raw_text

        st.text_area(
            "text",
            value=content,
            height=480,
            disabled=True,
            label_visibility="collapsed",
        )