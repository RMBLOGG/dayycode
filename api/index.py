import sys
import os

# Make sure the root project is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app import app

# Vercel looks for a variable named `app`
