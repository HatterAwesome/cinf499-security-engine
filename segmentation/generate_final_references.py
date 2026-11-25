from pathlib import Path
from PIL import Image
import numpy as np
import csv
import sys

from segmentation.individual_room_geometry import (
    make_individual_mask
)
from segmentation.render_labels import render_labels

output = Path("dataset/final_english_images")
output.mkdir(parents=True, exist_ok=True)

report = Path("dataset/reports/final_reference_report.csv")
report.parent.mkdir(parents=True, exist_ok=True)

stems = sorted(
    p.stem for p in Path("dataset/blank_images").glob("*.png")
)

if "--pilot" in sys.argv:
    stems = ["10465", "193", "20001"]

with report.open("w", newline="") as report_file:

    writer = csv.writer(report_file)

    writer.writerow([
        "floorplan",
        "translated_rooms",
        "labels_placed",
        "labels_skipped",
        "untranslated_or_undefined",
        "width",
        "height",
        "status"
    ])

    for index, stem in enumerate(stems, start=1):

        try:
            svg = Path("dataset/annotations") / f"{stem}_model.svg"

            with Image.open(f"dataset/blank_images/{stem}.png") as im:
                rgba = im.convert("RGBA")
                bg = Image.new("RGBA", rgba.size, "white")
                original = Image.alpha_composite(bg, rgba).convert("RGB")

            mask, labels = make_individual_mask(svg, *original.size)

            rgb = np.asarray(mask).astype(np.uint32)

            ids = (
                (rgb[:, :, 0] << 16)
                | (rgb[:, :, 1] << 8)
                | rgb[:, :, 2]
            )

            w, h = original.size
            scale = min(512 / w, 512 / h)

            nw = max(1, round(w * scale))
            nh = max(1, round(h * scale))

            placed = 0
            skipped = 0
            translated = 0
            result = original.copy()

            for room_id, label in labels.items():

                if label is None:
                    continue

                translated += 1

                binary = (ids == room_id).astype(np.uint8)

                resized = Image.fromarray(binary).resize(
                    (nw, nh),
                    Image.Resampling.NEAREST
                )

                canvas = Image.new("L", (512, 512), 0)

                canvas.paste(
                    resized,
                    ((512 - nw) // 2, (512 - nh) // 2)
                )

                candidate, count = render_labels(
                    result,
                    np.asarray(canvas),
                    {label: 1},
                    min_area=1000
                )

                if count == 1:
                    result = candidate
                    placed += 1
                else:
                    skipped += 1

            assert result.size == original.size

            destination = output / f"{stem}.png"
            result.save(destination)

            writer.writerow([
                stem,
                translated,
                placed,
                skipped,
                sum(label is None for label in labels.values()),
                w,
                h,
                "PASS"
            ])

            print(
                f"[{index}/{len(stems)}] {stem} | "
                f"Placed: {placed}/{translated} | "
                f"Skipped: {skipped} | PASS",
                flush=True
            )

        except Exception as error:

            writer.writerow([
                stem, "", "", "", "", "", "",
                f"ERROR: {error}"
            ])

            print(
                f"[{index}/{len(stems)}] {stem} | ERROR: {error}",
                flush=True
            )

        report_file.flush()

print("\nREFERENCE GENERATION FINISHED")
print("Images:", output)
print("Report:", report)
