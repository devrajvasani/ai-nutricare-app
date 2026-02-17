# 🥗 AI-NutriCare

**AI/ML-Based Personalized Diet Plan Generator from Medical Reports**

AI-NutriCare analyzes patient medical reports (PDF, scanned images, text), extracts structured health metrics and doctor notes, and generates personalized diet plans tailored to individual health conditions.

---

## 📁 Project Structure

```
AI-NUTRICARE-APP/
├── app/
│   ├── config/
│   │   └── settings.py          # Centralized env-based configuration
│   ├── controllers/
│   │   └── report_controller.py # UI ↔ service bridge + validation
│   ├── core/
│   │   ├── ocr_engine.py        # Tesseract / EasyOCR text extraction
│   │   ├── pdf_parser.py        # PyMuPDF / pdfplumber PDF parsing
│   │   └── data_extractor.py    # Regex-based metric + note extraction
│   ├── db/
│   │   ├── connection.py        # SQLAlchemy engine + session management
│   │   ├── models.py            # ORM models (all 8 tables)
│   │   └── migrations/
│   │       └── 001_initial_schema.sql
│   ├── prompts/
│   │   └── extraction_prompts.py  # GPT/BERT prompts (Week 5-6)
│   ├── services/
│   │   ├── extraction_service.py  # Full processing pipeline
│   │   └── report_service.py      # Patient & report CRUD
│   └── utils/
│       ├── file_utils.py          # Upload, validation, file helpers
│       ├── logger.py              # Loguru-based centralized logging
│       ├── text_utils.py          # Text cleaning & parsing helpers
│       └── validators.py          # Input validation
├── pages/
│   ├── 1_Upload_Report.py        # Upload + patient registration UI
│   ├── 2_View_Reports.py         # Report status dashboard
│   └── 3_Extracted_Data.py       # Metrics & notes viewer
├── sample_reports/
│   └── sample_report_john_doe.txt
├── uploads/                       # Uploaded files (gitignored)
├── logs/                          # Application logs (gitignored)
├── main.py                        # Streamlit entry point
├── requirements.txt
├── .env.example
└── README.md
```

---

## 🚀 Setup & Installation

### 1. Clone and create virtual environment

```bash
git clone <repo-url>
cd AI-NUTRICARE-APP
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Install Tesseract OCR (system dependency)

```bash
# Ubuntu / Debian
sudo apt-get install tesseract-ocr

# macOS
brew install tesseract

# Windows: Download installer from https://github.com/UB-Mannheim/tesseract/wiki
```

### 3. Set up PostgreSQL

```bash
# Create database
createdb nutricare_db

# Run migrations
psql -U postgres -d nutricare_db -f app/db/migrations/001_initial_schema.sql
```

### 4. Configure environment

```bash
cp .env.example .env
# Edit .env with your DB credentials and paths
```

### 5. Run the app

```bash
streamlit run main.py
```

---

## 🗃️ Database Schema

| Table | Purpose |
|---|---|
| `patients` | Patient profiles and demographics |
| `medical_reports` | Uploaded file metadata + processing status |
| `extracted_data` | Raw OCR/parsed text (1:1 with reports) |
| `health_metrics` | Structured numeric values (blood glucose, cholesterol, etc.) |
| `textual_notes` | Doctor notes, prescriptions, diagnoses |
| `allergies` | Patient food/drug allergies |
| `dietary_preferences` | Dietary preferences (vegetarian, vegan, etc.) |
| `diet_plans` | Generated diet plans (Week 7-8) |

---

## 📋 Week 1-2 Milestone Checklist

- [x] Project structure and configuration setup
- [x] PostgreSQL schema with all entities
- [x] PDF text extraction (PyMuPDF + pdfplumber fallback)
- [x] OCR for scanned images (Tesseract + EasyOCR fallback)
- [x] Structured health metric extraction (regex-based)
- [x] Doctor notes / textual section extraction
- [x] Patient registration and management
- [x] Report upload and processing pipeline
- [x] Streamlit UI: Upload, View Reports, Extracted Data
- [x] Centralized logging with loguru
- [x] Sample medical report for testing

---

## 🛠 Technology Stack

| Layer | Technology |
|---|---|
| Language | Python 3.11+ |
| Web Framework | Streamlit |
| Database | PostgreSQL + SQLAlchemy |
| PDF Parsing | PyMuPDF, pdfplumber |
| OCR | Tesseract (pytesseract), EasyOCR |
| Logging | Loguru |
| Config | python-dotenv + Pydantic |