# 📊 Data Quality Checker

A modern, full-stack web application built with **Flask** and **Pandas** that automatically analyzes uploaded CSV or Excel datasets for data quality issues.

---

## ✨ Features

| Feature | Description |
|---|---|
| 📂 File Upload | Supports CSV, XLSX, and XLS files (up to 16 MB) |
| 🕳 Missing Values | Detects and quantifies null/missing cells per column |
| 🔁 Duplicates | Counts identical duplicate rows |
| 🔠 Data Types | Shows detected data type for every column |
| 📈 Statistics | Mean, median, std dev, min, max for numeric columns |
| 🎯 Outliers | IQR-based outlier detection |
| ⚠ Warnings | Auto-generated warnings for problematic columns |
| 💯 Quality Score | Overall dataset quality score (0–100) |
| ⬇ Download | Export report as **PDF** or **CSV** |
| 📊 Charts | Interactive Chart.js visualizations |

---

## 🗂 Project Structure

```
Data_quality_checker/
├── run.py                          # Entry point — run the app
├── config.py                       # Configuration (upload folder, debug, etc.)
├── requirements.txt                # Python dependencies
├── sample_data.csv                 # Example dataset with quality issues
├── uploads/                        # Temporary upload storage (auto-created)
└── app/
    ├── __init__.py                 # Flask app factory
    ├── routes.py                   # Blueprint: all URL routes
    ├── services/
    │   ├── __init__.py
    │   ├── file_handler.py         # File upload, parsing (CSV/Excel)
    │   ├── analyzer.py             # Core quality analysis engine
    │   └── report_generator.py    # CSV & PDF report generation
    ├── templates/
    │   ├── base.html               # Base template (navbar, footer)
    │   ├── index.html              # Upload page
    │   └── report.html             # Results dashboard
    └── static/
        ├── css/style.css           # Main stylesheet (dark theme)
        └── js/
            ├── main.js             # Upload UX (drag-and-drop, validation)
            └── charts.js           # Chart.js chart rendering
```

---

## 🚀 Quick Start

### 1. Clone / Navigate to the project

```bash
cd Data_missing_checker
```

### 2. Create a virtual environment

```bash
python3 -m venv venv
source venv/bin/activate        # Linux/macOS
# OR
venv\Scripts\activate           # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the application

```bash
python run.py
```

### 5. Open in browser

Visit: **http://127.0.0.1:5000**

---

## 📦 Dependencies

| Package | Purpose |
|---|---|
| `Flask` | Web framework |
| `pandas` | Data loading and analysis |
| `numpy` | Numeric computations |
| `openpyxl` | Reading `.xlsx` Excel files |
| `reportlab` | PDF report generation |
| `Werkzeug` | Secure file upload utilities |

---

## 🧪 Testing with Sample Data

A sample dataset (`sample_data.csv`) is included with **intentional quality issues**:

- ✗ **Missing values** — several rows have empty `age`, `email`, `city`, `salary` fields
- ✗ **Duplicate rows** — rows 1–2 are duplicated as rows 21–22
- ✗ **Invalid email format** — one row has `invalid-email` instead of a valid address

Upload this file to see the full report in action.

---

## 🔗 Routes

| Method | URL | Description |
|---|---|---|
| `GET` | `/` | Upload page |
| `POST` | `/analyze` | Upload file and generate report |
| `GET` | `/download/csv` | Download quality report as CSV |
| `GET` | `/download/pdf` | Download quality report as PDF |

---

## 🧩 How Each Module Works

### `app/services/file_handler.py`
Handles secure file upload using `werkzeug.utils.secure_filename`, validates the file extension, parses CSV/Excel into a Pandas DataFrame, and cleans up the temp file after processing.

### `app/services/analyzer.py`
The core analysis engine. Runs 10 quality checks:
1. Row/column counts
2. Data preview
3. Missing value counts and percentages
4. Duplicate row detection
5. Data type inference
6. Descriptive statistics (numeric cols only)
7. IQR-based outlier detection
8. Unique value counts
9. Column-level warnings (high missing %, constant columns, possible type mismatch)
10. Overall quality score (0–100)

### `app/services/report_generator.py`
Generates downloadable reports:
- **CSV**: Plain-text tabular report using Python's `csv` module
- **PDF**: Styled, multi-section PDF using `ReportLab`

### `app/routes.py`
Flask Blueprint with three routes. Stores the report in the Flask session (for download), handles errors gracefully with `flash()` messages.

---

## ⚙️ Configuration (`config.py`)

| Setting | Default | Description |
|---|---|---|
| `SECRET_KEY` | auto | Used for Flask session encryption |
| `UPLOAD_FOLDER` | `./uploads` | Where uploaded files are stored |
| `MAX_CONTENT_LENGTH` | 16 MB | Max upload file size |
| `ALLOWED_EXTENSIONS` | `csv, xlsx, xls` | Allowed file types |
| `PREVIEW_ROWS` | 10 | Rows shown in data preview |

---

## 🛡️ Security Notes

- Files are validated by extension on both client (JS) and server (Python).
- Filenames are sanitized with `secure_filename()`.
- Uploaded files are **deleted immediately** after analysis.
- Secret key should be set via environment variable in production.

---

## 📄 License

MIT License — free for personal and commercial use.
