"""
run.py
------
Application entry point.
Run this file to start the Data Quality Checker web application.

Usage:
    python run.py

The application will be available at http://127.0.0.1:5000
"""

from app import create_app
from config import DevelopmentConfig

# Create the Flask application instance using the factory function
app = create_app(DevelopmentConfig)

if __name__ == '__main__':
    print("=" * 60)
    print("  Data Quality Checker - Starting Server")
    print("  Visit: http://127.0.0.1:5000")
    print("=" * 60)
    app.run(debug=True, host='0.0.0.0', port=5000)
