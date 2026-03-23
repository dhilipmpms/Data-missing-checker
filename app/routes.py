"""
app/routes.py
--------------
Flask Blueprint containing all route definitions for the application.
Routes:
    GET  /           → Upload page (index)
    POST /analyze    → Process uploaded file and return quality report
    GET  /download/<format> → Download report as CSV or PDF
"""

import os
import json
from flask import (
    Blueprint, render_template, request, redirect,
    url_for, flash, session, send_file, current_app
)
from app.services.file_handler import allowed_file, save_uploaded_file, parse_file, delete_file
from app.services.analyzer import analyze_dataset
from app.services.report_generator import generate_csv_report, generate_pdf_report

# Create the Blueprint – all routes will be registered under this blueprint
main_bp = Blueprint('main', __name__)


@main_bp.route('/', methods=['GET'])
def index():
    """
    Home page – displays the file upload form.
    """
    return render_template('index.html')


@main_bp.route('/analyze', methods=['POST'])
def analyze():
    """
    Handle file upload and run data quality analysis.
    Validates the uploaded file, parses it into a DataFrame,
    runs all quality checks, stores the report in the session,
    and renders the results dashboard.
    """
    # ── Validate file is present ───────────────────────────────────────────────
    if 'file' not in request.files:
        flash('No file selected. Please choose a CSV or Excel file.', 'error')
        return redirect(url_for('main.index'))

    file = request.files['file']

    if file.filename == '':
        flash('No file selected. Please choose a CSV or Excel file.', 'error')
        return redirect(url_for('main.index'))

    # ── Validate file extension ────────────────────────────────────────────────
    allowed = current_app.config['ALLOWED_EXTENSIONS']
    if not allowed_file(file.filename, allowed):
        flash('Invalid file type. Only CSV and Excel (.xlsx/.xls) files are allowed.', 'error')
        return redirect(url_for('main.index'))

    filepath = None
    try:
        # ── Save and parse the file ────────────────────────────────────────────
        upload_folder = current_app.config['UPLOAD_FOLDER']
        filepath = save_uploaded_file(file, upload_folder)
        df = parse_file(filepath)

        # ── Run quality analysis ───────────────────────────────────────────────
        preview_rows = current_app.config.get('PREVIEW_ROWS', 10)
        report = analyze_dataset(df, preview_rows=preview_rows)
        report['filename'] = os.path.basename(filepath)

        # ── Store report in session for download ───────────────────────────────
        # Store only the serializable parts (skip preview for session size)
        session_report = {k: v for k, v in report.items() if k != 'preview'}
        session['report'] = json.dumps(session_report)

        return render_template('report.html', report=report)

    except ValueError as e:
        flash(f'Error processing file: {str(e)}', 'error')
        return redirect(url_for('main.index'))

    except Exception as e:
        flash(f'An unexpected error occurred: {str(e)}', 'error')
        return redirect(url_for('main.index'))

    finally:
        # Always clean up the uploaded file after processing
        if filepath:
            delete_file(filepath)


@main_bp.route('/download/<report_format>', methods=['GET'])
def download_report(report_format):
    """
    Download the quality report in CSV or PDF format.

    Args:
        report_format (str): Either 'csv' or 'pdf'.
    """
    # Retrieve stored report from session
    report_json = session.get('report')
    if not report_json:
        flash('No report available. Please upload a file first.', 'error')
        return redirect(url_for('main.index'))

    report = json.loads(report_json)
    filename_base = report.get('filename', 'report').rsplit('.', 1)[0]

    if report_format == 'csv':
        # Generate CSV report
        csv_buffer = generate_csv_report(report)
        return send_file(
            csv_buffer,
            mimetype='text/csv',
            as_attachment=True,
            download_name=f'{filename_base}_quality_report.csv'
        )

    elif report_format == 'pdf':
        # Generate PDF report
        pdf_buffer = generate_pdf_report(report)
        return send_file(
            pdf_buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f'{filename_base}_quality_report.pdf'
        )

    else:
        flash('Unknown report format requested.', 'error')
        return redirect(url_for('main.index'))
