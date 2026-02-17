"""
Data Extractor Module.
Parses raw extracted text to identify structured health metrics and textual notes.

Uses regex pattern matching tuned for common medical report formats.
This is the rules-based extraction layer (Week 1-2).
ML-based classification is added in Week 3-4.
"""

import re
from dataclasses import dataclass, field
from typing import Optional

from app.utils.logger import logger
from app.utils.text_utils import (
    clean_text,
    extract_numeric_value,
    normalize_unit,
    split_into_sections,
    truncate,
)


# ─── Data Classes ─────────────────────────────────────────────────────────────
@dataclass
class ExtractedMetric:
    """A single parsed numeric health metric."""
    metric_name: str
    metric_key: str
    value: Optional[float]
    unit: str
    reference_min: Optional[float]
    reference_max: Optional[float]
    status: str                     # normal | low | high | critical | unknown
    raw_text_snippet: str
    confidence: float               # 0.0 – 1.0


@dataclass
class ExtractedNote:
    """A textual block (doctor note, prescription, diagnosis)."""
    note_type: str                  # doctor_note | prescription | diagnosis | general
    content: str
    section_heading: str = ""


@dataclass
class ExtractionResult:
    """Complete result from data extraction on one report's text."""
    metrics: list[ExtractedMetric] = field(default_factory=list)
    notes: list[ExtractedNote] = field(default_factory=list)
    sections_found: list[str] = field(default_factory=list)


# ─── Metric Reference Ranges ──────────────────────────────────────────────────
# Normal reference ranges for common lab values.
# Format: metric_key -> (min, max, unit)
REFERENCE_RANGES: dict[str, tuple[float, float, str]] = {
    "blood_glucose_fasting":    (70.0,   100.0,  "mg/dL"),
    "blood_glucose_postprandial":(70.0,  140.0,  "mg/dL"),
    "hba1c":                    (4.0,    5.7,    "%"),
    "total_cholesterol":        (0.0,    200.0,  "mg/dL"),
    "ldl_cholesterol":          (0.0,    100.0,  "mg/dL"),
    "hdl_cholesterol":          (40.0,   60.0,   "mg/dL"),
    "triglycerides":            (0.0,    150.0,  "mg/dL"),
    "bmi":                      (18.5,   24.9,   "kg/m²"),
    "systolic_bp":              (90.0,   120.0,  "mmHg"),
    "diastolic_bp":             (60.0,   80.0,   "mmHg"),
    "hemoglobin":               (12.0,   17.5,   "g/dL"),
    "creatinine":               (0.6,    1.2,    "mg/dL"),
    "uric_acid":                (2.4,    7.0,    "mg/dL"),
    "tsh":                      (0.4,    4.0,    "mIU/L"),
    "vitamin_d":                (20.0,   50.0,   "ng/mL"),
    "vitamin_b12":              (200.0,  900.0,  "pg/mL"),
}


# ─── Metric Patterns ──────────────────────────────────────────────────────────
# Each entry: (metric_key, display_name, regex_pattern)
METRIC_PATTERNS: list[tuple[str, str, str]] = [
    ("blood_glucose_fasting",
     "Blood Glucose (Fasting)",
     r"(?:fasting\s+)?(?:blood\s+)?(?:glucose|sugar|FBS|FPG)\s*[:\-]?\s*([\d.]+)\s*(mg/d[Ll]|mmol/L)?"),

    ("blood_glucose_postprandial",
     "Blood Glucose (Post-Prandial)",
     r"(?:post.?prandial|PP|2hr\s+PP|random)\s+(?:blood\s+)?(?:glucose|sugar|BS)\s*[:\-]?\s*([\d.]+)\s*(mg/d[Ll]|mmol/L)?"),

    ("hba1c",
     "HbA1c",
     r"(?:HbA1c|Hemoglobin\s+A1c|A1C)\s*[:\-]?\s*([\d.]+)\s*(%)?"),

    ("total_cholesterol",
     "Total Cholesterol",
     r"(?:total\s+)?cholesterol\s*[:\-]?\s*([\d.]+)\s*(mg/d[Ll])?"),

    ("ldl_cholesterol",
     "LDL Cholesterol",
     r"LDL(?:\s*cholesterol)?\s*[:\-]?\s*([\d.]+)\s*(mg/d[Ll])?"),

    ("hdl_cholesterol",
     "HDL Cholesterol",
     r"HDL(?:\s*cholesterol)?\s*[:\-]?\s*([\d.]+)\s*(mg/d[Ll])?"),

    ("triglycerides",
     "Triglycerides",
     r"triglycerides?\s*[:\-]?\s*([\d.]+)\s*(mg/d[Ll])?"),

    ("bmi",
     "BMI",
     r"BMI\s*[:\-]?\s*([\d.]+)\s*(kg/m[²2])?"),

    ("systolic_bp",
     "Systolic Blood Pressure",
     r"(?:blood\s+pressure|BP)\s*[:\-]?\s*([\d.]+)\s*/\s*[\d.]+\s*(mmHg)?"),

    ("diastolic_bp",
     "Diastolic Blood Pressure",
     r"(?:blood\s+pressure|BP)\s*[:\-]?\s*[\d.]+\s*/\s*([\d.]+)\s*(mmHg)?"),

    ("hemoglobin",
     "Hemoglobin",
     r"(?:hemoglobin|Hb|Hgb)\s*[:\-]?\s*([\d.]+)\s*(g/d[Ll])?"),

    ("creatinine",
     "Creatinine",
     r"creatinine\s*[:\-]?\s*([\d.]+)\s*(mg/d[Ll])?"),

    ("uric_acid",
     "Uric Acid",
     r"uric\s+acid\s*[:\-]?\s*([\d.]+)\s*(mg/d[Ll])?"),

    ("tsh",
     "TSH",
     r"TSH(?:\s*\(.*?\))?\s*[:\-]?\s*([\d.]+)\s*(mIU/L|μIU/mL)?"),

    ("vitamin_d",
     "Vitamin D",
     r"(?:vitamin\s+D|25-OH\s+Vitamin\s+D|25-hydroxyvitamin\s+D)\s*[:\-]?\s*([\d.]+)\s*(ng/mL|nmol/L)?"),

    ("vitamin_b12",
     "Vitamin B12",
     r"(?:vitamin\s+B12?|cobalamin|cyanocobalamin)\s*[:\-]?\s*([\d.]+)\s*(pg/mL|pmol/L)?"),
]


# ─── Note Section Keywords ────────────────────────────────────────────────────
DOCTOR_NOTE_KEYWORDS = [
    "doctor", "physician", "dr.", "notes", "recommendation", "impression",
    "finding", "diagnosis", "advised", "prescription", "medication", "rx",
    "treatment", "follow-up", "prognosis",
]


# ─── Metric Extraction ────────────────────────────────────────────────────────
def _compute_status(
    value: float,
    ref_min: Optional[float],
    ref_max: Optional[float],
) -> str:
    """Classify a value against its reference range."""
    if ref_min is None or ref_max is None:
        return "unknown"
    if value < ref_min * 0.8:
        return "critical"
    if value < ref_min:
        return "low"
    if value > ref_max * 1.5:
        return "critical"
    if value > ref_max:
        return "high"
    return "normal"


def extract_metrics(text: str) -> list[ExtractedMetric]:
    """
    Scan the extracted text for known health metric patterns.
    Returns a deduplicated list of ExtractedMetric objects.
    """
    metrics: list[ExtractedMetric] = []
    seen_keys: set[str] = set()
    text_lower = text.lower()

    for metric_key, metric_name, pattern in METRIC_PATTERNS:
        if metric_key in seen_keys:
            continue

        try:
            matches = list(re.finditer(pattern, text, re.IGNORECASE))
        except re.error as exc:
            logger.warning(f"Regex error for {metric_key}: {exc}")
            continue

        for match in matches:
            raw_snippet = truncate(match.group(0), 120)
            raw_value_str = match.group(1) if match.lastindex and match.lastindex >= 1 else ""
            value = extract_numeric_value(raw_value_str)

            if value is None:
                continue

            # Unit: use captured group 2 if available, else use reference default
            ref = REFERENCE_RANGES.get(metric_key)
            captured_unit = ""
            if match.lastindex and match.lastindex >= 2:
                captured_unit = (match.group(2) or "").strip()
            unit = normalize_unit(captured_unit) if captured_unit else (ref[2] if ref else "")

            ref_min = ref[0] if ref else None
            ref_max = ref[1] if ref else None
            status = _compute_status(value, ref_min, ref_max)

            metrics.append(
                ExtractedMetric(
                    metric_name=metric_name,
                    metric_key=metric_key,
                    value=value,
                    unit=unit,
                    reference_min=ref_min,
                    reference_max=ref_max,
                    status=status,
                    raw_text_snippet=raw_snippet,
                    confidence=0.85,  # Rule-based confidence; updated by ML in Week 3-4
                )
            )
            seen_keys.add(metric_key)
            break  # Take only first match per metric

    logger.info(f"Extracted {len(metrics)} health metrics from text.")
    return metrics


# ─── Note Extraction ──────────────────────────────────────────────────────────
def _classify_note_type(section_heading: str, content: str) -> str:
    """Heuristically classify the type of a textual note."""
    combined = (section_heading + " " + content).lower()
    if any(kw in combined for kw in ["rx", "prescription", "medication", "tablet", "capsule"]):
        return "prescription"
    if any(kw in combined for kw in ["diagnosis", "diagnosed", "condition"]):
        return "diagnosis"
    if any(kw in combined for kw in ["doctor", "physician", "dr.", "advised", "recommendation"]):
        return "doctor_note"
    return "general"


def extract_textual_notes(text: str) -> list[ExtractedNote]:
    """
    Extract meaningful textual blocks from the report.
    Sections with doctor notes, diagnoses, or prescriptions are returned.
    """
    sections = split_into_sections(text)
    notes: list[ExtractedNote] = []

    # Note-relevant section headings
    note_section_keys = {
        "DOCTOR_NOTES", "RECOMMENDATIONS", "DIAGNOSIS", "MEDICATIONS",
        "PRESCRIPTIONS", "IMPRESSIONS", "FINDINGS", "SUMMARY", "CONCLUSION", "GENERAL"
    }

    for heading, content in sections.items():
        if not content or len(content.strip()) < 20:
            continue

        # Include section if it matches known note sections OR contains keywords
        heading_match = any(key in heading.upper() for key in note_section_keys)
        content_match = any(kw in content.lower() for kw in DOCTOR_NOTE_KEYWORDS)

        if heading_match or content_match:
            note_type = _classify_note_type(heading, content)
            notes.append(
                ExtractedNote(
                    note_type=note_type,
                    content=clean_text(content),
                    section_heading=heading.replace("_", " ").title(),
                )
            )

    logger.info(f"Extracted {len(notes)} textual notes from text.")
    return notes


# ─── Main Entry Point ─────────────────────────────────────────────────────────
def extract_data_from_text(raw_text: str) -> ExtractionResult:
    """
    Orchestrate full data extraction from raw report text.

    Args:
        raw_text: The cleaned text extracted via OCR or PDF parser.

    Returns:
        ExtractionResult containing metrics and notes.
    """
    if not raw_text or not raw_text.strip():
        logger.warning("extract_data_from_text received empty text.")
        return ExtractionResult()

    sections = split_into_sections(raw_text)
    metrics = extract_metrics(raw_text)
    notes = extract_textual_notes(raw_text)

    return ExtractionResult(
        metrics=metrics,
        notes=notes,
        sections_found=list(sections.keys()),
    )