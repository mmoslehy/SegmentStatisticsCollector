import vtkSegmentationCorePython as vtkSegmentationCore
import vtkSlicerSegmentationsModuleLogicPython as vtkSlicerSegmentationsModuleLogic
from SegmentStatistics import SegmentStatisticsLogic

import os, sys
from os.path import join, getsize

#--DEBUGGING--
# import ptvsd
# ptvsd.enable_attach(secret='slicer')
# ptvsd.wait_for_attach()
# -----------

# If the number of arguments provided is less than 1 (by default, the first argument is the script name), throw an error
if len(sys.argv) < 2:
	print("Error: no folder specified")
	quit()
# Otherwise, store the pathname provided as an argument
else:
	path = sys.argv[1]
	print("Analyzing: ",path)

# --Load master volumes--
# Loop through directory given to find DICOM directories
pathWalk = os.walk(path)
dicomDirs = []
for root, dirs, files in pathWalk:
	for file in files:
		if file.endswith(".dcm"):
			dicomDirs.append(root)

masterVolumeNode = slicer.util.loadVolume("C:\Users\Moselhy\Documents\Testing\pyruvate8001.nrrd",returnNode=True)[1]

# Load segmentation
segmentNode = loadSegmentation("C:\\Users\\Moselhy\\Documents\\Segmentations\\54501_Segment.seg.nrrd",returnNode=True)[1]

# Compute statistics
segStatLogic = SegmentStatisticsLogic()
segStatLogic.computeStatistics(segmentNode, masterVolumeNode)

# Export results to table
resultsTableNode = slicer.vtkMRMLTableNode()
slicer.mrmlScene.AddNode(resultsTableNode)
segStatLogic.exportToTable(resultsTableNode)
segStatLogic.showTable(resultsTableNode)

# Export results to string
logging.info(segStatLogic.exportToString())

outputFilename = slicer.app.temporaryPath + '/SegmentStatisticsTestOutput.csv'
delayDisplay("Export results to CSV file: "+outputFilename)
segStatLogic.exportToCSVFile(outputFilename)
