"""
Centralized CSS styles for the AI-NutriCare Streamlit app.
Call inject_styles() once at the top of each page.
"""

import streamlit as st


# ─── Color Palette ─────────────────────────────────────────────────────────────
COLORS = {
    "primary":     "#2E7D32",   # Deep green
    "primary_lt":  "#4CAF50",   # Medium green
    "accent":      "#00ACC1",   # Teal accent
    "danger":      "#E53935",   # Red – critical / high
    "warning":     "#FB8C00",   # Orange – elevated
    "info":        "#1E88E5",   # Blue – low
    "success":     "#43A047",   # Green – normal
    "neutral":     "#78909C",   # Grey – unknown
    "bg_card":     "#FAFAFA",
    "bg_dark":     "#1B5E20",
    "text_dark":   "#212121",
    "text_muted":  "#757575",
    "border":      "#E0E0E0",
}

METRIC_STATUS_COLORS = {
    "normal":   COLORS["success"],
    "low":      COLORS["info"],
    "high":     COLORS["warning"],
    "critical": COLORS["danger"],
    "unknown":  COLORS["neutral"],
}

METRIC_STATUS_EMOJI = {
    "normal":   "🟢",
    "low":      "🔵",
    "high":     "🟠",
    "critical": "🔴",
    "unknown":  "⚪",
}


def inject_styles() -> None:
    """Inject global CSS into the Streamlit page."""
    st.markdown(
        f"""
        <style>
        /* ── App-wide ─────────────────────────────────────────────── */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

        html, body, [class*="css"] {{
            font-family: 'Inter', sans-serif;
        }}

        /* Hide default Streamlit header/footer */
        #MainMenu {{ visibility: hidden; }}
        footer    {{ visibility: hidden; }}

        /* ── App Header ─────────────────────────────────────────── */
        .nutricare-header {{
            background: linear-gradient(135deg, {COLORS["bg_dark"]} 0%, {COLORS["primary"]} 60%, {COLORS["accent"]} 100%);
            color: white;
            padding: 28px 32px 20px;
            border-radius: 12px;
            margin-bottom: 24px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.15);
        }}
        .nutricare-header h1 {{
            margin: 0;
            font-size: 1.9rem;
            font-weight: 700;
            letter-spacing: 0.5px;
        }}
        .nutricare-header p {{
            margin: 4px 0 0;
            font-size: 0.95rem;
            opacity: 0.85;
        }}

        /* ── Panel Cards ────────────────────────────────────────── */
        .panel-card {{
            background: {COLORS["bg_card"]};
            border: 1px solid {COLORS["border"]};
            border-radius: 10px;
            padding: 18px 20px;
            height: 100%;
            box-shadow: 0 1px 4px rgba(0,0,0,0.07);
        }}
        .panel-title {{
            font-size: 0.75rem;
            font-weight: 600;
            letter-spacing: 1.2px;
            text-transform: uppercase;
            color: {COLORS["text_muted"]};
            margin-bottom: 14px;
            padding-bottom: 8px;
            border-bottom: 2px solid {COLORS["primary_lt"]};
        }}

        /* ── Metric Insight Cards ───────────────────────────────── */
        .metric-insight {{
            display: flex;
            align-items: center;
            gap: 12px;
            background: white;
            border: 1px solid {COLORS["border"]};
            border-radius: 8px;
            padding: 10px 14px;
            margin-bottom: 8px;
        }}
        .metric-insight-icon {{
            font-size: 1.4rem;
            flex-shrink: 0;
        }}
        .metric-insight-body {{
            flex: 1;
            min-width: 0;
        }}
        .metric-insight-name {{
            font-size: 0.75rem;
            color: {COLORS["text_muted"]};
            margin-bottom: 2px;
        }}
        .metric-insight-value {{
            font-size: 1.05rem;
            font-weight: 600;
            color: {COLORS["text_dark"]};
        }}
        .metric-insight-badge {{
            font-size: 0.7rem;
            font-weight: 600;
            padding: 2px 8px;
            border-radius: 20px;
            white-space: nowrap;
        }}

        /* Status badge colors */
        .badge-normal   {{ background:#E8F5E9; color:#2E7D32; }}
        .badge-low      {{ background:#E3F2FD; color:#1565C0; }}
        .badge-high     {{ background:#FFF3E0; color:#E65100; }}
        .badge-critical {{ background:#FFEBEE; color:#B71C1C; }}
        .badge-unknown  {{ background:#ECEFF1; color:#546E7A; }}

        /* ── Conditions Tags ────────────────────────────────────── */
        .condition-tag {{
            display: inline-block;
            background: #EDE7F6;
            color: #4527A0;
            border-radius: 20px;
            padding: 3px 12px;
            font-size: 0.78rem;
            font-weight: 500;
            margin: 3px 3px 3px 0;
        }}
        .allergy-tag {{
            background: #FCE4EC;
            color: #880E4F;
        }}

        /* ── Diet Plan Cards ────────────────────────────────────── */
        .meal-card {{
            background: white;
            border: 1px solid {COLORS["border"]};
            border-radius: 10px;
            padding: 14px 16px;
            margin-bottom: 10px;
            position: relative;
        }}
        .meal-card-header {{
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 8px;
        }}
        .meal-icon {{
            font-size: 1.5rem;
        }}
        .meal-label {{
            font-size: 0.7rem;
            font-weight: 600;
            letter-spacing: 1px;
            text-transform: uppercase;
            color: {COLORS["text_muted"]};
        }}
        .meal-items {{
            font-size: 0.88rem;
            color: {COLORS["text_dark"]};
            line-height: 1.6;
        }}
        .meal-coming-soon {{
            color: {COLORS["text_muted"]};
            font-style: italic;
            font-size: 0.82rem;
        }}

        /* ── Day Nav ────────────────────────────────────────────── */
        .day-nav {{
            display: flex;
            justify-content: center;
            align-items: center;
            gap: 12px;
            margin: 16px 0;
        }}
        .day-badge {{
            background: {COLORS["primary"]};
            color: white;
            padding: 6px 20px;
            border-radius: 20px;
            font-size: 0.85rem;
            font-weight: 600;
        }}

        /* ── Upload Area ────────────────────────────────────────── */
        .upload-hint {{
            text-align: center;
            padding: 20px;
            border: 2px dashed {COLORS["border"]};
            border-radius: 10px;
            color: {COLORS["text_muted"]};
            font-size: 0.85rem;
            margin-bottom: 14px;
        }}
        .upload-hint .icon {{
            font-size: 2.5rem;
            display: block;
            margin-bottom: 8px;
        }}

        /* ── Patient Info Block ─────────────────────────────────── */
        .patient-info-row {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 6px 0;
            border-bottom: 1px solid {COLORS["border"]};
            font-size: 0.83rem;
        }}
        .patient-info-row:last-child {{ border-bottom: none; }}
        .patient-info-label {{ color: {COLORS["text_muted"]}; }}
        .patient-info-value {{ font-weight: 500; color: {COLORS["text_dark"]}; }}

        /* ── Doctor Notes Block ─────────────────────────────────── */
        .doctor-notes-box {{
            background: #F3E5F5;
            border-left: 4px solid #7B1FA2;
            border-radius: 0 8px 8px 0;
            padding: 12px 14px;
            font-size: 0.83rem;
            color: #4A148C;
            line-height: 1.6;
            margin-top: 8px;
        }}
        .ai-badge {{
            display: inline-block;
            background: #7B1FA2;
            color: white;
            font-size: 0.65rem;
            padding: 2px 8px;
            border-radius: 20px;
            margin-top: 8px;
        }}

        /* ── Status Badges (report list) ────────────────────────── */
        .status-pill {{
            display: inline-block;
            padding: 3px 12px;
            border-radius: 20px;
            font-size: 0.75rem;
            font-weight: 600;
        }}
        .status-completed  {{ background:#E8F5E9; color:#2E7D32; }}
        .status-pending    {{ background:#FFF8E1; color:#F57F17; }}
        .status-processing {{ background:#E3F2FD; color:#1565C0; }}
        .status-failed     {{ background:#FFEBEE; color:#B71C1C; }}

        /* ── Divider ────────────────────────────────────────────── */
        .section-divider {{
            border: none;
            border-top: 1px solid {COLORS["border"]};
            margin: 14px 0;
        }}

        /* ── Streamlit overrides ────────────────────────────────── */
        div[data-testid="stVerticalBlock"] > div {{ gap: 0.5rem; }}
        .stButton > button {{
            border-radius: 8px;
            font-weight: 600;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )