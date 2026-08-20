import os
import csv
import json
import logging
import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *
from slicer.util import VTKObservationMixin

#
# Batch brain MRI tumor segmentation
#

class BatchBrainMRTumorSegmentation(ScriptedLoadableModule):
  """Uses ScriptedLoadableModule base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "Batch Brain MRI Tumor Segmentation"
    self.parent.categories = ["Segmentation"]
    self.parent.dependencies = ["BraTSPreprocessor", "BraTSSegmentor", "BraTSFusionator"]
    self.parent.contributors = ["Saima Safdar (The University of Western Australia)"]
    self.parent.helpText = """Automates BraTS Toolkit preprocessing, segmentation, label fusion, and transformation of results back to the original MRI space for a cohort of patients.
Clicking Apply may install BraTS-Toolkit into the selected external Python environment and download upstream containers and model files.
See the <a href="https://github.com/UWA-Medical-Physics/SlicerBatchBrainMRTumorSegmentation#readme">module documentation</a> for requirements and a tutorial.
"""
    self.parent.acknowledgementText = "This work was developed at The University of Western Australia."

#
# BatchBrainMRTumorSegmentationWidget
#

class BatchBrainMRTumorSegmentationWidget(ScriptedLoadableModuleWidget, VTKObservationMixin):
  """Uses ScriptedLoadableModuleWidget base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def __init__(self, parent=None):
    """
    Called when the user opens the module the first time and the widget is initialized.
    """
    ScriptedLoadableModuleWidget.__init__(self, parent)
    VTKObservationMixin.__init__(self)  # needed for parameter node observation
    self.logic = None
    self._parameterNode = None
    self._updatingGUIFromParameterNode = False
    self.logCallback = None

  def setup(self):
    """
    Called when the user opens the module the first time and the widget is initialized.
    """
    ScriptedLoadableModuleWidget.setup(self)

    # Load widget from .ui file (created by Qt Designer).
    # Additional widgets can be instantiated manually and added to self.layout.
    uiWidget = slicer.util.loadUI(self.resourcePath('UI/BatchBrainMRTumorSegmentation.ui'))
    self.layout.addWidget(uiWidget)
    self.ui = slicer.util.childWidgetVariables(uiWidget)

    # Set scene in MRML widgets. Make sure that in Qt designer the top-level qMRMLWidget's
    # "mrmlSceneChanged(vtkMRMLScene*)" signal in is connected to each MRML widget's.
    # "setMRMLScene(vtkMRMLScene*)" slot.
    uiWidget.setMRMLScene(slicer.mrmlScene)

    # Create logic class. Logic implements all computations that should be possible to run
    # in batch mode, without a graphical user interface.
    self.logic = BatchBrainMRTumorSegmentationLogic()
    self.logic.logCallback = self.addLog
    # Connections

    # These connections ensure that we update parameter node when scene is closed
    self.addObserver(slicer.mrmlScene, slicer.mrmlScene.StartCloseEvent, self.onSceneStartClose)
    self.addObserver(slicer.mrmlScene, slicer.mrmlScene.EndCloseEvent, self.onSceneEndClose)

    # These connections ensure that whenever user changes some settings on the GUI, that is saved in the MRML scene
    # (in the selected parameter node).
    #self.ui.inputSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.updateParameterNodeFromGUI)
    #self.ui.outputSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.updateParameterNodeFromGUI)
    
    
   
    
    
    # self.layout = self.parent.layout()
    # self.textbox = qt.QTextEdit()
    # self.layout.addWidget(self.textbox)

    # Buttons
    self.ui.applyButton.connect('clicked(bool)', self.onApplyButton)

    # Make sure parameter node is initialized (needed for module reload)
    self.initializeParameterNode()

  def cleanup(self):
    """
    Called when the application closes and the module widget is destroyed.
    """
    self.removeObservers()

  def enter(self):
    """
    Called each time the user opens this module.
    """
    # Make sure parameter node exists and observed
    self.initializeParameterNode()

  def exit(self):
    """
    Called each time the user opens a different module.
    """
    # Do not react to parameter node changes (GUI wlil be updated when the user enters into the module)
    self.removeObserver(self._parameterNode, vtk.vtkCommand.ModifiedEvent, self.updateGUIFromParameterNode)

  def onSceneStartClose(self, caller, event):
    """
    Called just before the scene is closed.
    """
    # Parameter node will be reset, do not use it anymore
    self.setParameterNode(None)

  def onSceneEndClose(self, caller, event):
    """
    Called just after the scene is closed.
    """
    # If this module is shown while the scene is closed then recreate a new parameter node immediately
    if self.parent.isEntered:
      self.initializeParameterNode()

  def initializeParameterNode(self):
    """
    Ensure parameter node exists and observed.
    """
    # Parameter node stores all user choices in parameter values, node selections, etc.
    # so that when the scene is saved and reloaded, these settings are restored.

    self.setParameterNode(self.logic.getParameterNode())

    # Select default input nodes if nothing is selected yet to save a few clicks for the user
    if not self._parameterNode.GetNodeReference("InputVolume"):
      firstVolumeNode = slicer.mrmlScene.GetFirstNodeByClass("vtkMRMLScalarVolumeNode")
      if firstVolumeNode:
        self._parameterNode.SetNodeReferenceID("InputVolume", firstVolumeNode.GetID())

  def setParameterNode(self, inputParameterNode):
    """
    Set and observe parameter node.
    Observation is needed because when the parameter node is changed then the GUI must be updated immediately.
    """

    if inputParameterNode:
      self.logic.setDefaultParameters(inputParameterNode)

    # Unobserve previously selected parameter node and add an observer to the newly selected.
    # Changes of parameter node are observed so that whenever parameters are changed by a script or any other module
    # those are reflected immediately in the GUI.
    if self._parameterNode is not None:
      self.removeObserver(self._parameterNode, vtk.vtkCommand.ModifiedEvent, self.updateGUIFromParameterNode)
    self._parameterNode = inputParameterNode
    if self._parameterNode is not None:
      self.addObserver(self._parameterNode, vtk.vtkCommand.ModifiedEvent, self.updateGUIFromParameterNode)

    # Initial GUI update
    self.updateGUIFromParameterNode()

  def updateGUIFromParameterNode(self, caller=None, event=None):
    """
    This method is called whenever parameter node is changed.
    The module GUI is updated to show the current state of the parameter node.
    """

    if self._parameterNode is None or self._updatingGUIFromParameterNode:
      return

    # Make sure GUI changes do not call updateParameterNodeFromGUI (it could cause infinite loop)
    self._updatingGUIFromParameterNode = True

    # Update node selectors and sliders
    #self.ui.inputSelector.setCurrentNode(self._parameterNode.GetNodeReference("InputVolume"))
    #self.ui.outputSelector.setCurrentNode(self._parameterNode.GetNodeReference("OutputVolume"))
    #self.ui.invertedOutputSelector.setCurrentNode(self._parameterNode.GetNodeReference("OutputVolumeInverse"))
    


    # Update buttons states and tooltips
# =============================================================================
#     if self._parameterNode.GetNodeReference("InputVolume") and self._parameterNode.GetNodeReference("OutputVolume"):
#       self.ui.applyButton.toolTip = "Compute output volume"
#       self.ui.applyButton.enabled = True
#     else:
#       self.ui.applyButton.toolTip = "Select input and output volume nodes"
#       self.ui.applyButton.enabled = False
# =============================================================================

    # All the GUI updates are done
    self._updatingGUIFromParameterNode = False

  def updateParameterNodeFromGUI(self, caller=None, event=None):
    """
    This method is called when the user makes any change in the GUI.
    The changes are saved into the parameter node (so that they are restored when the scene is saved and loaded).
    """

    if self._parameterNode is None or self._updatingGUIFromParameterNode:
      return

    wasModified = self._parameterNode.StartModify()  # Modify all properties in a single batch

    #self._parameterNode.SetNodeReferenceID("InputVolume", self.ui.inputSelector.currentNodeID)
    #self._parameterNode.SetNodeReferenceID("OutputVolume", self.ui.outputSelector.currentNodeID)
   
    #self._parameterNode.SetParameter("Invert", "true" if self.ui.invertOutputCheckBox.checked else "false")
   

    self._parameterNode.EndModify(wasModified)

  def addLog(self, text):
    """Append text to log window
    """
    import re
   
    if re.search("^APT.*[0-9]+$", text,flags = re.IGNORECASE):
        self.ui.cPatient.appendPlainText(text)
        slicer.app.processEvents()
    else:
        self.ui.statusLabel.appendPlainText(text)
        slicer.app.processEvents()  # force update

  
  def onApplyButton(self):
    """
    Run processing when user clicks "Apply" button.
    """
    with slicer.util.tryWithErrorDisplay("Unexpected error.",waitCursor=True):#try:
      # Compute output
      self.ui.statusLabel.plainText = '' #initialise the container to output the progress of your terminal window or python interpreter
      self.ui.cPatient.plainText = '' 
      dataDirectoryPath = self.ui.dataDirectoryPath.directory
      pythonPath = self.ui.pythonPath.currentPath
      patientID= self.ui.patientID.value
      #l = self.ui.listAlgo.currentText
      #print(l)
     
      items = self.ui.listWidget1.selectedItems()
      nnModels= []
      for i in range(len(items)):
          nnModels.append(str(self.ui.listWidget1.selectedItems()[i].text()))
      print (nnModels)
      
      
      
      self.logic.process(nnModels, dataDirectoryPath, pythonPath, patientID)#,self.ui.imageThresholdSliderWidget.value, self.ui.invertOutputCheckBox.checked)
      self.ui.statusLabel.appendPlainText("\nProcessing finished.")
      # Compute inverted output (if needed)
      #if self.ui.invertedOutputSelector.currentNode():
        # If additional output volume is selected then result with inverted threshold is written there
        #self.logic.process(self.ui.inputSelector.currentNode(), self.ui.invertedOutputSelector.currentNode(),
         # self.ui.imageThresholdSliderWidget.value, not self.ui.invertOutputCheckBox.checked, showResult=False)
     
         
    # except Exception as e:
    #   slicer.util.errorDisplay("Failed to compute results: "+str(e))
    #   import traceback
    #   traceback.print_exc()


#
# BatchBrainMRTumorSegmentationLogic
#

class BatchBrainMRTumorSegmentationLogic(ScriptedLoadableModuleLogic):
  """This class should implement all the actual
  computation done by your module.  The interface
  should be such that other python code can import
  this class and make use of the functionality without
  requiring an instance of the Widget.
  Uses ScriptedLoadableModuleLogic base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """
 
            
  def __init__(self):
    """
    Called when the logic class is instantiated. Can be used for initializing member variables.
    """
    ScriptedLoadableModuleLogic.__init__(self)
    self.logCallback = None

  def setDefaultParameters(self, parameterNode):
    """
    Initialize parameter node with default settings.
    """
    if not parameterNode.GetParameter("Threshold"):
      parameterNode.SetParameter("Threshold", "100.0")
    if not parameterNode.GetParameter("Invert"):
      parameterNode.SetParameter("Invert", "false")
      
  def log(self, text):
    logging.info(text)
    if self.logCallback:
      self.logCallback(text)
      
  def installPackages(self, pythonPath):
    """Install BraTS Toolkit in the selected external Python if needed."""
    from subprocess import CalledProcessError

    checkCommand = [pythonPath, '-c', 'import brats_toolkit']
    checkProcess = slicer.util.launchConsoleProcess(checkCommand, useStartupEnvironment=True)
    try:
      self.logProcessOutput(checkProcess)
      self.log('BraTS-Toolkit is already installed in the selected Python environment.')
      return
    except CalledProcessError:
      self.log('BraTS-Toolkit is not installed; installing it from PyPI...')

    cmdLine = [pythonPath, '-m', 'pip', 'install', 'BraTS-Toolkit']
    proc = slicer.util.launchConsoleProcess(cmdLine, useStartupEnvironment=True)
    self.logProcessOutput(proc)
  def logProcessOutput(self, proc):
    # Wait for the process to end and forward output to the log
    from subprocess import CalledProcessError
    while True:
        try:
            line = proc.stdout.readline()
        except UnicodeDecodeError as e:
            # Code page conversion happens because `universal_newlines=True` sets process output to text mode,
            # and it fails because probably system locale is not UTF8. We just ignore the error and discard the string,
            # as we only guarantee correct behavior if an UTF8 locale is used.
            pass
        if not line:
            break
        self.log(line.rstrip())
    proc.wait()
    retcode = proc.returncode
    if retcode != 0:
        raise CalledProcessError(retcode, proc.args, output=proc.stdout, stderr=proc.stderr)

  @staticmethod
  def writePatientStatusFile(filePath, patients):
    with open(filePath, 'w', newline='', encoding='utf-8') as outputFile:
      writer = csv.DictWriter(outputFile, fieldnames=['DirPaths', 'DirNames', 'Status'])
      writer.writeheader()
      writer.writerows(patients)

  @staticmethod
  def cliScriptPath(moduleName):
    try:
      modulePath = slicer.util.modulePath(moduleName)
    except (AttributeError, NameError) as exc:
      raise RuntimeError(f"Required CLI module '{moduleName}' is not installed.") from exc
    if not modulePath or not os.path.isfile(modulePath):
      raise RuntimeError(f"Cannot locate the script for required CLI module '{moduleName}'.")
    return modulePath

  def process(self, nnModels, directoryPath, pythonPath, patientID): 
    """
    #, imageThreshold, invert=False, showResult=True):
    Run the processing algorithm.
    Can be used without GUI widget.
    :param nnModels: list of neural network models used for segmentation
    :param directoryPath: the path to the directory containing the patient data
    :param pythonPath: the path to the Python interpreter to be used with installed brattoolkit librariries
    :param patientID: an integer indicating the patient ID to start processing from
    
    """
    if not nnModels:
      raise ValueError('Select at least one neural-network model.')
    if not directoryPath or not os.path.isdir(directoryPath):
      raise ValueError('Select an existing patient data directory.')
    if not pythonPath or not os.path.isfile(pythonPath):
      raise ValueError('Select an existing external Python executable.')
    if patientID < 0:
      raise ValueError('Patient ID must not be negative.')

    self.installPackages(pythonPath)
    import time
    import re
    startTime = time.time()
    self.log('Processing started............\n')
    patients = []
    patientNamePattern = re.compile(r'.*APT.*\d+$', re.IGNORECASE)
    for root, directoryNames, _files in os.walk(directoryPath, topdown=False):
      for directoryName in sorted(directoryNames):
        if patientNamePattern.match(directoryName):
          patients.append({
            'DirPaths': os.path.join(root, directoryName),
            'DirNames': directoryName,
            'Status': '',
          })
    patients.sort(key=lambda patient: patient['DirNames'].lower())

    if not patients:
      raise ValueError("No patient directories matching 'APT<number>' were found.")
    if patientID >= len(patients):
      raise ValueError(f'Patient ID {patientID} is outside the available range 0-{len(patients) - 1}.')

    statusFilePath = os.path.join(directoryPath, 'patients_id.csv')
    self.writePatientStatusFile(statusFilePath, patients)

    for patientID in range(patientID, len(patients)):
        patID = patientID
        startPatientDirName = patients[patientID]['DirNames']
        startPatientDirPath = patients[patientID]['DirPaths']
        self.log(startPatientDirName)
        self.log(startPatientDirPath)

        #checking the files for each patient if all the original files to run the preprocessor exist or not flair, t1, t2 and t1c
        path = startPatientDirPath
        
        #checking if the folder is empty
        if len(os.listdir(path)) == 0:
            patients[patientID]['Status'] = 'incomplete'
            self.writePatientStatusFile(statusFilePath, patients)
            continue
        
        #checking the incomplete ones in the file
        
        patterns = [".*fla.*.nii.gz", ".*t1.nii.gz", ".*t1c.nii.gz", ".*t2.nii.gz"]
        files = []
        
        try:
            for pattern in patterns:
                for file in os.listdir(path):
                    if re.search(pattern, file, flags = re.IGNORECASE):
                        print(os.path.join(path,file))
                        files.append(os.path.join(path,file))
            print(len(patterns), len(files))      
        
            if len(files) != len(patterns):
                self.log("Not all required files found in directory.........."+startPatientDirName)
                with open(directoryPath+"/failed_patient.txt", "a") as f:
                    f.write(str(patID))
                    f.write("\n")
                raise Exception("Not all required files found in directory")
        except FileNotFoundError as e:
            self.log(str(e))
            return


        self.log(f"All required patient files found for patient with id = {patID} and patient directory = {startPatientDirName}\n")
        self.log(f"Starting preprocessor of the brats toolkit for patient id {patID}\n")
        path_to_bratPreprocessor = self.cliScriptPath('BraTSPreprocessor')
        print(path_to_bratPreprocessor)
        command_line = [pythonPath, path_to_bratPreprocessor ,startPatientDirPath, startPatientDirName, files[0], files[1], files[2], files[3]]
        import subprocess
        import sys
        
        try:
          #command_results = subprocess.run(command_line, env=slicer.util.startupEnvironment())
          print("inside pre-processor")
          proc = slicer.util.launchConsoleProcess(command_line, useStartupEnvironment=True)
          self.logProcessOutput(proc)
          #command_result = check_output(command_line, env=slicer.util.startupEnvironment(), shell = True, stderr=subprocess.STDOUT)
          #You can write both stderr and stdout to two separate files: 
          #self.logProcessOutput(check_output(command_line, env=slicer.util.startupEnvironment(), shell = True, stderr=subprocess.STDOUT))                 
          #print(command_result)
        except subprocess.CalledProcessError as e:
            self.log(str(e))
            with open(directoryPath+"/failed_patient.txt", "a") as f:
                  f.write(str(patID))
                  f.write("\n")
                
            return
             
 
# =============================================================================
        # checking of the availability of the files for a current patient then enter to do segmentation
        # code for the checking of the files for the current patient
        # search the preprocessed brat files using the regular expression in a directory if all files exist proceed with segmentation 
        self.log(f"Starting checking the preprocessed brats files (fla, t1, t2, t1c) in path {startPatientDirPath}/output/hdbet_brats-space/\n")
        import re
        path = startPatientDirPath+"/output/hdbet_brats-space/"
        
        patterns = [".*fla.nii.gz", ".*t1.nii.gz", ".*t2.nii.gz", ".*t1c.nii.gz"]
        
        files = []
        try:
            for file in os.listdir(path):
                print(file)
                for pattern in patterns:
                    if re.search(pattern, file, flags=re.IGNORECASE):
                        print(os.path.join(path,file))
                        files.append(os.path.join(path,file))
            print(len(patterns), len(files))           
            if len(files) != len(patterns):
                self.log("Not all required files found in directory..........")
                with open(directoryPath+"/failed_patient.txt", "a") as f:
                    f.write(str(patID))
                    f.write("\n")
                raise Exception("Not all required files found in directory")
        except FileNotFoundError as e:
            self.log(str(e))
            return
        
        self.log(f"All required patient files found for starting segmentator for patient with id = {patID} and patient directory = {startPatientDirName}\n")
        self.log(f"Starting segmentator of the brats toolkit for patient id {patID}")
        path_to_bratSegmentor = self.cliScriptPath('BraTSSegmentor')
        print(path_to_bratSegmentor)
        command_line = [pythonPath, path_to_bratSegmentor, startPatientDirPath, startPatientDirName, json.dumps(nnModels)]
        try:
            print("inside segmentator")
            proc = slicer.util.launchConsoleProcess(command_line, useStartupEnvironment=True)
            self.logProcessOutput(proc)
            
        except subprocess.CalledProcessError as e:
            print("exception")
            self.log(str(e))
            with open(directoryPath+"/failed_patient.txt", "a") as f:
                f.write(str(patID))
                f.write("\n")
            return
            
        self.log(f"Segmentator of the brats toolkit finished successfully for patient id {patID}\n")    


        #checking of the files existence for fusion
        self.log("Starting checking the segmentation files for fusion in path "+startPatientDirPath+"/outputSegmentator/ \n")
        cids = nnModels#['isen-20','hnfnetv1-20','sanet0-20','scan-20']
        segFiles = [startPatientDirPath+"/outputSegmentator/"+ cid+".nii.gz" for cid in cids]
        
        try:
            for file in segFiles:
                if not os.path.exists(file):
                    raise FileNotFoundError(f"File {file} not found!")
            print("All files for fusion exist")
        except FileNotFoundError as e:
              print(e, file=sys.stderr)
              self.log(str(e))
              with open(directoryPath+"/failed_patient.txt", "a") as f:
                f.write(str(patID))
                f.write("\n")
              return

            
        self.log(f"All required patient files found to proceed with fusionator for patient with id = {patID} and patient directory = {startPatientDirName}\n")    
        self.log("Starting fusionator of the brats toolkit.............")    
        path_to_bratFusionator = self.cliScriptPath('BraTSFusionator')
        print( path_to_bratFusionator)
        command_line = [pythonPath, path_to_bratFusionator ,  startPatientDirPath, startPatientDirName, json.dumps(nnModels)]
        try:
            print("inside fusionator", startPatientDirPath, startPatientDirName)
            proc = slicer.util.launchConsoleProcess(command_line, useStartupEnvironment=True)
            self.logProcessOutput(proc)
            self.log("Fusionator of the brats toolkit finished successfully.................") 
            #add a flag in the fourth column "complete"
            
            
        except subprocess.CalledProcessError as e:
            print("exception")
            self.log(str(e))
            with open(directoryPath+"/failed_patient.txt", "a") as f:
                f.write(str(patID))
                f.write("\n")
            return
        
        #after performing the fusionator do the inverse transform and apply it to the segmentation and save the segmentation in a seperate output folder   
        registrationFilepath = startPatientDirPath+"/output/registrations/output_native_t1_to_brats_0GenericAffine.mat"
        trans = slicer.util.loadTransform(registrationFilepath)
        trans.Inverse()
        
        segMavFilepath = startPatientDirPath+"/outputFusionator/mav.nii.gz"
        segSimpleFilepath = startPatientDirPath+"/outputFusionator/simple.nii.gz"
        
        #loading segmentation files/volumes from the fusionator output folder 
        mavVol = slicer.util.loadVolume(segMavFilepath)
        simpleVol = slicer.util.loadVolume(segSimpleFilepath)
        
        #converting the volume to the label maps
        labelVolumeNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLLabelMapVolumeNode")
        labelVolumeNode.SetName("mav-seg")
        slicer.vtkSlicerVolumesLogic().CreateLabelVolumeFromVolume(slicer.mrmlScene, labelVolumeNode, mavVol)
        
        labelVolumeNode1 = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLLabelMapVolumeNode")
        labelVolumeNode1.SetName("simple-seg")
        slicer.vtkSlicerVolumesLogic().CreateLabelVolumeFromVolume(slicer.mrmlScene, labelVolumeNode1, simpleVol)
        
        #convert labelmap to segmentation node
        mavSeg = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLSegmentationNode")
        slicer.modules.segmentations.logic().ImportLabelmapToSegmentationNode(labelVolumeNode, mavSeg)
        #seg.CreateClosedSurfaceRepresentation()
        simpleSeg = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLSegmentationNode")
        slicer.modules.segmentations.logic().ImportLabelmapToSegmentationNode(labelVolumeNode1, simpleSeg)
        
        #now transform all the segmentation and label volume files and store it in a seperate folder for the patient under consideration
        labelVolumeNode.SetAndObserveTransformNodeID(trans.GetID())
        labelVolumeNode.HardenTransform()
        
        labelVolumeNode1.SetAndObserveTransformNodeID(trans.GetID())
        labelVolumeNode1.HardenTransform()
        
        mavSeg.SetAndObserveTransformNodeID(trans.GetID())
        mavSeg.HardenTransform()
        
        simpleSeg.SetAndObserveTransformNodeID(trans.GetID())
        simpleSeg.HardenTransform()
        
        #Now save all the transformed final file s to a folder
        transformedFilesPath = startPatientDirPath+"/outputFinal"
        os.makedirs(transformedFilesPath, exist_ok=True)

        slicer.util.saveNode(labelVolumeNode, transformedFilesPath+"/transMav-label.nrrd")
        slicer.util.saveNode(labelVolumeNode1, transformedFilesPath+"/transSimple-label.nrrd")
        slicer.mrmlScene.Clear(0)

        patients[patientID]['Status'] = 'complete'
        self.writePatientStatusFile(statusFilePath, patients)
      
        
        stopTime = time.time()
        self.log('Processing completed in {0:.2f} seconds\n'.format(stopTime-startTime))
