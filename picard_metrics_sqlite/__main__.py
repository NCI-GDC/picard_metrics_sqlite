import sys

from picard_metrics_sqlite.main import main

try:
    from picard_metrics_sqlite.main import __version__
except Exception:
    __version__ = "0.0.0"

if __name__ == "__main__":
    sys.exit(main())
