#!/usr/bin/env python3
"""
Simple Python wrapper to run tests with proper PYTHONPATH

Usage:
    python3 runtests.py                  # Run unit tests
    python3 runtests.py --integration    # Run integration tests
    python3 runtests.py --tempo          # Run Tempo tests
    python3 runtests.py --all            # Run all tests
"""

import sys
import os
from pathlib import Path

# Add backend to Python path
BACKEND_PATH = Path(__file__).parent.parent.parent / "backend"
sys.path.insert(0, str(BACKEND_PATH))

# Now run pytest
import pytest

if __name__ == "__main__":
    # Default to unit tests
    args = ["-v"]

    if len(sys.argv) > 1:
        if "--integration" in sys.argv:
            args.extend(["-m", "integration", "test_integration_traces.py"])
        elif "--tempo" in sys.argv:
            args.extend(["-m", "tempo", "test_dashboard_queries.py"])
        elif "--all" in sys.argv:
            args.append(".")
        elif "--help" in sys.argv or "-h" in sys.argv:
            print(__doc__)
            sys.exit(0)
        else:
            args.extend(["-m", "not integration and not tempo", "test_unit_instrumentation.py"])
    else:
        # Default: unit tests only
        args.extend(["-m", "not integration and not tempo", "test_unit_instrumentation.py"])

    # Run pytest
    sys.exit(pytest.main(args))
