from pathlib import Path
from PIL import Image
import numpy as np
import csv

ROOT = Path("pix2pix/datasets/cubicasa_v4_pilot")
REPORT = Path("reports/v4_pilot_quality_check.csv")
REPORT.parent.mkdir(parents=True, exist_ok=True)

TILE = 512
BORDER = 24

rows = []

for split in ["train", "val", "test"]:
    folder = ROOT / split
    files = sorted(folder.glob("*.png"))

    passed = 0
    flagged = 0
    errors = 0

    for path in files:
        try:
            with Image.open(path) as im:
                img = np.asarray(im.convert("RGB"))

            if img.shape != (TILE, TILE * 2, 3):
                rows.append([split, path.name, "WRONG_SIZE", 0, 0])
                errors += 1
                continue

            A = img[:, :TILE]
            B = img[:, TILE:]

            # Identify differences between blank and labeled plans.
            difference = np.max(
                np.abs(A.astype(np.int16) - B.astype(np.int16)),
                axis=2
            ) > 35

            changed = int(difference.sum())

            # Check whether changed pixels touch crop boundaries.
            border_mask = np.zeros((TILE, TILE), dtype=bool)
            border_mask[:BORDER, :] = True
            border_mask[-BORDER:, :] = True
            border_mask[:, :BORDER] = True
            border_mask[:, -BORDER:] = True

            edge_pixels = int((difference & border_mask).sum())

            if changed == 0:
                status = "NO_LABEL_DIFFERENCE"
                flagged += 1
            elif edge_pixels > 0:
                status = "CHECK_EDGE_LABEL"
                flagged += 1
            else:
                status = "PASS"
                passed += 1

            rows.append([
                split,
                path.name,
                status,
                changed,
                edge_pixels
            ])

        except Exception as e:
            rows.append([split, path.name, "ERROR", 0, str(e)])
            errors += 1

    print(
        f"{split}: {len(files)} checked | "
        f"{passed} passed | "
        f"{flagged} flagged | "
        f"{errors} errors"
    )

with REPORT.open("w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow([
        "split",
        "filename",
        "status",
        "changed_pixels",
        "edge_changed_pixels"
    ])
    writer.writerows(rows)

print("\nReport saved:", REPORT)
print("Original dataset unchanged.")
