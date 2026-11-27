"""Architectural room boundary refinement and label placement."""

import cv2
import numpy as np

from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage
from segmentation.fonts import load_label_font



def refine(original, prediction, classes, ratio=0.02):
    names = {idx: name for name, idx in classes.items()}

    w, h = original.size

    scale = min(512 / w, 512 / h)

    nw = max(1, round(w * scale))
    nh = max(1, round(h * scale))

    left = (512 - nw) // 2
    top = (512 - nh) // 2

    prediction = Image.fromarray(prediction)

    prediction = prediction.crop(
        (left, top, left + nw, top + nh)
    )

    prediction = np.asarray(
        prediction.resize(
            (w, h),
            Image.Resampling.NEAREST
        )
    )

    gray = np.asarray(original.convert("L"))

    walls = (gray < 180).astype(np.uint8) * 255

    gap = max(3, round(max(w, h) * ratio))

    if gap % 2 == 0:
        gap += 1

    kernel = cv2.getStructuringElement(
        cv2.MORPH_RECT, (gap, gap)
    )

    closed = cv2.morphologyEx(
        walls, cv2.MORPH_CLOSE, kernel
    )

    count, regions, stats, _ = (
        cv2.connectedComponentsWithStats(
            (closed == 0).astype(np.uint8),
            connectivity=4
        )
    )

    exterior = set(np.concatenate([
        regions[0, :],
        regions[-1, :],
        regions[:, 0],
        regions[:, -1]
    ]))

    result = original.copy()
    draw = ImageDraw.Draw(result)

    placed = 0
    skipped = 0

    minimum_area = max(
        12000, int(w * h * 0.003)
    )

    for region_id in range(1, count):

        if region_id in exterior:
            continue

        area = stats[region_id, cv2.CC_STAT_AREA]

        if area < minimum_area:
            continue

        region = regions == region_id

        votes = np.bincount(
            prediction[region],
            minlength=len(classes)
        )

        # Select the dominant non-background class.
        votes[0] = 0

        winner = int(votes.argmax())

        agreement = votes[winner] / area

        # Reject regions without sufficient agreement.
        if winner == 0 or agreement < 0.50:
            skipped += 1
            continue

        name = names[winner]

        distance = ndimage.distance_transform_edt(
            np.pad(region, 1, constant_values=False)
        )[1:-1, 1:-1]

        y, x = np.unravel_index(
            distance.argmax(), distance.shape
        )

        for size in range(28, 11, -1):

            font = load_label_font(size)

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
                and x1 > x0 and y1 > y0
                and region[y0:y1, x0:x1].all()
            ):
                break

        else:
            skipped += 1
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

        print(
            f"  {name}: "
            f"{agreement:.1%} pixel agreement"
        )

    return result, placed, skipped
