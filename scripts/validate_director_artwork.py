"""Check the published native PNG set and its collection artwork patch.

Usage: python scripts/validate_director_artwork.py
Dependencies: numpy, opencv-python-headless
"""
import hashlib
import json
from pathlib import Path

import cv2
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / "assets/covers/diretores/revisao-2026-10-17"


def validate():
    manifest = json.loads((ART / "manifest.json").read_text("utf-8"))
    patch = json.loads((ROOT / "collections/diretores-artwork.json").read_text("utf-8"))
    rows = manifest["directors"]
    assert len(rows) == len(patch["folders"]) == 38
    assert len({r["slug"] for r in rows}) == len({r["folderId"] for r in rows}) == 38
    assert patch["collectionId"] == "collection-f3634f6f"
    total = 0
    for row, folder in zip(rows, patch["folders"]):
        assert (row["folderId"], row["name"]) == (folder["id"], folder["title"])
        assert set(row["files"]) == set(manifest["formats"])
        portrait_alpha = None
        for kind, info in row["files"].items():
            path = ROOT / info["path"]
            assert path.resolve().is_relative_to(ART.resolve())
            data = path.read_bytes()
            assert len(data) == info["bytes"] < 100 * 1024 * 1024
            assert hashlib.sha256(data).hexdigest() == info["sha256"]
            image = cv2.imdecode(np.frombuffer(data, np.uint8), cv2.IMREAD_UNCHANGED)
            assert image.ndim == 3 and image.shape[2] == 4, path
            height, width = image.shape[:2]
            assert [width, height] == [info["width"], info["height"]]
            assert image.dtype == (np.uint16 if info["bits"] == 16 else np.uint8)
            # Existing native layouts can differ by one rounding pixel.
            assert abs(width / height - (16 / 9 if kind.startswith("landscape") else 2 / 3)) < .003
            alpha = image[:, :, 3]
            assert alpha.min() == 0 and alpha.max() > 0
            assert np.any(alpha[-1] > 0), (row["slug"], kind, "bottom gap")
            if kind == "portrait-color":
                portrait_alpha = alpha.copy()
            elif kind == "portrait-bw":
                assert np.array_equal(portrait_alpha, alpha), row["slug"]
                assert np.array_equal(image[:, :, 0], image[:, :, 1])
                assert np.array_equal(image[:, :, 1], image[:, :, 2])
            total += len(data)
        files = row["files"]
        assert folder["set"] == {
            "tileShape": "POSTER",
            "coverImageUrl": files["portrait-bw"]["url"],
            "focusGifUrl": files["portrait-color"]["url"],
            "focusGifEnabled": True,
            "heroBackdropUrl": files["landscape-color"]["url"],
        }
    print(f"OK: {len(rows)} directors, {len(rows) * 3} native PNGs, {total:,} bytes")


if __name__ == "__main__":
    validate()
