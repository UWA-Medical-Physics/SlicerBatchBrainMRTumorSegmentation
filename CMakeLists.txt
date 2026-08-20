cmake_minimum_required(VERSION 3.16.3...3.19.7 FATAL_ERROR)

project(BatchBrainMRTumorSegmentation)

#-----------------------------------------------------------------------------
# Extension meta-information
set(EXTENSION_HOMEPAGE "https://github.com/UWA-Medical-Physics/SlicerBatchBrainMRTumorSegmentation#readme")
set(EXTENSION_CATEGORY "Segmentation")
set(EXTENSION_CONTRIBUTORS "Saima Safdar (The University of Western Australia)")
set(EXTENSION_DESCRIPTION "Automates BraTS Toolkit preprocessing, brain tumour segmentation, label fusion, and transformation of results back to the original MRI space for a cohort of patients.")
set(EXTENSION_ICONURL "https://raw.githubusercontent.com/UWA-Medical-Physics/SlicerBatchBrainMRTumorSegmentation/main/BatchBrainMRTumorSegmentation/Resources/Icons/BatchBrainMRTumorSegmentation.png")
set(EXTENSION_SCREENSHOTURLS "https://raw.githubusercontent.com/UWA-Medical-Physics/SlicerBatchBrainMRTumorSegmentation/main/Screenshot%20from%202024-02-06%2012-11-03.png")
set(EXTENSION_DEPENDS "NA") # Specified as a list or "NA" if no dependencies

#-----------------------------------------------------------------------------
# Extension dependencies
find_package(Slicer REQUIRED)
include(${Slicer_USE_FILE})
# The lightweight packaging environment used by ExtensionsIndex does not load
# this macro from UseSlicer.cmake, so include it explicitly.
include(SlicerMacroBuildScriptedCLI)

#-----------------------------------------------------------------------------
# Extension modules
add_subdirectory(BraTSPreprocessor)
add_subdirectory(BraTSSegmentor)
add_subdirectory(BraTSFusionator)
add_subdirectory(BatchBrainMRTumorSegmentation)
## NEXT_MODULE

#-----------------------------------------------------------------------------
include(${Slicer_EXTENSION_GENERATE_CONFIG})
include(${Slicer_EXTENSION_CPACK})
