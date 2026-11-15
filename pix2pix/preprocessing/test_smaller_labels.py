from pathlib import Path
import xml.etree.ElementTree as ET
import re

source = Path("dataset/english_annotations")
destination = Path("dataset/english_annotations_small_TEST")

if destination.exists():
    raise SystemExit("Test folder already exists. Nothing overwritten.")

destination.mkdir()

files = sorted(source.glob("*.svg"))[:5]

for file in files:
    tree = ET.parse(file)
    root = tree.getroot()

    changed = 0

    for element in root.iter():
        if element.tag.split("}")[-1] != "text":
            continue

        style = element.get("style", "")

        if "font-size:" in style:
            style = re.sub(
                r"font-size:\s*[\d.]+px",
                "font-size: 12px",
                style
            )
            element.set("style", style)

        element.set("font-size", "12")
        changed += 1

    tree.write(
        destination / file.name,
        encoding="utf-8",
        xml_declaration=True
    )

    print(file.name, "text elements adjusted:", changed)

print("\nTEST SVG FILES CREATED:", destination)
print("Original SVGs unchanged.")
