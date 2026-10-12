"""Development entry point.

Regenerate every Qt Designer form before starting the application::

    python _main.py
"""


if __name__ == "__main__":
    from utils.ui_converter import ui_to_py

    ui_to_py()

    from main import main

    raise SystemExit(main())
