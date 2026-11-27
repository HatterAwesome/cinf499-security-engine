"""Portable font selection for floor plan annotations."""

import os
from PIL import ImageFont


def load_label_font(size):

    candidates = [
        os.environ.get("FLOORPLAN_FONT"),
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
        "C:/Windows/Fonts/arialbd.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "DejaVuSans-Bold.ttf"
    ]

    for candidate in candidates:

        if not candidate:
            continue

        try:
            return ImageFont.truetype(candidate, size)
        except OSError:
            continue

    return ImageFont.load_default(size=size)
