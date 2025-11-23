#!/bin/bash

# Quick Test Script to Verify Setup
# Run this to check if everything is working

set -e

echo "🧪 TESTING EVALUATION SETUP"
echo "=============================="
echo ""

# Check GROQ_API_KEY
echo "1. Checking GROQ_API_KEY..."
if [ -z "$GROQ_API_KEY" ]; then
    echo "❌ GROQ_API_KEY not set!"
    echo "   Run: export GROQ_API_KEY=your_key"
    exit 1
else
    echo "✅ GROQ_API_KEY is set"
fi

# Check backend
echo ""
echo "2. Checking backend..."
if curl -s -f http://localhost:8080/health > /dev/null 2>&1; then
    echo "✅ Backend is running"
else
    echo "⚠️  Backend not running (optional for retrieval-only tests)"
    echo "   Start with: cd ../backend && docker-compose up"
fi

# Check dependencies
echo ""
echo "3. Checking Python dependencies..."
poetry run python check_dependencies.py

echo ""
echo "=============================="
echo "🎯 RUNNING QUICK TEST"
echo "=============================="
echo ""

# Run retrieval evaluation (doesn't need backend or API)
echo "Running retrieval evaluation (no backend needed)..."
poetry run python evaluate_retrieval.py --dataset test_dataset.json

echo ""
echo "=============================="
echo "✅ SETUP TEST COMPLETE!"
echo "=============================="
echo ""
echo "Everything looks good! 🎉"
echo ""
echo "To run full evaluation:"
echo "  ./run_all_evaluations.sh"
echo ""
