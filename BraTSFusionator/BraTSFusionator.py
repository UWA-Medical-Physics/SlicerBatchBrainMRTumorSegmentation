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


def main(directoryPath, patientName, modelsValue):
    from brats_toolkit.fusionator import Fusionator

    models = parseModels(modelsValue)
    sourceDirectory = os.path.join(directoryPath, "outputSegmentator")
    segmentationFiles = [os.path.join(sourceDirectory, f"{model}.nii.gz") for model in models]
    missingFiles = [filePath for filePath in segmentationFiles if not os.path.isfile(filePath)]
    if missingFiles:
        raise FileNotFoundError("Missing segmentation files: " + ", ".join(missingFiles))

    outputDirectory = os.path.join(directoryPath, "outputFusionator")
    os.makedirs(outputDirectory, exist_ok=True)
    print(f"Fusing {len(models)} segmentations for patient {patientName}", flush=True)

    fusionator = Fusionator(verbose=True)
    fusionator.fuse(
        segmentations=segmentationFiles,
        outputPath=os.path.join(outputDirectory, "mav.nii.gz"),
        method="mav",
        weights=None,
    )
    fusionator.fuse(
        segmentations=segmentationFiles,
        outputPath=os.path.join(outputDirectory, "simple.nii.gz"),
        method="simple",
        weights=None,
    )


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print(
            "Usage: BraTSFusionator <patient-directory> <patient-name> <models-json>",
            file=sys.stderr,
        )
        sys.exit(1)
    main(*sys.argv[1:])
