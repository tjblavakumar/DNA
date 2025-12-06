#!/bin/bash

echo "==================================="
echo "Daily News AI Assistant Setup"
echo "==================================="
echo ""

# Check Python version
echo "Checking Python version..."
python3 --version

# Create virtual environment
echo ""
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo ""
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo ""
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "Please edit .env file and add your AWS credentials!"
else
    echo ""
    echo ".env file already exists."
fi

# Create static directory
mkdir -p static

echo ""
echo "==================================="
echo "Setup Complete!"
echo "==================================="
echo ""
echo "Next steps:"
echo "1. Edit .env file and add your AWS credentials"
echo "2. (Optional) Add logo image to static/frb_sf_logo.jpg"
echo "3. Run: source venv/bin/activate"
echo "4. Run: python app.py"
echo "5. Open browser to http://localhost:5000"
echo ""
