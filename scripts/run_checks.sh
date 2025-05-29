#!/bin/bash

# Script to run code checks and tests with coverage
# Usage: ./run_checks.sh

set -e  # Exit immediately if a command exits with a non-zero status

echo "Running Ruff checks..."
python -m ruff check .

echo ""
echo "Applying Ruff fixes where possible..."
python -m ruff check --fix .

echo ""
echo "Running tests with coverage..."
COVERAGE_FILE="coverage.json"
python -m pytest --cov-report=html --cov-report=term --cov-report=json:$COVERAGE_FILE --cov=src/hrt tests/

# Check coverage threshold
echo ""
echo "Checking coverage threshold..."
COVERAGE_THRESHOLD=80

# Calculate coverage percentage by parsing the coverage output
COVERAGE=$(python -c '
import json
import sys

# Load the coverage report
with open("'$COVERAGE_FILE'") as f:
    coverage_data = json.load(f)

# Extract the total coverage percentage
coverage = coverage_data["totals"]["percent_covered"]
print(int(coverage))
')

if [ -z "$COVERAGE" ]; then
    echo "Could not determine coverage percentage. Skipping threshold check."
else
    if [ "$COVERAGE" -lt "$COVERAGE_THRESHOLD" ]; then
        echo -e "\033[0;31mWARNING: Test coverage is ${COVERAGE}%, which is below the threshold of ${COVERAGE_THRESHOLD}%\033[0m"
        echo "Please add more tests to improve coverage."
    else
        echo -e "\033[0;32mCoverage is ${COVERAGE}%, which meets the threshold of ${COVERAGE_THRESHOLD}%\033[0m"
    fi
fi

rm -f $COVERAGE_FILE

echo ""
echo "All checks completed!"
echo "Coverage report saved to htmlcov/index.html"
