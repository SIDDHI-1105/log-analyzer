#!/usr/bin/env python3
"""
Test runner script that sets up PYTHONPATH correctly before invoking pytest.
"""

import sys
from pathlib import Path
import pytest

# Add backend/src to the path BEFORE importing anything
backend_src = Path(__file__).parent / "backend" / "src"
if str(backend_src) not in sys.path:
    sys.path.insert(0, str(backend_src))

# Now run pytest
sys.exit(pytest.main([str(Path(__file__).parent / "backend" / "tests"), "-v"]))
