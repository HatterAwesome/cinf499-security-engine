from pathlib import Path
import xml.etree.ElementTree as ET
from collections import Counter
from PIL import Image
import cairosvg
import random
import json
import io

SVG_DIR = Path("dataset/english_annotations")
BLANK_DIR = Path("dataset/blank_images")
OUTPUT = Path("pix2pix/datasets/cubicasa_room_masks_preview")

SIZE = 512
NS = "http://www.w3.org/2000/svg"

ET.register_namespace("", NS)

PALETTE = {
    "Bedroom": "#e6194b",
    "Bathroom": "#4363d8",
    "Living Room": "#3cb44b",
    "Kitchen": "#ffe119",
    "Entry": "#f58231",
    "Closet": "#911eb4",
    "Dining Room": "#46f0f0",
    "Garage": "#a9a9a9",
    "Laundry Room": "#f032e6",
    "Storage Room": "#808000",
    "Terrace": "#008080",
    "Balcony": "#fabebe",
    "Office": "#000075",
    "Hallway": "#9a6324",
    "Sauna": "#800000",
    "Technical Room": "#aaffc3",
    "Outdoor Area": "#bfef45",
    "Dressing Room": "#dcbeff",
    "Carport": "#469990",
    "Patio": "#ffd8b1",
}

def room_name(cls):
    parts = cls.split()

    if not parts or parts[0] != "Space":
        return None

    if len(parts) < 2:
        return None

    main = parts[1]

    mapping = {
        "Bedroom": "Bedroom",
        "Bath": "Bathroom",
        "LivingRoom": "Living Room",
        "Kitchen": "Kitchen",
        "Entry": "Entry",
        "DraughtLobby": "Entry",
        "Closet": "Closet",
        "Dining": "Dining Room",
        "Garage": "Garage",
        "Utility": "Laundry Room",
        "Storage": "Storage Room",
        "Office": "Office",
        "Hall": "Hallway",
        "Sauna": "Sauna",
        "TechnicalRoom": "Technical Room",
        "DressingRoom": "Dressing Room",
        "CarPort": "Carport",
    }

    if main == "Outdoor":
        for name in ["Terrace", "Balcony", "Patio"]:
            if name in parts:
                return name
        return "Outdoor Area"

    return mapping.get(main)


def is_hidden(elem):
    style = {}

    for item in elem.get("style", "").split(";"):
        if ":" in item:
            key, value = item.split(":", 1)
            style[key.strip()] = value.strip()

    display = style.get(
        "display", elem.get("display", "")
    )

    visibility = style.get(
        "visibility", elem.get("visibility", "")
    )

    opacity = style.get(
        "opacity", elem.get("opacity", "1")
    )

    return (
        display == "none"
        or visibility in ("hidden", "collapse")
        or opacity in ("0", "0.0", "0%")
    )


def make_mask(path, width, height):
    root = ET.parse(path).getroot()

    mask = ET.Element(f"{{{NS}}}svg", root.attrib)
    counts = Counter()

    def walk(source, destination):
        for child in source:
            if is_hidden(child):
                continue
            tag = child.tag.split("}")[-1]
            cls = child.get("class", "")

            if "Space" in cls.split():
                label = room_name(cls)

                group = ET.SubElement(
                    destination, f"{{{NS}}}g"
                )

                if child.get("transform"):
                    group.set(
                        "transform", child.get("transform")
                    )

                color = PALETTE.get(label, "#000000")

                for polygon in child:
                    if is_hidden(polygon):
                        continue
                    if polygon.tag.split("}")[-1] != "polygon":
                        continue

                    attrs = {
                        "points": polygon.get("points", ""),
                        "fill": color,
                        "stroke": "none"
                    }

                    if polygon.get("transform"):
                        attrs["transform"] = polygon.get("transform")

                    ET.SubElement(
                        group, f"{{{NS}}}polygon", attrs
                    )

                    if label:
                        counts[label] += 1

            elif tag in ("g", "svg"):
                attrs = {}

                for key in [
                    "transform", "viewBox", "width",
                    "height", "x", "y", "preserveAspectRatio"
                ]:
                    if child.get(key):
                        attrs[key] = child.get(key)

                group = ET.SubElement(
                    destination, f"{{{NS}}}{tag}", attrs
                )

                walk(child, group)

    walk(root, mask)

    png = cairosvg.svg2png(
        bytestring=ET.tostring(mask),
        output_width=width,
        output_height=height
    )

    rgba = Image.open(io.BytesIO(png)).convert("RGBA")
    background = Image.new("RGBA", rgba.size, "black")

    return Image.alpha_composite(
        background, rgba
    ).convert("RGB"), counts

def letterbox(image, background, resample):
    w, h = image.size
    scale = min(SIZE / w, SIZE / h)

    nw = max(1, round(w * scale))
    nh = max(1, round(h * scale))

    resized = image.resize((nw, nh), resample)

    canvas = Image.new("RGB", (SIZE, SIZE), background)

    canvas.paste(
        resized,
        ((SIZE - nw) // 2, (SIZE - nh) // 2)
    )

    return canvas

OUTPUT.mkdir(parents=True, exist_ok=True)

files = [
    p for p in sorted(SVG_DIR.glob("*.svg"))
    if (BLANK_DIR / (p.stem.removesuffix("_model") + ".png")).exists()
]

random.Random(42).shuffle(files)

total = Counter()
saved = 0

for path in files:
    if saved >= 20:
        break

    blank_path = BLANK_DIR / (path.stem.removesuffix("_model") + ".png")

    with Image.open(blank_path) as im:
        rgba = im.convert("RGBA")
        bg = Image.new("RGBA", rgba.size, "white")
        blank = Image.alpha_composite(bg, rgba).convert("RGB")

    mask, counts = make_mask(path, *blank.size)

    if not counts:
        continue

    a = letterbox(
        blank, "white", Image.Resampling.LANCZOS
    )

    b = letterbox(
        mask, "black", Image.Resampling.NEAREST
    )

    pair = Image.new("RGB", (SIZE * 2, SIZE))
    pair.paste(a, (0, 0))
    pair.paste(b, (SIZE, 0))

    pair.save(OUTPUT / f"{path.stem.removesuffix('_model')}.png")

    total.update(counts)
    saved += 1

    print(f"{saved}/20: {path.stem} | {dict(counts)}")

with open(OUTPUT / "palette.json", "w") as f:
    json.dump(PALETTE, f, indent=2)

print("\nPREVIEW COMPLETE")
print("Matching source files:", len(files))
print("Generated pairs:", saved)
print("Room counts:", dict(total))
print("Output:", OUTPUT)
