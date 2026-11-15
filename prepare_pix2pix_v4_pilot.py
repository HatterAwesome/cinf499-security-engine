from pathlib import Path
from PIL import Image
import numpy as np
import random

blank_dir = Path("dataset/blank_images")
english_dir = Path("dataset/english_images_small_v4")
output = Path("pix2pix/datasets/cubicasa_v4_pilot")

if output.exists():
    raise SystemExit("STOP: Pilot dataset already exists. Nothing overwritten.")

for split in ["train", "val", "test"]:
    (output / split).mkdir(parents=True)

names = sorted(
    set(p.name for p in blank_dir.glob("*.png")) &
    set(p.name for p in english_dir.glob("*.png"))
)

random.Random(42).shuffle(names)

# Use 200 floor plans for the pilot.
names = names[:200]

train_end = int(len(names) * 0.8)
val_end = int(len(names) * 0.9)

splits = {
    "train": names[:train_end],
    "val": names[train_end:val_end],
    "test": names[val_end:]
}

tile_size = 512
border = 32

for split, filenames in splits.items():
    saved = 0
    rejected = 0

    for filename in filenames:
        with Image.open(blank_dir / filename) as im:
            a = im.convert("RGB")

        with Image.open(english_dir / filename) as im:
            b = im.convert("RGB")

        if a.size != b.size:
            print("SIZE MISMATCH:", filename)
            continue

        width, height = a.size

        for y in range(0, height - tile_size + 1, tile_size):
            for x in range(0, width - tile_size + 1, tile_size):

                a_tile = a.crop((x, y, x + tile_size, y + tile_size))
                b_tile = b.crop((x, y, x + tile_size, y + tile_size))

                aa = np.asarray(a_tile).astype(np.int16)
                bb = np.asarray(b_tile).astype(np.int16)

                changed = np.max(np.abs(aa - bb), axis=2) > 20

                if changed.sum() < 10:
                    rejected += 1
                    continue

                if (
                    changed[:border, :].any()
                    or changed[-border:, :].any()
                    or changed[:, :border].any()
                    or changed[:, -border:].any()
                ):
                    rejected += 1
                    continue

                pair = Image.new("RGB", (1024, 512), "white")
                pair.paste(a_tile, (0, 0))
                pair.paste(b_tile, (512, 0))

                stem = Path(filename).stem
                pair.save(
                    output / split / f"{stem}_{x}_{y}.png"
                )
                saved += 1

    print(f"{split}: {saved} saved, {rejected} rejected")

print("\nPILOT DATASET CREATED:", output)
print("Original files unchanged.")
