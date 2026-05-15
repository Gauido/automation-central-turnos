import json
from pathlib import Path
from typing import Any


def read_json(path: str | Path) -> dict[str, Any]:
    file_path = Path(path)
    if not file_path.is_absolute():
        file_path = Path(__file__).resolve().parents[1] / file_path

    with file_path.open(encoding="utf-8") as file:
        return json.load(file)
