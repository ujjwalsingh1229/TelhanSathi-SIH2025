#!/bin/bash
# Installation and Setup Script for Farmer Dashboard Backend

echo "=========================================="
echo "Farmer Dashboard Backend - Setup Script"
echo "=========================================="
echo ""

# Step 1: Check Python
echo "Step 1: Checking Python installation..."
python --version
if [ $? -ne 0 ]; then
    echo "ERROR: Python not found. Please install Python 3.7+"
    exit 1
fi
echo "✓ Python found"
echo ""

# Step 2: Create virtual environment
echo "Step 2: Creating virtual environment..."
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
echo "✓ Virtual environment created"
echo ""

# Step 3: Install dependencies
echo "Step 3: Installing dependencies..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install dependencies"
    exit 1
fi
echo "✓ Dependencies installed"
echo ""

# Step 4: Initialize database
echo "Step 4: Initializing database..."
if command -v sqlite3 &> /dev/null; then
    sqlite3 farmer_dashboard.db < database_schema.sql
    echo "✓ Database initialized"
else
    echo "WARNING: sqlite3 not found. Creating empty database..."
    python -c "import sqlite3; sqlite3.connect('farmer_dashboard.db')"
    echo "⚠ Please manually run: sqlite3 farmer_dashboard.db < database_schema.sql"
fi
echo ""

# Step 5: Run tests
echo "Step 5: Running tests..."
python -m pytest test_endpoints.py -v
if [ $? -ne 0 ]; then
    echo "WARNING: Some tests failed. Check the output above."
fi
echo ""

echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
echo "To start the server, run:"
echo "  python app.py"
echo ""
echo "Then access the API at:"
echo "  http://localhost:5000/api/predict-profit (POST)"
echo "  http://localhost:5000/api/forecast-arima (POST)"
echo "  http://localhost:5000/api/recommend-crop (POST)"
echo ""
