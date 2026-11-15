from pathlib import Path
from PIL import Image
import xml.etree.ElementTree as ET
import cairosvg
import re
import io
import json

source = Path("dataset/english_annotations")
blank_dir = Path("dataset/blank_images")

svg_dir = Path("dataset/english_annotations_small_v4")
png_dir = Path("dataset/english_images_small_v4")
report = Path("dataset/small_labels_v4_report.json")

if svg_dir.exists() or png_dir.exists() or report.exists():
    raise SystemExit(
        "STOP: V4 output already exists. Nothing overwritten."
    )

svg_dir.mkdir()
png_dir.mkdir()

files = sorted(source.glob("*.svg"))
results = {
    "total": len(files),
    "completed": 0,
    "skipped": 0,
    "errors": []
}

for index, file in enumerate(files, 1):
    try:
        tree = ET.parse(file)
        root = tree.getroot()

        for element in root.iter():
            if element.tag.split("}")[-1] != "text":
                continue

            style = element.get("style", "")

            # Reduce CSS-defined font sizes.
            style = re.sub(
                r"font-size:\s*[\d.]+(?:px)?",
                "font-size: 12px",
                style
            )

            element.set("style", style)
            element.set("font-size", "12")

        svg_output = svg_dir / file.name

        tree.write(
            svg_output,
            encoding="utf-8",
            xml_declaration=True
        )

        name = file.stem.replace("_model", "") + ".png"
        blank_file = blank_dir / name

        if not blank_file.exists():
            results["skipped"] += 1
            results["errors"].append(
                f"{file.name}: matching blank PNG missing"
            )
            continue

        with Image.open(blank_file) as blank:
            width, height = blank.size

        png_bytes = cairosvg.svg2png(
            url=str(svg_output),
            output_width=width,
            output_height=height
        )

        with Image.open(io.BytesIO(png_bytes)) as im:
            rgba = im.convert("RGBA")

            white = Image.new(
                "RGBA",
                rgba.size,
                (255, 255, 255, 255)
            )

            white.alpha_composite(rgba)
            labeled = white.convert("RGB")

        labeled.save(png_dir / name)

        results["completed"] += 1

        if index % 100 == 0:
            print(
                f"Processed {index}/{len(files)} "
                f"| Completed: {results['completed']}"
            )

    except Exception as error:
        results["skipped"] += 1
        results["errors"].append(
            f"{file.name}: {error}"
        )

report.write_text(json.dumps(results, indent=2))

print("\n===== V4 COMPLETE =====")
print("Total SVG files:", results["total"])
print("Completed:", results["completed"])
print("Skipped/errors:", results["skipped"])
print("New SVG folder:", svg_dir)
print("New PNG folder:", png_dir)
print("Original files unchanged.")
