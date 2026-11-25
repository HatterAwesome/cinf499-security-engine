import json
import time
from pathlib import Path

import torch
import torch.nn as nn
from torch.utils.data import DataLoader

from segmentation.model import UNet
from segmentation.dataset import FloorplanDataset

torch.manual_seed(42)

ROOT = Path("segmentation/datasets/cubicasa")
CHECKPOINTS = Path("segmentation/checkpoints")

EPOCHS = 5
BATCH_SIZE = 2
LEARNING_RATE = 0.001
NUM_CLASSES = 21
IGNORE_INDEX = 255

device = torch.device(
    "mps" if torch.backends.mps.is_available() else "cpu"
)

config = json.loads(
    Path("segmentation/datasets/pilot_config.json").read_text()
)

train_dataset = FloorplanDataset(
    ROOT, "train", config["train"]
)

val_dataset = FloorplanDataset(
    ROOT, "val", config["val"]
)

train_loader = DataLoader(
    train_dataset,
    batch_size=BATCH_SIZE,
    shuffle=True,
    num_workers=0
)

val_loader = DataLoader(
    val_dataset,
    batch_size=BATCH_SIZE,
    shuffle=False,
    num_workers=0
)

model = UNet().to(device)

weights = torch.tensor(
    config["class_weights"],
    dtype=torch.float32,
    device=device
)

criterion = nn.CrossEntropyLoss(
    weight=weights,
    ignore_index=IGNORE_INDEX
)

optimizer = torch.optim.Adam(
    model.parameters(),
    lr=LEARNING_RATE
)

CHECKPOINTS.mkdir(parents=True, exist_ok=True)

print("Device:", device)
print("Training samples:", len(train_dataset))
print("Validation samples:", len(val_dataset))
print("Epochs:", EPOCHS)
print("Batch size:", BATCH_SIZE)
print("Learning rate:", LEARNING_RATE)
print("Training batches:", len(train_loader))
print("Validation batches:", len(val_loader))
print("PASS: Training initialization complete")


def train_epoch(epoch):
    model.train()

    total_loss = 0.0
    completed = 0
    start = time.time()

    for batch, (images, masks) in enumerate(
        train_loader, start=1
    ):
        images = images.to(device)
        masks = masks.to(device)

        if not (masks != IGNORE_INDEX).any().item():
            continue

        optimizer.zero_grad()

        predictions = model(images)
        loss = criterion(predictions, masks)

        if not torch.isfinite(loss).item():
            raise RuntimeError("Non-finite training loss")

        loss.backward()
        optimizer.step()

        total_loss += loss.item()
        completed += 1

        if batch == 1 or batch % 10 == 0:
            print(
                f"Epoch {epoch}/{EPOCHS} | "
                f"Batch {batch}/{len(train_loader)} | "
                f"Loss: {loss.item():.4f}",
                flush=True
            )

    if device.type == "mps":
        torch.mps.synchronize()

    elapsed = time.time() - start

    if completed == 0:
        raise RuntimeError("No valid training batches")

    average_loss = total_loss / completed

    return average_loss, elapsed


def calculate_iou(confusion):
    intersection = confusion.diag()

    union = (
        confusion.sum(dim=0)
        + confusion.sum(dim=1)
        - intersection
    )

    valid = union[1:] > 0

    if not valid.any():
        return 0.0

    iou = intersection[1:][valid] / union[1:][valid]

    return iou.mean().item()


@torch.no_grad()
def validate():
    model.eval()

    total_loss = 0.0
    completed = 0

    confusion = torch.zeros(
        NUM_CLASSES,
        NUM_CLASSES,
        dtype=torch.int64
    )

    for images, masks in val_loader:
        images = images.to(device)
        masks = masks.to(device)

        valid = masks != IGNORE_INDEX

        if not valid.any().item():
            continue

        logits = model(images)
        loss = criterion(logits, masks)

        if not torch.isfinite(loss).item():
            raise RuntimeError("Non-finite validation loss")

        predictions = logits.argmax(dim=1)

        actual = masks[valid].cpu()
        predicted = predictions[valid].cpu()

        indices = actual * NUM_CLASSES + predicted

        confusion += torch.bincount(
            indices,
            minlength=NUM_CLASSES ** 2
        ).reshape(NUM_CLASSES, NUM_CLASSES)

        total_loss += loss.item()
        completed += 1

    if completed == 0:
        raise RuntimeError("No valid validation batches")

    return total_loss / completed, calculate_iou(confusion)


if __name__ == "__main__":
    best_iou = -1.0
    history = []
    start = time.time()

    for epoch in range(1, EPOCHS + 1):

        train_loss, elapsed = train_epoch(epoch)
        val_loss, val_iou = validate()

        record = {
            "epoch": epoch,
            "train_loss": train_loss,
            "val_loss": val_loss,
            "foreground_miou": val_iou,
            "training_seconds": elapsed
        }

        history.append(record)

        print(
            f"\nEpoch {epoch}/{EPOCHS} complete | "
            f"Train loss: {train_loss:.4f} | "
            f"Val loss: {val_loss:.4f} | "
            f"Foreground mIoU: {val_iou:.4f} | "
            f"Time: {elapsed:.1f}s",
            flush=True
        )

        if val_iou > best_iou:
            best_iou = val_iou

            torch.save(
                model.state_dict(),
                CHECKPOINTS / "pilot_best.pth"
            )

            print("Saved best checkpoint", flush=True)

        torch.save(
            model.state_dict(),
            CHECKPOINTS / "pilot_latest.pth"
        )

        (CHECKPOINTS / "pilot_history.json").write_text(
            json.dumps(history, indent=2)
        )

    print("\nTRAINING COMPLETE")
    print("Best foreground mIoU:", best_iou)
    print("Total seconds:", round(time.time() - start, 2))
