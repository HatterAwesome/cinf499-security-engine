from pathlib import Path

import cv2
import numpy as np

INPUT = Path("segmentation/examples/blank")
OUTPUT = Path("segmentation/experiments/room_refinement/detected_rooms")

OUTPUT.mkdir(parents=True, exist_ok=True)


def detect_rooms(image, gap):

    height, width = image.shape[:2]

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    walls = (gray < 180).astype(np.uint8) * 255

    kernel = cv2.getStructuringElement(
        cv2.MORPH_RECT, (gap, gap)
    )

    closed = cv2.morphologyEx(
        walls, cv2.MORPH_CLOSE, kernel
    )

    free_space = (closed == 0).astype(np.uint8)

    count, regions, stats, centers = (
        cv2.connectedComponentsWithStats(
            free_space, connectivity=4
        )
    )

    exterior = set(np.concatenate([
        regions[0, :],
        regions[-1, :],
        regions[:, 0],
        regions[:, -1]
    ]))

    minimum_area = max(
        500, int(height * width * 0.002)
    )

    overlay = image.copy()
    rng = np.random.default_rng(42)
    detected = 0

    for region_id in range(1, count):

        if region_id in exterior:
            continue

        area = stats[region_id, cv2.CC_STAT_AREA]

        if area < minimum_area:
            continue

        region = regions == region_id

        color = rng.integers(
            50, 240, size=3
        ).astype(np.uint8)

        overlay[region] = color
        detected += 1

    result = cv2.addWeighted(
        image, 0.60, overlay, 0.40, 0
    )

    return result, detected


for path in sorted(INPUT.glob("*.png")):

    image = cv2.imread(str(path))

    if image is None:
        print(path.stem, "READ ERROR")
        continue

    height, width = image.shape[:2]

    print(f"\nFloor plan: {path.stem}")

    for ratio in [0.01, 0.02, 0.03, 0.04]:

        gap = max(
            3, round(max(height, width) * ratio)
        )

        if gap % 2 == 0:
            gap += 1

        result, count = detect_rooms(image, gap)

        output = OUTPUT / f"{path.stem}_gap_{gap}.png"

        if not cv2.imwrite(str(output), result):
            raise RuntimeError(f"Could not save {output}")

        print(
            f"Gap: {gap:3d} | "
            f"Detected spaces: {count:3d}"
        )

print("\nRoom detection experiment complete.")
