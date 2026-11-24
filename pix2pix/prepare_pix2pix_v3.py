from pathlib import Path
from PIL import Image
import numpy as np
import shutil
import json

source = Path("datasets/cubicasa2k_highres")
destination = Path("datasets/cubicasa_label_safe_v3")

if destination.exists():
    raise SystemExit(
        "V3 dataset already exists. Nothing overwritten."
    )

destination.mkdir(parents=True)

summary = {}

for split in ["train", "val", "test"]:
    src = source / split
    dst = destination / split
    dst.mkdir()

    accepted = 0
    rejected = 0

    for file in sorted(src.glob("*.png")):
        with Image.open(file) as im:
            image = np.array(im.convert("RGB"))

        h, w = image.shape[:2]

        if w != 1024 or h != 512:
            rejected += 1
            continue

        a = image[:, :512]
        b = image[:, 512:]

        # Detect changes between the blank and labeled images.
        difference = np.max(
            np.abs(a.astype(np.int16) - b.astype(np.int16)),
            axis=2
        ) > 20

        # Reject pairs with substantial differences at crop edges,
        # where room labels may have been cut in half.
        border = np.zeros_like(difference)
        border[:16, :] = True
        border[-16:, :] = True
        border[:, :16] = True
        border[:, -16:] = True

        edge_changes = np.count_nonzero(difference & border)
        total_changes = np.count_nonzero(difference)

        if total_changes < 10:
            rejected += 1
            continue

        if edge_changes > max(30, total_changes * 0.10):
            rejected += 1
            continue

        shutil.copy2(file, dst / file.name)
        accepted += 1

    summary[split] = {
        "accepted": accepted,
        "rejected": rejected
    }

    print(f"{split}: {accepted} accepted, {rejected} rejected")

(destination / "summary.json").write_text(
    json.dumps(summary, indent=2)
)

print("\nV3 DATASET CREATED:", destination)
print("Original datasets unchanged.")
