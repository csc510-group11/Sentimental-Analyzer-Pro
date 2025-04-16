#!/bin/bash

# Start virtual display
Xvfb :99 -screen 0 1920x1080x24 &

export DISPLAY=:99

# Run Django
python sentimental_analysis/manage.py makemigrations
python sentimental_analysis/manage.py migrate
python sentimental_analysis/manage.py runserver 0.0.0.0:8000
