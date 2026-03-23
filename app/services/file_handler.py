"""
app/services/file_handler.py
-----------------------------
Handles file upload validation and parsing.
Supports CSV and Excel (.xlsx, .xls) file formats.
"""

import os
import pandas as pd
from werkzeug.utils import secure_filename


def allowed_file(filename, allowed_extensions):
    """
    Check if the uploaded file has an allowed extension.

    Args:
        filename (str): The name of the uploaded file.
        allowed_extensions (set): Set of allowed file extensions.

    Returns:
        bool: True if allowed, False otherwise.
    """
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions


def save_uploaded_file(file, upload_folder):
    """
    Securely save the uploaded file to the upload folder.

    Args:
        file: The file object from Flask request.
        upload_folder (str): Path to the folder where files are saved.

    Returns:
        str: The full saved file path.

    Raises:
        ValueError: If the file has an invalid name.
    """
    filename = secure_filename(file.filename)
    if not filename:
        raise ValueError("Invalid file name.")
    filepath = os.path.join(upload_folder, filename)
    file.save(filepath)
    return filepath


def parse_file(filepath):
    """
    Parse a CSV or Excel file into a Pandas DataFrame.

    Args:
        filepath (str): Full path to the uploaded file.

    Returns:
        pd.DataFrame: The parsed dataset as a DataFrame.

    Raises:
        ValueError: If the file format is not supported or cannot be read.
    """
    ext = filepath.rsplit('.', 1)[1].lower()

    try:
        if ext == 'csv':
            # Try reading with UTF-8 first, fall back to latin-1 for special chars
            try:
                df = pd.read_csv(filepath, encoding='utf-8')
            except UnicodeDecodeError:
                df = pd.read_csv(filepath, encoding='latin-1')
        elif ext in ('xlsx', 'xls'):
            df = pd.read_excel(filepath, engine='openpyxl')
        else:
            raise ValueError(f"Unsupported file format: .{ext}")
    except Exception as e:
        raise ValueError(f"Could not read the file: {str(e)}")

    if df.empty:
        raise ValueError("The uploaded file is empty.")

    return df


def delete_file(filepath):
    """
    Delete a file from the filesystem after processing.

    Args:
        filepath (str): Full path to the file to delete.
    """
    try:
        if os.path.exists(filepath):
            os.remove(filepath)
    except OSError:
        pass  # Non-critical if deletion fails
