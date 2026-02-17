"""
Report Table Component.
Reusable report listing with status badges, filters, and action buttons.
Used by both the View Reports page and the Dashboard.
"""

import streamlit as st
from typing import Optional, Callable
from uuid import UUID

from app.db.models import MedicalReport, ReportStatus, Patient
from app.services.report_service import get_all_patients
from app.utils.file_utils import get_human_readable_size


FILE_TYPE_ICON = {
    "pdf":   "📄",
    "image": "🖼️",
    "text":  "📝",
}

STATUS_ICON = {
    "completed":  "✅",
    "pending":    "⏳",
    "processing": "🔄",
    "failed":     "❌",
}


def render_report_row(
    report: MedicalReport,
    patient_name: str,
    on_view: Optional[Callable[[UUID], None]] = None,
    expanded: bool = False,
) -> None:
    """
    Render one report as a collapsible expander row.

    Args:
        report:       The MedicalReport ORM object.
        patient_name: Display name of the patient.
        on_view:      Callback called with report.id when "View Data" is clicked.
        expanded:     Whether the row starts expanded.
    """
    status_val = report.status.value if report.status else "unknown"
    file_type  = report.file_type.value if report.file_type else "pdf"
    icon       = FILE_TYPE_ICON.get(file_type, "📄")
    status_ico = STATUS_ICON.get(status_val, "❓")

    date_str = (
        report.created_at.strftime("%b %d, %Y  %H:%M")
        if report.created_at else "—"
    )

    title = (
        f"{icon} {report.original_filename}"
        f"   ·   👤 {patient_name}"
        f"   ·   {status_ico} {status_val.capitalize()}"
        f"   ·   {date_str}"
    )

    with st.expander(title, expanded=expanded):
        col_a, col_b, col_c, col_d = st.columns(4)

        col_a.markdown(
            f'<span class="status-pill status-{status_val}">'
            f'{status_ico} {status_val.capitalize()}</span>',
            unsafe_allow_html=True,
        )
        col_b.write(f"**Type:** {file_type.upper()}")
        col_c.write(
            f"**Size:** {get_human_readable_size(report.file_size_bytes)}"
            if report.file_size_bytes else "**Size:** —"
        )
        col_d.write(
            f"**Duration:** {report.processing_duration_ms} ms"
            if report.processing_duration_ms else "**Duration:** —"
        )

        if report.page_count:
            st.write(f"**Pages:** {report.page_count}")

        if report.error_message:
            st.error(f"**Error:** {report.error_message}")

        st.caption(f"ID: `{report.id}`")

        if status_val == "completed" and on_view:
            if st.button("🔍 View Extracted Data", key=f"view_{report.id}"):
                on_view(report.id)


def render_report_summary_metrics(reports: list[MedicalReport]) -> None:
    """Render 4 summary metric boxes above a report list."""
    total     = len(reports)
    completed = sum(1 for r in reports if r.status == ReportStatus.COMPLETED)
    pending   = sum(1 for r in reports if r.status == ReportStatus.PENDING)
    failed    = sum(1 for r in reports if r.status == ReportStatus.FAILED)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("📄 Total",     total)
    c2.metric("✅ Completed", completed)
    c3.metric("⏳ Pending",   pending)
    c4.metric("❌ Failed",    failed)