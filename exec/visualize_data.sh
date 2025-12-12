#!/bin/sh

echo "extracting data from traces..."
cd E2E-analysis/visualize_data/E2E/
uv run ./src/main.py
cd ../..