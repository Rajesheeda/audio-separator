#!/usr/bin/env bash

# Exit on any error
set -o errexit

# Install system dependencies (FFmpeg)
apt-get update && apt-get install -y ffmpeg

# Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt
