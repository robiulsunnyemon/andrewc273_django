#!/bin/bash

echo "🔄 Pulling latest changes from Git..."
git pull

echo "⚙️ Checking for virtual environment..."
if [ -d "venv" ]; then
    echo "Using venv/bin/python..."
    venv/bin/python manage.py load_halfway_houses
elif [ -d "env" ]; then
    echo "Using env/bin/python..."
    env/bin/python manage.py load_halfway_houses
else
    echo "Using system python..."
    python manage.py load_halfway_houses
fi

echo "✅ Import completed!"
