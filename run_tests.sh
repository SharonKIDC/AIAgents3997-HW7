#!/bin/bash
# Test runner script for Agent League System

set -e

echo "=================================="
echo "Agent League System - Test Runner"
echo "=================================="
echo ""

# Check Python version
echo "Checking Python version..."
python3 --version
echo ""

# Check if pytest is installed
if ! python3 -c "import pytest" 2>/dev/null; then
    echo "Installing test dependencies..."
    python3 -m pip install -r requirements-test.txt --quiet
    echo "✓ Dependencies installed"
    echo ""
fi

# Run tests
echo "Running test suite..."
echo ""

# Option 1: Run all tests with verbose output
if [ "$1" == "-v" ] || [ "$1" == "--verbose" ]; then
    python3 -m pytest tests/ -v --tb=short
# Option 2: Run with coverage
elif [ "$1" == "-c" ] || [ "$1" == "--coverage" ]; then
    python3 -m pytest tests/ --cov=src --cov-report=term --cov-report=html
    echo ""
    echo "Coverage report generated in htmlcov/index.html"
# Option 3: Run specific test file
elif [ -n "$1" ]; then
    python3 -m pytest "$1" -v
# Default: Run all tests with summary
else
    python3 -m pytest tests/ -v --tb=short
fi

echo ""
echo "=================================="
echo "Test run complete!"
echo "=================================="
