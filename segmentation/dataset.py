from pathlib import Path

import numpy as np
import torch
from PIL import Image
from torch.utils.data import Dataset


class FloorplanDataset(Dataset):

    def __init__(self, root, split, filenames):
        self.root = Path(root) / split
        self.filenames = filenames

    def __len__(self):
        return len(self.filenames)

    def __getitem__(self, index):
        filename = self.filenames[index]

        image_path = self.root / "images" / filename
        mask_path = self.root / "masks" / filename

        with Image.open(image_path) as im:
            image = np.array(im.convert("RGB"))

        with Image.open(mask_path) as im:
            mask = np.array(im)

        image = torch.from_numpy(image).float()
        image = image.permute(2, 0, 1) / 255.0

        mask = torch.from_numpy(mask).long()

        return image, mask
