#!/bin/bash
cd /app
. venv/bin/activate
python3 manage.py migrate
python3 manage.py createsuperuser --noinput --username admin --email noreply@noreply.com
python3 manage.py runserver 0.0.0.0:8000