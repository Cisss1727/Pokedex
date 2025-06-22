#!/bin/bash

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Check if MongoDB is running
echo "Checking MongoDB status..."
if ! pgrep -x "mongod" > /dev/null; then
    echo "MongoDB is not running. Please start MongoDB before running the application."
    echo "You can start MongoDB with: mongod --dbpath=data/db"
    exit 1
fi

# Run the application
echo "Starting the application..."
python run.py 