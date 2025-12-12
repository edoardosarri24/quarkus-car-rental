#!/bin/sh

echo "extracting data from traces..."
cd E2E-analysis/extract_data
uv run ./src/main.py
cd ../..