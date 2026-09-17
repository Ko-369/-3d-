"""
Process the Hi3D photogrammetry scans in 模型/*.glb into deployable web models
in public/models/*.glb.

The scans are already correctly oriented (Y-up glTF, one watertight-ish mesh,
~500k triangles). Their only problem for the web is texture weight: the base
colour map is an 8K PNG (~30 MB) and the metallic/roughness map a 3K PNG (~4 MB).
Re-encoding both as JPEG keeps the geometry, UVs, materials and orientation
bit-for-bit while shrinking a 43–55 MB file to ~20 MB — the same weight class as
the already-shipped cpu.glb / motherboard.glb.

CPU is intentionally excluded (already shipped, "don't touch").
"""
import io
import os
import sys
from pathlib import Path

import trimesh
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "模型"
DST = ROOT / "public" / "models"

# 模型/*.glb source filename -> public/models target name (no extension).
JOBS = [
    ("主板.glb",      "motherboard"),
    ("cpu散热器.glb", "cooling"),
    ("内存条.glb",    "memory"),
    ("固态硬盘.glb",  "storage"),
    ("显卡.glb",      "gpu"),
    ("电源.glb",      "power"),
    ("网卡.glb",      "network"),
    ("机箱.glb",      "case"),
]

# Base colour is capped at 4K — the model is rendered at FIT_SIZE (~3.8 world
# units) in a ~800px viewport, so 4K already has ~5x more texel detail than the
# closest zoom needs; 8K is pure download weight. The metallic/roughness data
# map is halved to 2K — its G/B channels are smooth, so it needs far less
# resolution than the albedo.
BASE_MAX = 4096
BASE_QUALITY = 88
MR_MAX = 2048
MR_QUALITY = 92


def to_jpeg(pil: Image.Image, maxdim: int, quality: int) -> Image.Image:
    """Resize (if over maxdim) and re-encode a texture as an in-memory JPEG."""
    if pil.mode not in ("RGB", "L"):
        pil = pil.convert("RGB")
    w, h = pil.size
    longest = max(w, h)
    if longest > maxdim:
        ratio = maxdim / longest
        pil = pil.resize((max(1, int(w * ratio)), max(1, int(h * ratio))), Image.LANCZOS)
    buf = io.BytesIO()
    pil.save(buf, format="JPEG", quality=quality, optimize=True, subsampling=2)
    buf.seek(0)
    return Image.open(buf)


def process(src: Path, dst: Path) -> int:
    scene = trimesh.load(str(src), force="scene")
    recompressed = 0
    for geom in scene.geometry.values():
        material = getattr(getattr(geom, "visual", None), "material", None)
        if material is None:
            continue
        if getattr(material, "baseColorTexture", None) is not None:
            material.baseColorTexture = to_jpeg(material.baseColorTexture, BASE_MAX, BASE_QUALITY)
            recompressed += 1
        if getattr(material, "metallicRoughnessTexture", None) is not None:
            material.metallicRoughnessTexture = to_jpeg(
                material.metallicRoughnessTexture, MR_MAX, MR_QUALITY
            )
            recompressed += 1
        if getattr(material, "normalTexture", None) is not None:
            material.normalTexture = to_jpeg(material.normalTexture, MR_MAX, MR_QUALITY)
            recompressed += 1
    scene.export(file_type="glb", file_obj=str(dst))
    return recompressed


def main() -> None:
    only = sys.argv[1] if len(sys.argv) > 1 else None
    for src_name, target in JOBS:
        if only and target != only:
            continue
        src = SRC / src_name
        dst = DST / f"{target}.glb"
        if not src.exists():
            print(f"MISSING  {src}")
            continue
        n = process(src, dst)
        src_mb = src.stat().st_size / 1e6
        dst_mb = dst.stat().st_size / 1e6
        print(f"{src_name:<16} -> {target:<12} {src_mb:6.1f} MB -> {dst_mb:6.1f} MB  ({n} textures)")


if __name__ == "__main__":
    main()
