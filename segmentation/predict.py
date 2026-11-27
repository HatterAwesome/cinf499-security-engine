from pathlib import Path

import numpy as np
import torch
from PIL import Image

from segmentation.model import UNet


SIZE = 512


def preprocess_image(image_path):

    with Image.open(image_path) as source:
        rgba = source.convert("RGBA")

    background = Image.new("RGBA", rgba.size, "white")
    original = Image.alpha_composite(
        background, rgba
    ).convert("RGB")

    w, h = original.size

    scale = min(SIZE / w, SIZE / h)

    nw = max(1, round(w * scale))
    nh = max(1, round(h * scale))

    resized = original.resize(
        (nw, nh),
        Image.Resampling.LANCZOS
    )

    canvas = Image.new(
        "RGB", (SIZE, SIZE), "white"
    )

    left = (SIZE - nw) // 2
    top = (SIZE - nh) // 2

    canvas.paste(resized, (left, top))

    array = np.array(canvas)

    tensor = torch.from_numpy(array).float()
    tensor = tensor.permute(2, 0, 1) / 255.0

    return original, tensor.unsqueeze(0)


def load_model(checkpoint_path):

    device = torch.device(
        "mps" if torch.backends.mps.is_available()
        else "cpu"
    )

    model = UNet().to(device)

    model.load_state_dict(
        torch.load(
            checkpoint_path,
            map_location="cpu",
            weights_only=True
        )
    )

    model.eval()

    return model, device


def predict_mask(model, device, tensor):

    with torch.inference_mode():

        logits = model(tensor.to(device))

        prediction = logits.argmax(dim=1)

    return prediction[0].cpu().numpy().astype(np.uint8)


def main():

    import argparse
    import json

    from segmentation.render_labels import (
        clean_mask,
        render_labels
    )

    parser = argparse.ArgumentParser(
        description="AI floor-plan room labeling"
    )

    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)

    parser.add_argument(
        "--baseline",
        action="store_true",
        help="Use original segmentation label placement"
    )

    parser.add_argument(
        "--checkpoint",
        default="segmentation/checkpoints/full_best.pth"
    )

    args = parser.parse_args()

    classes = json.loads(
        Path(
            "segmentation/datasets/cubicasa/classes.json"
        ).read_text()
    )

    model, device = load_model(args.checkpoint)

    original, tensor = preprocess_image(args.input)

    prediction = predict_mask(
        model, device, tensor
    )

    cleaned = clean_mask(prediction)

    if args.baseline:
        labeled, count = render_labels(
            original, cleaned, classes
        )
    else:
        from segmentation.room_refinement import refine

        labeled, count, skipped = refine(
            original, cleaned, classes
        )

        print("Regions skipped:", skipped)

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)

    labeled.save(output)

    print("Device:", device)
    print("Labels placed:", count)
    print("Saved:", output)


if __name__ == "__main__":
    main()
