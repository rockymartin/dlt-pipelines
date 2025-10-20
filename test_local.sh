#!/bin/bash

# Local testing script for Pokemon Pipeline
# This script helps you test the pipeline locally before deploying to Cloud Run

set -e

echo "Pokemon Pipeline - Local Testing Script"
echo "======================================="

# Check if we're in a virtual environment
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "Warning: No virtual environment detected. Consider using one for isolation."
fi

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Test basic imports
echo "Testing imports..."
python -c "
import dlt
from pokemon import source
print('✓ All imports successful')
"

# Test with sample data
echo "Running pipeline with sample data (first 5 Pokemon)..."
export POKEMON_RESOURCES="pokemon_details"
export POKEMON_LIMIT="5"

# For local testing, we'll use a local destination instead of BigQuery
echo "Note: For local testing, you may want to use a local destination like 'duckdb'"
echo "To test with BigQuery, ensure you have:"
echo "1. Google Cloud credentials configured"
echo "2. BigQuery dataset 'pokemon_data' created"
echo "3. Proper permissions"

read -p "Do you want to test with BigQuery? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Testing with BigQuery..."
    python pokemon_pipeline.py
else
    echo "Skipping BigQuery test. You can run 'python pokemon_pipeline.py' manually when ready."
fi

echo "Local testing completed!"
echo ""
echo "Next steps:"
echo "1. Push your code to GitHub"
echo "2. Set up GitHub secrets (GCP_PROJECT_ID, GCP_SA_KEY)"
echo "3. The GitHub Action will automatically deploy to Cloud Run"
