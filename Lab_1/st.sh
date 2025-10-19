#!/bin/bash

# Script to start the Flask image blender application
# st.sh - startup script

echo "Starting Flask Image Blender Application..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python3 is not installed"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install requirements
echo "Installing requirements..."
pip install -r requirements.txt

# Create necessary directories
mkdir -p static/uploads
mkdir -p static/css
mkdir -p static/js

# Start the application
echo "Starting Flask application..."
export FLASK_APP=some_app.py
export FLASK_ENV=development

# Run the application
python some_app.py

# Deactivate virtual environment when done
deactivate
echo "Application stopped."
