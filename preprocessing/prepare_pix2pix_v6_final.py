from pathlib import Path
from PIL import Image
import numpy as np
import random
import json

BLANK = Path("dataset/blank_images")
ENGLISH = Path("dataset/english_images")
OUTPUT = Path("pix2pix/datasets/cubicasa_v6_final")

TILE = 512
STRIDE = 448
SEED = 42

rng = random.Random(SEED)

names = sorted(
    {p.name for p in BLANK.glob("*.png")}
    & {p.name for p in ENGLISH.glob("*.png")}
)

assert len(names) == 2000, "Expected 2000 pairs"

rng.shuffle(names)

splits = {
    "train": names[:1600],
    "val": names[1600:1800],
    "test": names[1800:]
}

def positions(length):
    if length <= TILE:
        return [0]

    points = list(range(0, length - TILE + 1, STRIDE))

    if points[-1] != length - TILE:
        points.append(length - TILE)

    return points

def load_rgb(path):
    with Image.open(path) as im:
        rgba = im.convert("RGBA")
        bg = Image.new("RGBA", rgba.size, "white")
        return Image.alpha_composite(bg, rgba).convert("RGB")

def pad_image(im):
    w, h = im.size
    canvas = Image.new(
        "RGB",
        (max(w, TILE), max(h, TILE)),
        "white"
    )
    canvas.paste(im, (0, 0))
    return canvas

report = {}

for split, files in splits.items():
    folder = OUTPUT / split
    folder.mkdir(parents=True, exist_ok=True)

    saved = 0
    represented = set()
    no_change = 0

    for index, name in enumerate(files, 1):

        a = load_rgb(BLANK / name)
        b = load_rgb(ENGLISH / name)

        assert a.size == b.size, name

        a = pad_image(a)
        b = pad_image(b)

        w, h = a.size
        stem = Path(name).stem

        positive = []
        negative = []

        for y in positions(h):
            for x in positions(w):

                box = (x, y, x + TILE, y + TILE)

                aa = np.asarray(
                    a.crop(box), dtype=np.int16
                )

                bb = np.asarray(
                    b.crop(box), dtype=np.int16
                )

                changed = np.count_nonzero(
                    np.max(np.abs(aa - bb), axis=2) > 20
                )

                if changed >= 10:
                    positive.append((x, y))
                else:
                    negative.append((x, y))

        if not positive:
            no_change += 1

        if split == "train":
            selected = positive + rng.sample(
                negative,
                min(len(negative), max(1, len(positive) // 4))
            )
        else:
            selected = positive + negative

        for x, y in selected:

            box = (x, y, x + TILE, y + TILE)

            pair = Image.new("RGB", (TILE * 2, TILE))

            pair.paste(a.crop(box), (0, 0))
            pair.paste(b.crop(box), (TILE, 0))

            path = folder / f"{stem}_{x}_{y}.png"

            pair.save(path, compress_level=1)

            saved += 1
            represented.add(stem)

        if index % 50 == 0 or index == len(files):
            print(
                f"{split}: {index}/{len(files)} plans | "
                f"{saved} tiles",
                flush=True
            )

    report[split] = {
        "source_plans": len(files),
        "represented_plans": len(represented),
        "saved_tiles": saved,
        "plans_without_detected_changes": no_change
    }

    assert len(represented) == len(files)

with open(OUTPUT / "dataset_report.json", "w") as f:
    json.dump(report, f, indent=2)

with open(OUTPUT / "dataset_splits.json", "w") as f:
    json.dump(splits, f, indent=2)

print("\nFINAL DATASET REPORT")
print(json.dumps(report, indent=2))
print("\nPASS: All 2000 floor plans represented.")
