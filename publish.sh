#!/bin/bash
set -e

# Ensure we're in the project root
cd "$(dirname "$0")"

echo "Installing build dependencies..."
uv pip install pyinstaller

echo "Building binary..."
# --onefile: Create a single executable file
# --name: Name of the executable
# --clean: Clean PyInstaller cache and remove temporary files before building
uv run pyinstaller --onefile --clean --name github-reports github_reports/cli.py

echo ""
echo "Build complete!"
echo "The binary is located at: dist/github-reports"
echo "You can add this to your PATH or copy it to a bin directory."
