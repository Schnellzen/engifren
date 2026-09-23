#!/usr/bin/env python3
"""
Shrink project photos before uploading, so the site stays fast on phones.

    python tools/compress_images.py projects/my-project

- resizes so the long side is at most 1600 px
- fixes phone-camera rotation
- removes metadata (including GPS location from phone photos)
- overwrites the files in place, keeping the same file names

Needs Pillow:  pip install pillow
"""
import sys
from pathlib import Path

from PIL import Image, ImageOps

MAX_SIDE = 1600
JPEG_QUALITY = 82
EXTS = {".jpg", ".jpeg", ".png", ".webp"}


def process(path):
    before = path.stat().st_size
    with Image.open(path) as im:
        im = ImageOps.exif_transpose(im)
        im.thumbnail((MAX_SIDE, MAX_SIDE), Image.LANCZOS)
        ext = path.suffix.lower()
        if ext in (".jpg", ".jpeg"):
            im.convert("RGB").save(path, "JPEG", quality=JPEG_QUALITY, optimize=True, progressive=True)
        elif ext == ".webp":
            im.save(path, "WEBP", quality=JPEG_QUALITY)
        else:
            im.save(path, "PNG", optimize=True)
    after = path.stat().st_size
    print(f"  {path}: {before // 1024} KB -> {after // 1024} KB")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    for arg in sys.argv[1:]:
        for f in sorted(Path(arg).rglob("*")):
            if f.suffix.lower() in EXTS and f.is_file():
                process(f)


if __name__ == "__main__":
    main()
