#!/usr/bin/env python-real

import os
import sys


def requireFile(filePath, modality):
    if not os.path.isfile(filePath):
        raise FileNotFoundError(f"{modality} input file not found: {filePath}")


def main(directoryPath, patientName, flairFile, t1File, t1cFile, t2File):
    from brats_toolkit.preprocessor import Preprocessor

    for modality, filePath in (
        ("FLAIR", flairFile),
        ("T1", t1File),
        ("T1c", t1cFile),
        ("T2", t2File),
    ):
        requireFile(filePath, modality)

    outputDirectory = os.path.join(directoryPath, "output")
    os.makedirs(outputDirectory, exist_ok=True)
    print(f"Preprocessing patient {patientName} into {outputDirectory}", flush=True)

    preprocessor = Preprocessor()
    preprocessor.single_preprocess(
        t1File=t1File,
        t1cFile=t1cFile,
        t2File=t2File,
        flaFile=flairFile,
        outputFolder=outputDirectory,
        mode="gpu",
        confirm=True,
        skipUpdate=False,
        gpuid="0",
    )


if __name__ == "__main__":
    if len(sys.argv) != 7:
        print(
            "Usage: BraTSPreprocessor <patient-directory> <patient-name> "
            "<flair> <t1> <t1c> <t2>",
            file=sys.stderr,
        )
        sys.exit(1)
    main(*sys.argv[1:])
