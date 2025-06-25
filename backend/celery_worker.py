#!/usr/bin/env python
"""
Celery worker startup script.
Run with: python celery_worker.py
"""
import sys
import os

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.celery_app import celery_app

if __name__ == "__main__":
    celery_app.start()