cmake_minimum_required(VERSION 3.16.3...3.19.7 FATAL_ERROR)

project(BatchBrainMRTumorSegmentation)

#-----------------------------------------------------------------------------
# Extension meta-information
set(EXTENSION_HOMEPAGE "https://github.com/UWA-Medical-Physics/SlicerBatchBrainMRTumorSegmentation#readme")
set(EXTENSION_CATEGORY "Segmentation")
set(EXTENSION_CONTRIBUTORS "Saima Safdar (The University of Western Australia)")
set(EXTENSION_DESCRIPTION "Supports segmentation of brain tumor for a cohort at once without any human intervention.")
set(EXTENSION_ICONURL "https://raw.githubusercontent.com/UWA-Medical-Physics/SlicerBatchBrainMRTumorSegmentation/main/BatchBrainMRTumorSegmentation.png")
set(EXTENSION_SCREENSHOTURLS "https://raw.githubusercontent.com/UWA-Medical-Physics/SlicerBatchBrainMRTumorSegmentation/main/Screenshot%20from%202024-02-06%2012-11-03.png")
set(EXTENSION_DEPENDS "NA") # Specified as a list or "NA" if no dependencies

#-----------------------------------------------------------------------------
# Extension dependencies
find_package(Slicer REQUIRED)
include(${Slicer_USE_FILE})

#-----------------------------------------------------------------------------
# Extension modules
add_subdirectory(BatchBrainMRTumorSegmentation)
## NEXT_MODULE

#-----------------------------------------------------------------------------
include(${Slicer_EXTENSION_GENERATE_CONFIG})
include(${Slicer_EXTENSION_CPACK})
