from pathlib import Path
import re
import difflib

import cv2
import numpy as np
import pytesseract
from PIL import Image, ImageDraw, ImageFont

# Pix2Pix results
RESULTS_DIR = Path("results/cubicasa2k_pix2pix/test_latest/images")
OUTPUT_DIR = Path("results/cubicasa2k_pix2pix/cleaned")

# Room names the system is allowed to recognize
ROOM_LABELS = [
    "Bedroom",
    "Bathroom",
    "Kitchen",
    "Living Room",
    "Dining Area",
    "Entry",
    "Hallway",
    "Utility",
    "Office",
    "Study",
    "Garage",
    "Closet",
    "Laundry",
    "Balcony",
    "Terrace",
    "Outdoor Space",
    "Porch",
    "Pantry",
    "Restroom",
    "Storage",
    "Master Bedroom",
]

CONFIDENCE_THRESHOLD = 50
MATCH_THRESHOLD = 0.70


def normalize_text(text):
    return re.sub(r"[^a-z]", "", text.lower())


def recognize_room(crop):
    # Enlarge the generated text so OCR has a better chance
    enlarged = cv2.resize(
        crop, None, fx=4, fy=4,
        interpolation=cv2.INTER_CUBIC
    )

    # Convert the colored generated pixels into black text
    # on a white background for OCR
    _, binary = cv2.threshold(
        enlarged, 0, 255,
        cv2.THRESH_BINARY + cv2.THRESH_OTSU
    )

    binary = cv2.bitwise_not(binary)

    data = pytesseract.image_to_data(
        binary,
        config="--psm 7",
        output_type=pytesseract.Output.DICT
    )

    words = []
    confidences = []

    for word, confidence in zip(data["text"], data["conf"]):
        word = word.strip()

        try:
            confidence = float(confidence)
        except ValueError:
            continue

        if word and confidence >= 0:
            words.append(word)
            confidences.append(confidence)

    if not words:
        return "UNDEFINED"

    recognized_text = " ".join(words)
    average_confidence = sum(confidences) / len(confidences)

    normalized = normalize_text(recognized_text)

    best_label = "UNDEFINED"
    best_score = 0

    for label in ROOM_LABELS:
        score = difflib.SequenceMatcher(
            None,
            normalized,
            normalize_text(label)
        ).ratio()

        if score > best_score:
            best_score = score
            best_label = label

    if (
        average_confidence >= CONFIDENCE_THRESHOLD
        and best_score >= MATCH_THRESHOLD
    ):
        return best_label

    return "UNDEFINED"


def find_label_regions(fake_image):
    # Find the colored pixels produced by Pix2Pix.
    hsv = cv2.cvtColor(fake_image, cv2.COLOR_RGB2HSV)

    mask = cv2.inRange(
        hsv,
        np.array([0, 35, 60]),
        np.array([179, 255, 255])
    )

    # Connect nearby colored letters into text regions
    kernel = cv2.getStructuringElement(
        cv2.MORPH_RECT, (9, 3)
    )

    mask = cv2.morphologyEx(
        mask, cv2.MORPH_CLOSE, kernel
    )

    mask = cv2.dilate(
        mask,
        cv2.getStructuringElement(
            cv2.MORPH_RECT, (3, 3)
        ),
        iterations=1
    )

    contours, _ = cv2.findContours(
        mask,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )

    regions = []

    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        area = cv2.contourArea(contour)

        if w < 5 or h < 2 or area < 5:
            continue

        if w > fake_image.shape[1] * 0.4:
            continue

        if h > fake_image.shape[0] * 0.15:
            continue

        regions.append((x, y, w, h))

    return regions, mask


def get_font(size):
    font_paths = [
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/Library/Fonts/Arial.ttf",
    ]

    for path in font_paths:
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            pass

    return ImageFont.load_default()


def clean_prediction(fake_path):
    image_name = fake_path.name.replace("_fake_B.png", "")
    real_a_path = RESULTS_DIR / f"{image_name}_real_A.png"

    if not real_a_path.exists():
        print(f"Missing original input for {image_name}")
        return

    # Use the original blank floorplan as the background
    original = Image.open(real_a_path).convert("RGB")
    fake = np.array(
        Image.open(fake_path).convert("RGB")
    )

    regions, mask = find_label_regions(fake)

    draw = ImageDraw.Draw(original)
    font = get_font(8)

    print(f"\nProcessing {image_name}: {len(regions)} regions")

    for x, y, w, h in regions:
        # OCR only the generated text region
        crop = mask[y:y + h, x:x + w]

        label = recognize_room(crop)

        # Position the clean label at the detected text location
        center_x = x + w // 2
        center_y = y + h // 2

        text_box = draw.textbbox(
            (0, 0), label, font=font
        )

        text_w = text_box[2] - text_box[0]
        text_h = text_box[3] - text_box[1]

        # White background makes the text readable
        padding = 2

        draw.rectangle(
            [
                center_x - text_w // 2 - padding,
                center_y - text_h // 2 - padding,
                center_x + text_w // 2 + padding,
                center_y + text_h // 2 + padding,
            ],
            fill="white"
        )

        draw.text(
            (center_x, center_y),
            label,
            fill="black",
            font=font,
            anchor="mm"
        )

        print(f"  {label} at ({center_x}, {center_y})")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    output_path = OUTPUT_DIR / f"{image_name}_clean.png"
    original.save(output_path)

    print(f"Saved: {output_path}")


def main():
    if not RESULTS_DIR.exists():
        print(f"Results folder not found: {RESULTS_DIR}")
        return

    predictions = sorted(
        RESULTS_DIR.glob("*_fake_B.png")
    )

    if not predictions:
        print("No generated fake_B images found.")
        return

    print(f"Found {len(predictions)} generated predictions.")

    for fake_path in predictions:
        clean_prediction(fake_path)

    print("\nCleanup complete.")
    print(f"Cleaned images saved in: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
