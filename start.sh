#!/bin/bash
# Start gunicorn with increased timeout for large file uploads
gunicorn --bind 0.0.0.0:5000 --reuse-port --reload --timeout 300 --workers 1 main:app
