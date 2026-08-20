# Batch Brain MRI Tumor Segmentation

Batch Brain MRI Tumor Segmentation is a 3D Slicer extension that automates the
[BraTS Toolkit](https://github.com/neuronflow/BraTS-Toolkit) workflow for a
cohort of patients. It preprocesses four MRI modalities, runs one or more brain
tumour segmentation models, fuses their results, and transforms the consensus
segmentations back to each patient's original T1 MRI space.

![Batch Brain MRI Tumor Segmentation interface](Screenshot%20from%202024-02-06%2012-11-03.png)

## Modules

- **Batch Brain MRI Tumor Segmentation** provides the Slicer user interface and
  coordinates processing of all patient directories in a cohort.
- **BraTS Preprocessor** is a scripted CLI wrapper around the BraTS Toolkit
  preprocessing stage.
- **BraTS Segmentor** is a scripted CLI wrapper that runs the selected BraTS
  neural-network models.
- **BraTS Fusionator** is a scripted CLI wrapper that creates majority-voting
  and iterative SIMPLE consensus segmentations.

The three CLI scripts are installed with the extension. The batch module runs
them using the external Python executable selected by the user, so the large
BraTS dependencies remain outside Slicer's Python environment.

## Requirements

- Linux (the current workflow has been tested on Ubuntu 20.04)
- An NVIDIA GPU and current NVIDIA driver
- [Docker Engine](https://docs.docker.com/engine/install/)
- [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html)
- A Python environment in which `BraTS-Toolkit` can be installed

Docker must be usable by the current user without `sudo`; see Docker's
[Linux post-installation instructions](https://docs.docker.com/engine/install/linux-postinstall/#manage-docker-as-a-non-root-user).
Verify the GPU container setup before using the extension:

```console
docker run --rm --runtime=nvidia --gpus all ubuntu nvidia-smi
```

## Input layout

Choose a data directory containing one subdirectory per patient. Patient
directory names must contain `APT` followed by a numeric identifier. Each
patient directory must contain NIfTI files for all four modalities:

- T1-weighted MRI (`*t1.nii.gz`)
- contrast-enhanced T1-weighted MRI (`*t1c.nii.gz`)
- T2-weighted MRI (`*t2.nii.gz`)
- T2 FLAIR MRI (`*fla*.nii.gz`)

## Tutorial

1. Install the extension and restart 3D Slicer.
2. Open **Segmentation > Batch Brain MRI Tumor Segmentation**.
3. Set **Path to external Python** to the Python executable for the environment
   that should contain BraTS Toolkit. When processing starts, the extension
   checks this environment and, if needed, runs
   `python -m pip install BraTS-Toolkit`. This is an explicit network operation
   initiated by clicking **Apply**.
4. Set **Path to data directory** to the cohort directory described above.
5. Set **Patient ID** to the zero-based patient index at which processing should
   begin. Use `0` to process the full cohort.
6. Select one or more neural-network models.
7. Click **Apply** and monitor progress in the module.

For every patient, intermediate results are written to `output`,
`outputSegmentator`, and `outputFusionator`. Final transformed label maps are
written to `outputFinal`. A `patients_id.csv` file in the cohort directory
records completion status.

## Third-party downloads and privacy

The extension does not upload patient data or telemetry. Clicking **Apply** may
download the BraTS Toolkit Python package, container images, and model files
from the upstream BraTS Toolkit services. Review the
[BraTS Toolkit documentation](https://github.com/neuronflow/BraTS-Toolkit)
and its model terms before processing data.

## Publication

No publication describing this Slicer extension is available yet. Please cite
the upstream BraTS Toolkit and the publications for the segmentation models you
use.

## License

This extension is distributed under the
[BSD 3-Clause License](LICENSE). Third-party packages, container images, and
models retain their own licenses and terms.

## Support

Please use the repository's
[issue tracker](https://github.com/UWA-Medical-Physics/SlicerBatchBrainMRTumorSegmentation/issues)
for bug reports and feature requests.
