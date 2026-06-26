from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any

try:
    import bpy
except ImportError:  # pragma: no cover - exercised in plain Python test environments
    class _BpyStub:
        class _App:
            version_string = "unknown"

        class _Data:
            filepath = ""

        app = _App()
        data = _Data()

    bpy = _BpyStub()

CATEGORY_FOLDERS = {
    "hair": "hair",
    "top": "tops",
    "bottom": "bottoms",
    "shoes": "shoes",
    "accessory": "accessories",
}

CATEGORY_LABELS = {
    "hair": "Hair",
    "top": "Top",
    "bottom": "Bottom",
    "shoes": "Shoes",
    "accessory": "Accessory",
}

DEFAULT_SLOTS = {
    "hair": "head",
    "top": "torso",
    "bottom": "legs",
    "shoes": "feet",
    "accessory": "body",
}


def sanitize_name(name: str) -> str:
    cleaned = re.sub(r"[^0-9A-Za-z._-]+", "_", name).strip("._-")
    return cleaned or "asset"


def get_category_folder(category: str) -> str:
    return CATEGORY_FOLDERS.get(category, "accessories")


def get_default_slot(category: str) -> str:
    return DEFAULT_SLOTS.get(category, "body")


def build_export_output_path(library_root: str, category: str, object_name: str) -> str:
    root = Path(library_root).expanduser().resolve()
    category_folder = get_category_folder(category)
    filename = f"{sanitize_name(object_name)}.usd"
    return str((root / category_folder / filename).resolve())


def build_metadata(
    category: str,
    object_name: str,
    source_file: str | None,
    slot: str | None = None,
    exclusivity_tags: list[str] | None = None,
) -> dict[str, Any]:
    metadata = {
        "category": category,
        "slot": slot or get_default_slot(category),
        "exclusivity_tags": exclusivity_tags or [],
        "source_file": source_file or bpy.data.filepath or "",
        "export_date": datetime.utcnow().isoformat() + "Z",
        "blender_version": bpy.app.version_string,
        "source_asset_name": object_name,
    }
    return metadata


def ensure_library_root(library_root: str) -> Path:
    root = Path(library_root).expanduser().resolve()
    root.mkdir(parents=True, exist_ok=True)
    return root


def write_metadata_sidecar(export_path: str, metadata: dict[str, Any]) -> str:
    sidecar_path = Path(export_path).with_suffix(".json")
    ensure_library_root(str(sidecar_path.parent))
    with sidecar_path.open("w", encoding="utf-8") as handle:
        json.dump(metadata, handle, indent=2)
        handle.write("\n")
    return str(sidecar_path)
