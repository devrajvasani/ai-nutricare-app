"""
Insights Panel Component.
Renders the right "Insights Panel" from the PDF UI mockup:
  - Key health metric cards (Blood Sugar, Cholesterol, BMI, etc.)
  - Detected conditions tags
  - Doctor's Notes (Interpreted) block
  - AI interpretation badge
"""

import streamlit as st
from typing import Optional
from uuid import UUID

from app.db.models import MedicalReport, HealthMetric, TextualNote
from app.services.report_service import (
    get_health_metrics,
    get_textual_notes,
    get_reports_for_patient,
)
from app.ui.styles import METRIC_STATUS_COLORS, METRIC_STATUS_EMOJI, COLORS


# ─── Metric display config: metric_key → (icon, display_label) ───────────────
METRIC_DISPLAY = {
    "blood_glucose_fasting":      ("🩸", "Blood Sugar (Fasting)"),
    "blood_glucose_postprandial": ("🩸", "Blood Sugar (PP)"),
    "hba1c":                      ("📊", "HbA1c"),
    "total_cholesterol":          ("💛", "Total Cholesterol"),
    "ldl_cholesterol":            ("💛", "LDL Cholesterol"),
    "hdl_cholesterol":            ("💚", "HDL Cholesterol"),
    "triglycerides":              ("🫀", "Triglycerides"),
    "bmi":                        ("⚖️", "BMI"),
    "systolic_bp":                ("💉", "Blood Pressure (Sys)"),
    "diastolic_bp":               ("💉", "Blood Pressure (Dia)"),
    "hemoglobin":                 ("🔴", "Hemoglobin"),
    "tsh":                        ("🦋", "TSH"),
    "vitamin_d":                  ("☀️", "Vitamin D"),
    "vitamin_b12":                ("🔵", "Vitamin B12"),
}

# ─── Infer medical conditions from metric status ───────────────────────────────
CONDITION_INFERENCE = {
    ("hba1c",             "high"):    "Diabetes (Uncontrolled)",
    ("blood_glucose_fasting", "high"):"Hyperglycemia",
    ("total_cholesterol", "high"):    "High Cholesterol",
    ("ldl_cholesterol",   "high"):    "High LDL",
    ("hdl_cholesterol",   "low"):     "Low HDL",
    ("triglycerides",     "high"):    "Hypertriglyceridemia",
    ("bmi",               "high"):    "Overweight / Obesity",
    ("systolic_bp",       "high"):    "Hypertension",
    ("vitamin_d",         "low"):     "Vitamin D Deficiency",
    ("vitamin_b12",       "low"):     "Vitamin B12 Deficiency",
    ("hemoglobin",        "low"):     "Anemia",
    ("tsh",               "high"):    "Hypothyroidism (Possible)",
    ("tsh",               "low"):     "Hyperthyroidism (Possible)",
}


def _infer_conditions(metrics: list[HealthMetric]) -> list[str]:
    """Derive likely conditions from flagged metric statuses."""
    conditions = []
    for m in metrics:
        key = (m.metric_key, m.status.value)
        if key in CONDITION_INFERENCE:
            cond = CONDITION_INFERENCE[key]
            if cond not in conditions:
                conditions.append(cond)
    return conditions


def _metric_card(metric: HealthMetric) -> None:
    """Render one metric insight card."""
    icon, label = METRIC_DISPLAY.get(metric.metric_key, ("📋", metric.metric_name))
    status_val = metric.status.value if metric.status else "unknown"
    color = METRIC_STATUS_COLORS.get(status_val, COLORS["neutral"])
    badge_class = f"badge-{status_val}"

    value_str = f"{metric.value} {metric.unit}" if metric.value is not None else "—"

    st.markdown(
        f"""
        <div class="metric-insight">
            <div class="metric-insight-icon">{icon}</div>
            <div class="metric-insight-body">
                <div class="metric-insight-name">{label}</div>
                <div class="metric-insight-value" style="color:{color};">{value_str}</div>
            </div>
            <span class="metric-insight-badge {badge_class}">
                {status_val.capitalize()}
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_insights_panel(report: Optional[MedicalReport]) -> None:
    """
    Render the right Insights Panel.

    Args:
        report: The currently selected MedicalReport (or None if none selected).
    """
    st.markdown('<div class="panel-title">📊 INSIGHTS PANEL</div>', unsafe_allow_html=True)

    if report is None:
        st.markdown(
            '<div style="text-align:center;padding:40px 0;color:#BDBDBD;">'
            '<div style="font-size:2rem;">📋</div>'
            '<div style="font-size:0.85rem;margin-top:8px;">No report selected</div>'
            '</div>',
            unsafe_allow_html=True,
        )
        return

    metrics = get_health_metrics(report.id)
    notes = get_textual_notes(report.id)

    if not metrics and not notes:
        st.info("No extracted data yet. Process the report first.")
        return

    # ── Key Metrics (prioritize flagged ones first) ───────────────────
    # Show critical/high/low first, then normal, max 6 shown
    flagged = [m for m in metrics if m.status and m.status.value in ("critical", "high", "low")]
    normal  = [m for m in metrics if m.status and m.status.value == "normal"]
    display_metrics = (flagged + normal)[:6]

    if display_metrics:
        for metric in display_metrics:
            _metric_card(metric)

        if len(metrics) > 6:
            st.caption(f"↳ +{len(metrics) - 6} more metrics — see Extracted Data page")

    # ── Detected Conditions ───────────────────────────────────────────
    conditions = _infer_conditions(metrics)
    if conditions:
        st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
        st.markdown(
            '<div style="font-size:0.75rem;font-weight:600;color:#757575;'
            'letter-spacing:0.8px;margin-bottom:8px;">DETECTED CONDITIONS</div>',
            unsafe_allow_html=True,
        )
        tags_html = "".join(
            f'<span class="condition-tag">{c}</span>' for c in conditions
        )
        st.markdown(f'<div>{tags_html}</div>', unsafe_allow_html=True)

    # ── Doctor's Notes ────────────────────────────────────────────────
    doctor_notes = [n for n in notes if n.note_type in ("doctor_note", "prescription", "diagnosis")]
    if doctor_notes:
        st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
        st.markdown(
            '<div style="font-size:0.75rem;font-weight:600;color:#757575;'
            'letter-spacing:0.8px;margin-bottom:6px;">DOCTOR\'S NOTES (INTERPRETED)</div>',
            unsafe_allow_html=True,
        )
        # Show the first doctor note (most relevant)
        note_text = doctor_notes[0].content[:400]
        if len(doctor_notes[0].content) > 400:
            note_text += "..."

        # If AI interpretation exists, show it; otherwise show raw content
        display_text = doctor_notes[0].ai_interpretation or note_text

        st.markdown(
            f"""
            <div class="doctor-notes-box">
                {display_text}
                <div><span class="ai-badge">🤖 AI-powered interpretation · Week 5–6</span></div>
            </div>
            """,
            unsafe_allow_html=True,
        )