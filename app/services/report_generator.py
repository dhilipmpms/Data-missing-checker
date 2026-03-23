"""
app/services/report_generator.py
----------------------------------
Generates downloadable reports from the quality analysis results.
Supports:
  - CSV report export
  - PDF report export (using ReportLab)
"""

import csv
import io
import datetime

# ReportLab imports for PDF generation
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)


def generate_csv_report(report):
    """
    Generate a CSV-format quality report as a string buffer.

    Args:
        report (dict): The data quality report dictionary from analyzer.py.

    Returns:
        io.StringIO: A string buffer containing the CSV data.
    """
    output = io.StringIO()
    writer = csv.writer(output)

    # ── Header ─────────────────────────────────────────────────────────────────
    writer.writerow(['Data Quality Report'])
    writer.writerow(['Generated at', datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')])
    writer.writerow([])

    # ── Summary ────────────────────────────────────────────────────────────────
    writer.writerow(['=== SUMMARY ==='])
    writer.writerow(['Total Rows', report['total_rows']])
    writer.writerow(['Total Columns', report['total_columns']])
    writer.writerow(['Total Missing Cells', report['total_missing_cells']])
    writer.writerow(['Duplicate Rows', report['duplicate_rows']])
    writer.writerow(['Quality Score', f"{report['quality_score']}/100"])
    writer.writerow([])

    # ── Missing Values ─────────────────────────────────────────────────────────
    writer.writerow(['=== MISSING VALUES ==='])
    writer.writerow(['Column', 'Missing Count', 'Missing %'])
    for col, info in report['missing_values'].items():
        writer.writerow([col, info['count'], f"{info['percentage']}%"])
    writer.writerow([])

    # ── Data Types ─────────────────────────────────────────────────────────────
    writer.writerow(['=== DATA TYPES ==='])
    writer.writerow(['Column', 'Data Type'])
    for col, dtype in report['data_types'].items():
        writer.writerow([col, dtype])
    writer.writerow([])

    # ── Statistics ─────────────────────────────────────────────────────────────
    writer.writerow(['=== STATISTICS (Numeric Columns) ==='])
    writer.writerow(['Column', 'Mean', 'Median', 'Std', 'Min', 'Max', 'Count'])
    for col, stats in report['statistics'].items():
        writer.writerow([
            col,
            stats['mean'], stats['median'], stats['std'],
            stats['min'],  stats['max'],    stats['count']
        ])
    writer.writerow([])

    # ── Outliers ───────────────────────────────────────────────────────────────
    writer.writerow(['=== OUTLIERS ==='])
    writer.writerow(['Column', 'Outlier Count', 'Lower Bound', 'Upper Bound'])
    for col, info in report['outliers'].items():
        writer.writerow([col, info['count'], info['lower_bound'], info['upper_bound']])
    writer.writerow([])

    # ── Warnings ───────────────────────────────────────────────────────────────
    writer.writerow(['=== WARNINGS ==='])
    writer.writerow(['Type', 'Column', 'Message'])
    for w in report['warnings']:
        writer.writerow([w['type'], w['column'], w['message']])

    output.seek(0)
    return output


def generate_pdf_report(report):
    """
    Generate a PDF-format quality report as a bytes buffer.

    Args:
        report (dict): The data quality report dictionary from analyzer.py.

    Returns:
        io.BytesIO: A bytes buffer containing the PDF data.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
                            rightMargin=2 * cm, leftMargin=2 * cm,
                            topMargin=2 * cm, bottomMargin=2 * cm)

    styles = getSampleStyleSheet()
    story = []

    # Custom styles
    title_style = ParagraphStyle('Title', parent=styles['Title'],
                                 fontSize=20, textColor=colors.HexColor('#2563eb'),
                                 spaceAfter=10)
    h2_style = ParagraphStyle('H2', parent=styles['Heading2'],
                              fontSize=14, textColor=colors.HexColor('#1e40af'),
                              spaceBefore=14, spaceAfter=6)
    body_style = styles['Normal']

    # ── Title ──────────────────────────────────────────────────────────────────
    story.append(Paragraph("📊 Data Quality Report", title_style))
    story.append(Paragraph(
        f"Generated: {datetime.datetime.now().strftime('%B %d, %Y at %H:%M:%S')}",
        body_style))
    story.append(HRFlowable(width='100%', thickness=1, color=colors.HexColor('#93c5fd')))
    story.append(Spacer(1, 0.3 * cm))

    # ── Summary Table ──────────────────────────────────────────────────────────
    story.append(Paragraph("Summary", h2_style))
    summary_data = [
        ['Metric', 'Value'],
        ['Total Rows', str(report['total_rows'])],
        ['Total Columns', str(report['total_columns'])],
        ['Total Missing Cells', str(report['total_missing_cells'])],
        ['Duplicate Rows', str(report['duplicate_rows'])],
        ['Quality Score', f"{report['quality_score']} / 100"],
        ['Total Warnings', str(report['warning_count'])],
    ]
    story.append(_make_table(summary_data))
    story.append(Spacer(1, 0.4 * cm))

    # ── Missing Values Table ───────────────────────────────────────────────────
    story.append(Paragraph("Missing Values", h2_style))
    mv_data = [['Column', 'Missing Count', 'Missing %']]
    for col, info in report['missing_values'].items():
        mv_data.append([col, str(info['count']), f"{info['percentage']}%"])
    story.append(_make_table(mv_data))
    story.append(Spacer(1, 0.4 * cm))

    # ── Data Types Table ───────────────────────────────────────────────────────
    story.append(Paragraph("Data Types", h2_style))
    dt_data = [['Column', 'Data Type']]
    for col, dtype in report['data_types'].items():
        dt_data.append([col, dtype])
    story.append(_make_table(dt_data))
    story.append(Spacer(1, 0.4 * cm))

    # ── Statistics Table ───────────────────────────────────────────────────────
    if report['statistics']:
        story.append(Paragraph("Statistics (Numeric Columns)", h2_style))
        st_data = [['Column', 'Mean', 'Median', 'Std Dev', 'Min', 'Max']]
        for col, s in report['statistics'].items():
            st_data.append([col, str(s['mean']), str(s['median']),
                            str(s['std']), str(s['min']), str(s['max'])])
        story.append(_make_table(st_data))
        story.append(Spacer(1, 0.4 * cm))

    # ── Warnings ───────────────────────────────────────────────────────────────
    if report['warnings']:
        story.append(Paragraph("Warnings", h2_style))
        w_data = [['Type', 'Column', 'Message']]
        for w in report['warnings']:
            w_data.append([w['type'], w['column'], w['message']])
        story.append(_make_table(w_data, warn=True))

    doc.build(story)
    buffer.seek(0)
    return buffer


def _make_table(data, warn=False):
    """
    Helper to create a styled ReportLab Table.

    Args:
        data (list of list): Rows of data; first row is the header.
        warn (bool): If True, use a warning-style (amber header) color.

    Returns:
        Table: A styled ReportLab Table object.
    """
    header_color = colors.HexColor('#f59e0b') if warn else colors.HexColor('#2563eb')
    t = Table(data, repeatRows=1, hAlign='LEFT')
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), header_color),
        ('TEXTCOLOR',  (0, 0), (-1, 0), colors.white),
        ('FONTNAME',   (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE',   (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('TOPPADDING',    (0, 0), (-1, 0), 8),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#eff6ff')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1),
         [colors.HexColor('#eff6ff'), colors.white]),
        ('FONTNAME',  (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE',  (0, 1), (-1, -1), 9),
        ('GRID',      (0, 0), (-1, -1), 0.5, colors.HexColor('#bfdbfe')),
        ('VALIGN',    (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING',  (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING',   (0, 1), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 5),
    ]))
    return t
