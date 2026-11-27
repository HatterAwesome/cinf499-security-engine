from pathlib import Path

import json
import numpy as np

from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage


def clean_mask(mask, size=15):

    votes = np.stack([
        ndimage.uniform_filter(
            (mask == idx).astype(np.float32),
            size=size
        )
        for idx in range(21)
    ])

    return votes.argmax(axis=0).astype(np.uint8)


def render_labels(original, mask, classes, min_area=12000):

    image = original.copy()

    w, h = image.size
    scale = min(512 / w, 512 / h)

    nw = max(1, round(w * scale))
    nh = max(1, round(h * scale))

    left = (512 - nw) // 2
    top = (512 - nh) // 2

    mask = Image.fromarray(mask.astype(np.uint8))

    mask = mask.crop(
        (left, top, left + nw, top + nh)
    )

    mask = np.asarray(
        mask.resize((w, h), Image.Resampling.NEAREST)
    )

    draw = ImageDraw.Draw(image)

    font = ImageFont.truetype(
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
        28
    )

    placed = 0

    for name, idx in classes.items():

        if idx == 0:
            continue

        regions, count = ndimage.label(mask == idx)

        for region_id in range(1, count + 1):

            region = regions == region_id

            if region.sum() < min_area:
                continue

            distance = ndimage.distance_transform_edt(
                np.pad(region, 1, constant_values=False)
            )[1:-1, 1:-1]

            y, x = np.unravel_index(
                distance.argmax(),
                distance.shape
            )

            # Adaptive font sizing.
            radius = distance[y, x]

            for font_size in range(28, 11, -1):

                font = ImageFont.truetype(
                    "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
                    font_size
                )

                box = draw.textbbox(
                    (int(x), int(y)),
                    name,
                    font=font,
                    anchor="mm",
                    stroke_width=2
                )

                x0, y0, x1, y1 = box

                if (
                    x0 >= 0 and y0 >= 0
                    and x1 <= w and y1 <= h
                    and np.hypot(x1-x0, y1-y0) <= 2*radius
                ):
                    break

            else:
                continue

            draw.text(
                (int(x), int(y)),
                name,
                font=font,
                fill="black",
                anchor="mm",
                stroke_width=2,
                stroke_fill="white"
            )

            placed += 1

    return image, placed
