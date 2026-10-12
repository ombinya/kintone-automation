"""Compile Qt Designer forms into importable PySide6 modules."""

from pathlib import Path
import re
import shutil
import subprocess


BASE_DIR = Path(__file__).resolve().parent.parent
UI_DIR = BASE_DIR / "ui"
OUTPUT_DIR = BASE_DIR / "gen_ui"


def _module_name(ui_file: Path) -> str:
    """Return a valid generated module name for a Designer file."""
    clean_name = re.sub(r"\W+", "_", ui_file.stem).strip("_")
    if not clean_name:
        raise ValueError(f"UI filename cannot form a Python module: {ui_file}")
    if clean_name[0].isdigit():
        clean_name = f"ui_{clean_name}"
    return f"{clean_name}_ui.py"


def _ensure_package(directory: Path) -> None:
    directory.mkdir(parents=True, exist_ok=True)
    (directory / "__init__.py").touch(exist_ok=True)


def ui_to_py() -> None:
    """Regenerate Python modules for every ``ui/**/*.ui`` source file."""
    if not UI_DIR.is_dir():
        raise FileNotFoundError(f"UI directory not found: {UI_DIR}")

    ui_files = sorted(UI_DIR.rglob("*.ui"))
    if not ui_files:
        raise FileNotFoundError(f"No .ui files found in: {UI_DIR}")

    uic_command = shutil.which("pyside6-uic")
    if uic_command is None:
        raise RuntimeError(
            "pyside6-uic was not found. Install PySide6 in the active "
            "Python environment."
        )

    _ensure_package(OUTPUT_DIR)

    for ui_file in ui_files:
        relative_parent = ui_file.relative_to(UI_DIR).parent
        output_directory = OUTPUT_DIR / relative_parent
        _ensure_package(output_directory)
        output_file = output_directory / _module_name(ui_file)

        result = subprocess.run(
            [uic_command, str(ui_file), "-o", str(output_file)],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            error = result.stderr.strip() or result.stdout.strip()
            raise RuntimeError(f"Failed to convert {ui_file}:\n{error}")

        print(f"Converted {ui_file.relative_to(BASE_DIR)} -> "
              f"{output_file.relative_to(BASE_DIR)}")


if __name__ == "__main__":
    ui_to_py()
