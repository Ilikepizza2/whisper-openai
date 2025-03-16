#!/bin/bash

START_COMMAND="python api-server.py"


# Create and activate Conda environment
echo "Setting up Conda environment..."
conda create -y -n "whisper" python="3.10"
source activate "whisper" || conda activate "whisper"

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt


# Start the model server
echo "Starting Whisper server..."
eval "$START_COMMAND"
