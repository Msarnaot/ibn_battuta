#!/bin/bash
# Ibn Battuta - MacBook Setup Script (Using Conda)
# This script sets up the project without touching your system Python

set -e  # Exit on error

echo "🚀 Setting up Ibn Battuta on your MacBook..."
echo ""

# Check if conda is installed
if ! command -v conda &> /dev/null; then
    echo "❌ Conda not found!"
    echo ""
    echo "Please install Miniconda first:"
    echo "  1. Visit: https://docs.conda.io/en/latest/miniconda.html"
    echo "  2. Download the macOS installer"
    echo "  3. Run the installer"
    echo "  4. Restart your terminal"
    echo "  5. Run this script again"
    echo ""
    exit 1
fi

echo "✅ Conda found: $(conda --version)"
echo ""

# Create conda environment
echo "📦 Creating conda environment 'ibn_battuta'..."
conda create -n ibn_battuta python=3.11 -y

echo ""
echo "✅ Conda environment created!"
echo ""

# Activate environment and install Python dependencies
echo "📥 Installing Python dependencies..."
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate ibn_battuta
pip install -r requirements.txt

echo ""
echo "✅ Python dependencies installed!"
echo ""

# Install frontend dependencies
echo "📥 Installing frontend dependencies..."
cd frontend
npm install
cd ..

echo ""
echo "✅ Frontend dependencies installed!"
echo ""

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    cp .env.example .env
    echo "✅ .env file created! Please add your API keys to .env"
    echo ""
else
    echo "✅ .env file already exists"
    echo ""
fi

echo ""
echo "✨ Setup complete! ✨"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📋 Next steps:"
echo ""
echo "1. Add your API keys to .env file:"
echo "   - GOOGLE_MAPS_API_KEY"
echo "   - AMADEUS_API_KEY"
echo "   - AMADEUS_API_SECRET"
echo ""
echo "2. Start the application:"
echo "   ./start.sh"
echo ""
echo "   Or manually:"
echo "   - Terminal 1: conda activate ibn_battuta && python api.py"
echo "   - Terminal 2: cd frontend && npm start"
echo ""
echo "3. Open http://localhost:3000 in your browser"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
