#!/usr/bin/env bash

set -e  # Exit on any error

echo "Updating package lists..."
apt-get update -y

echo "Installing ffmpeg..."
apt-get install -y ffmpeg

echo "Installing Python dependencies..."
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt

echo "Build completed."
