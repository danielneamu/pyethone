import sys
import os
import json


def get_venv_info():
    venv_path = sys.prefix
    venv_name = os.path.basename(venv_path)
    python_version = f"{sys.version_info.major}.{
        sys.version_info.minor}.{sys.version_info.micro}"

    # Check if yfinance is installed
    yfinance_installed = False
    try:
        import yfinance
        yfinance_installed = True
        yfinance_version = yfinance.__version__
    except ImportError:
        yfinance_version = "Not installed"

    info = {
        "venv_path": venv_path,
        "venv_name": venv_name,
        "python_version": python_version,
        "yfinance_installed": yfinance_installed,
        "yfinance_version": yfinance_version
    }

    print(json.dumps(info))
    sys.stdout.flush()  # Ensure output is flushed


if __name__ == "__main__":
    get_venv_info()
