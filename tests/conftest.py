"""
Pytest configuration for FocusTimer tests.
Sets the headless Qt platform before any test module is imported.
"""

import os
import sys

# Force headless rendering — must happen before PyQt6 is first imported.
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

# Ensure the project root is on sys.path so 'import config', 'import core.*'
# etc. resolve correctly regardless of how pytest is invoked.
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
