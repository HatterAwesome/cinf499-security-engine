from pathlib import Path
from PIL import Image
import numpy as np
import shutil
import json

source = Path("datasets/cubicasa_label_safe_v3")
destination = Path("datasets/cubicasa_label_safe_v3_fixed")

if destination.exists():
    raise SystemExit("STOP: Fixed dataset already exists. Nothing overwritten.")

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

        if image.shape[:2] != (512, 1024):
            rejected += 1
            continue

        a = image[:, :512]
        b = image[:, 512:]

        # Find pixels changed by the English labels.
        diff = np.max(
            np.abs(a.astype(np.int16) - b.astype(np.int16)),
            axis=2
        ) > 20

        # Reject tiles with label-like differences near any edge.
        margin = 48

        if (
            diff[:margin, :].any()
            or diff[-margin:, :].any()
            or diff[:, :margin].any()
            or diff[:, -margin:].any()
        ):
            rejected += 1
            continue

        if np.count_nonzero(diff) < 10:
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

print("\nFIXED DATASET CREATED:", destination)
print("Original datasets and checkpoints unchanged.")
