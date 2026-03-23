"""
app/services/analyzer.py
-------------------------
Core data quality analysis engine.
Performs comprehensive checks on the uploaded dataset:
  - Missing/null values
  - Duplicate records
  - Data type detection
  - Basic statistics (mean, min, max)
  - Format / pattern validation
  - Range outlier detection
"""

import pandas as pd
import numpy as np
import re


def analyze_dataset(df, preview_rows=10):
    """
    Main entry point: runs all quality checks on the DataFrame.

    Args:
        df (pd.DataFrame): The dataset to analyze.
        preview_rows (int): Number of rows to include in the preview.

    Returns:
        dict: A comprehensive data quality report dictionary.
    """
    report = {}

    # ── 1. Basic Info ──────────────────────────────────────────────────────────
    report['total_rows'] = int(df.shape[0])
    report['total_columns'] = int(df.shape[1])
    report['column_names'] = list(df.columns)

    # ── 2. Data Preview (first N rows, NaN → None for JSON serialization) ─────
    report['preview'] = df.head(preview_rows).where(pd.notnull(df), None).to_dict(orient='records')
    report['preview_columns'] = list(df.columns)

    # ── 3. Missing Values ──────────────────────────────────────────────────────
    missing = df.isnull().sum()
    missing_pct = (missing / len(df) * 100).round(2)
    report['missing_values'] = {
        col: {
            'count': int(missing[col]),
            'percentage': float(missing_pct[col])
        }
        for col in df.columns
    }
    report['total_missing_cells'] = int(missing.sum())

    # ── 4. Duplicate Rows ──────────────────────────────────────────────────────
    duplicate_count = int(df.duplicated().sum())
    report['duplicate_rows'] = duplicate_count
    report['duplicate_percentage'] = round(duplicate_count / len(df) * 100, 2) if len(df) > 0 else 0.0

    # ── 5. Data Types ──────────────────────────────────────────────────────────
    report['data_types'] = {col: str(dtype) for col, dtype in df.dtypes.items()}

    # ── 6. Basic Statistics for Numeric Columns ──────────────────────────────
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    stats = {}
    for col in numeric_cols:
        col_data = df[col].dropna()
        stats[col] = {
            'mean':   round(float(col_data.mean()), 4)   if len(col_data) > 0 else None,
            'median': round(float(col_data.median()), 4) if len(col_data) > 0 else None,
            'std':    round(float(col_data.std()), 4)    if len(col_data) > 0 else None,
            'min':    round(float(col_data.min()), 4)    if len(col_data) > 0 else None,
            'max':    round(float(col_data.max()), 4)    if len(col_data) > 0 else None,
            'count':  int(col_data.count()),
        }
    report['statistics'] = stats

    # ── 7. Outlier Detection (IQR method) ──────────────────────────────────────
    outliers = {}
    for col in numeric_cols:
        col_data = df[col].dropna()
        if len(col_data) < 4:
            continue
        Q1 = col_data.quantile(0.25)
        Q3 = col_data.quantile(0.75)
        IQR = Q3 - Q1
        lower = Q1 - 1.5 * IQR
        upper = Q3 + 1.5 * IQR
        out_count = int(((col_data < lower) | (col_data > upper)).sum())
        outliers[col] = {
            'count': out_count,
            'lower_bound': round(float(lower), 4),
            'upper_bound': round(float(upper), 4),
        }
    report['outliers'] = outliers

    # ── 8. Unique Value Counts ──────────────────────────────────────────────────
    report['unique_counts'] = {col: int(df[col].nunique()) for col in df.columns}

    # ── 9. Column-level Warnings ───────────────────────────────────────────────
    warnings = []

    for col in df.columns:
        missing_pct_val = report['missing_values'][col]['percentage']

        # Warn if column has > 20% missing values
        if missing_pct_val > 20:
            warnings.append({
                'type': 'HIGH_MISSING',
                'column': col,
                'message': f"Column '{col}' has {missing_pct_val}% missing values."
            })

        # Warn if column has only 1 unique value (constant column)
        if report['unique_counts'][col] == 1:
            warnings.append({
                'type': 'CONSTANT_COLUMN',
                'column': col,
                'message': f"Column '{col}' has only one unique value (constant column)."
            })

        # Warn if a numeric column might be stored as string
        if df[col].dtype == object:
            sample = df[col].dropna().head(20)
            numeric_looking = sample.apply(_is_numeric_string).sum()
            if len(sample) > 0 and numeric_looking / len(sample) > 0.8:
                warnings.append({
                    'type': 'TYPE_MISMATCH',
                    'column': col,
                    'message': f"Column '{col}' looks numeric but is stored as text/object."
                })

    # Warn if duplicate rows found
    if duplicate_count > 0:
        warnings.append({
            'type': 'DUPLICATES',
            'column': 'all',
            'message': f"Dataset contains {duplicate_count} duplicate row(s) ({report['duplicate_percentage']}%)."
        })

    report['warnings'] = warnings
    report['warning_count'] = len(warnings)

    # ── 10. Overall Quality Score ──────────────────────────────────────────────
    report['quality_score'] = _compute_quality_score(report)

    return report


def _is_numeric_string(val):
    """
    Check if a string value looks like a number.

    Args:
        val: Any value.

    Returns:
        bool: True if the value can be interpreted as numeric.
    """
    try:
        float(str(val).replace(',', ''))
        return True
    except (ValueError, TypeError):
        return False


def _compute_quality_score(report):
    """
    Compute an overall data quality score (0–100).
    Penalizes for missing values, duplicates, warnings, and outliers.

    Args:
        report (dict): The quality report dictionary.

    Returns:
        float: Quality score between 0 and 100.
    """
    score = 100.0

    total_cells = report['total_rows'] * report['total_columns']
    if total_cells > 0:
        missing_ratio = report['total_missing_cells'] / total_cells
        score -= missing_ratio * 40   # Up to -40 for missing values

    if report['total_rows'] > 0:
        dup_ratio = report['duplicate_rows'] / report['total_rows']
        score -= dup_ratio * 20       # Up to -20 for duplicates

    score -= report['warning_count'] * 5   # -5 per warning
    score = max(0.0, min(100.0, score))

    return round(score, 1)
