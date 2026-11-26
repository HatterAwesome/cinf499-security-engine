# Floor Plan Semantic Segmentation

## Overview

This component implements a two-stage machine learning
pipeline for architectural floor plan analysis.

The first stage utilizes a trained U-Net model to
predict room classes. The second stage applies
post-processing and renders readable English room
labels onto the original floor plan.

This approach was developed following limitations
observed during the original Pix2Pix experiments.

## Development Environment

The model was developed and trained on macOS using
Apple Silicon and PyTorch MPS acceleration.

Recorded software versions:

| Dependency | Version |
|---|---|
| Python | 3.11.5 |
| PyTorch | 2.15.0 |
| NumPy | 2.4.6 |
| Pillow | 13.0.0 |
| SciPy | 1.17.1 |
| CairoSVG | 2.9.1 |

## Installation

Clone the repository:

```bash
git clone https://github.com/HatterAwesome/cinf499-security-engine.git
cd cinf499-security-engine
```

Create and activate a Python virtual environment:

```bash
python3.11 -m venv .venv
source .venv/bin/activate
```

Install the inference dependencies:

```bash
pip install torch numpy Pillow scipy
```

CairoSVG and its native Cairo dependencies are
additionally required for SVG-based dataset
preparation and reference generation.

The current label renderer utilizes a macOS Arial
Bold font path. Other operating systems require
an adjustment to the font configuration.

## Model Architecture

The segmentation model utilizes a U-Net architecture
with encoder and decoder layers, skip connections,
and pixel-level room classification.

| Configuration | Value |
|---|---|
| Input Resolution | 512 x 512 |
| Input Channels | 3 |
| Output Classes | 21 |
| Trainable Parameters | 1,944,389 |
| Training Epochs | 20 |
| Batch Size | 2 |
| Optimizer | Adam |
| Learning Rate | 0.001 |
| Loss Function | Weighted Cross-Entropy |
| Best Validation Epoch | 14 |
| Best Validation Foreground mIoU | 21.28% |

## Room Classification

The model includes the following classes:

- Background
- Bedroom
- Bathroom
- Living Room
- Kitchen
- Entry
- Closet
- Dining Room
- Garage
- Laundry Room
- Storage Room
- Terrace
- Balcony
- Office
- Hallway
- Sauna
- Technical Room
- Outdoor Area
- Dressing Room
- Carport
- Patio

Class definitions are stored in
datasets/cubicasa/classes.json.

## Trained Model

The trained model checkpoint is included at:

    segmentation/checkpoints/full_best.pth

The checkpoint was selected based on validation
foreground mean Intersection over Union (mIoU).

Retraining is not required to execute the current
prediction pipeline.

## Model Inference

Run the following command from the repository root:

```bash
python -m segmentation.predict \
  --input segmentation/examples/blank/10465.png \
  --output segmentation/results/demo_prediction.png \
  --checkpoint segmentation/checkpoints/full_best.pth
```

The prediction pipeline accepts a blank floor plan
image and does not require the original SVG annotations.

The output image retains the original dimensions
and uses the original floor plan as the base image.

The prediction pipeline utilizes MPS acceleration
when available and otherwise uses the CPU.

## Dataset Preparation

The dataset contains 2,000 architectural floor plans
from CubiCasa5k.

The dataset was divided into:

- 1,600 training floor plans
- 200 validation floor plans
- 200 testing floor plans

Room masks were generated using the original SVG
annotations. Images and masks were resized and
padded to a consistent input resolution.

Dataset split identifiers are preserved in:

    segmentation/datasets/dataset_splits.json

The complete training dataset is not included
in the repository.

Dataset reconstruction requires the original
CubiCasa annotations and prepared blank images.

## Reference Floor Plan Generation

A separate reference generation pipeline utilizes
existing SVG room geometry and Finnish-to-English
translations to produce labeled floor plans.

The translation dictionary is available at:

    dataset/final_translations.json

The reference generation report is available at:

    dataset/reports/final_reference_report.csv

Reference generation produced 2,000 floor plans
with 16,939 successfully placed English labels.

The reference label placement rate was 96.52%.

These results measure annotation-based label
placement rather than independent model accuracy.

## Source Files

| File | Description |
|---|---|
| model.py | U-Net model architecture |
| dataset.py | Dataset loading |
| prepare_dataset.py | Dataset and mask preparation |
| train.py | Pilot model training |
| train_full.py | Full model training |
| predict.py | Model inference |
| render_labels.py | Mask post-processing and label placement |
| room_geometry.py | SVG room geometry extraction |
| individual_room_geometry.py | Individual room mask generation |
| generate_final_references.py | English reference generation |

## Research Results

Training histories, experimental configurations,
prediction comparisons, and reference generation
results are preserved in the following directories:

- checkpoints/
- datasets/
- examples/
- experiments/
- results/

## Limitations

The current model produces readable English labels,
but room classification accuracy remains limited.

Observed limitations include:

- Incorrect room classifications
- Duplicate predicted room labels
- Missing labels within smaller rooms
- Label overlap with architectural fixtures
- Limited generalization to unseen floor plans
- Operating system-specific font configuration

Independent evaluation of the held-out testing
dataset remains pending.

## Future Development

Further development includes improving room
classification accuracy, refining label placement,
and integrating the prediction pipeline with the
Java Spring Boot access control application.

The long-term objective is to support architectural
floor plan analysis for physical access control
system planning.
