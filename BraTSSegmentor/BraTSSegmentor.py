#!/usr/bin/env python-real

import ast
import json
import os
import sys


def parseModels(modelsValue):
    try:
        models = json.loads(modelsValue)
    except json.JSONDecodeError:
        models = ast.literal_eval(modelsValue)
    if not isinstance(models, list) or not models or not all(isinstance(model, str) for model in models):
        raise ValueError("Models must be a non-empty JSON list of model identifiers.")
    return models


def requireFile(filePath, modality):
    if not os.path.isfile(filePath):
        raise FileNotFoundError(f"Preprocessed {modality} file not found: {filePath}")


def main(directoryPath, patientName, modelsValue):
    from brats_toolkit.segmentor import Segmentor

    models = parseModels(modelsValue)
    inputDirectory = os.path.join(directoryPath, "output", "hdbet_brats-space")
    inputs = {
        "t1": os.path.join(inputDirectory, "output_hdbet_brats_t1.nii.gz"),
        "t1c": os.path.join(inputDirectory, "output_hdbet_brats_t1c.nii.gz"),
        "t2": os.path.join(inputDirectory, "output_hdbet_brats_t2.nii.gz"),
        "fla": os.path.join(inputDirectory, "output_hdbet_brats_fla.nii.gz"),
    }
    for modality, filePath in inputs.items():
        requireFile(filePath, modality)

    outputDirectory = os.path.join(directoryPath, "outputSegmentator")
    os.makedirs(outputDirectory, exist_ok=True)
    print(f"Segmenting patient {patientName} with {len(models)} model(s)", flush=True)

    segmentor = Segmentor(verbose=True)
    failures = []
    for model in models:
        outputFile = os.path.join(outputDirectory, f"{model}.nii.gz")
        try:
            segmentor.segment(outputPath=outputFile, cid=model, **inputs)
        except Exception as exc:
            failures.append(f"{model}: {exc}")
    if failures:
        raise RuntimeError("Segmentation failed for " + "; ".join(failures))


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print(
            "Usage: BraTSSegmentor <patient-directory> <patient-name> <models-json>",
            file=sys.stderr,
        )
        sys.exit(1)
    main(*sys.argv[1:])
