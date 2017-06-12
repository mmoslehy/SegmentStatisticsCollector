"""
MAKE SURE THAT YOU ALWAYS PUT 'r' OR 'R' IN FRONT OF ANY PATH NAMES, SUCH AS 
r"C:\testdata\54545Heart.seg.nrrd"
or
R"C:\testdata\54545Heart.seg.nrrd"
"""

import vtkSegmentationCorePython as vtkSegmentationCore
import vtkSlicerSegmentationsModuleLogicPython as vtkSlicerSegmentationsModuleLogic
from SegmentStatistics import SegmentStatisticsLogic

import os, sys

#--DEBUGGING--
# import ptvsd
# ptvsd.enable_attach(secret='slicer')
# ptvsd.wait_for_attach()
# -----------

# # If the number of arguments provided is less than 1 (by default, the first argument is the script name), throw an error
# if len(sys.argv) < 2:
# 	print("Error: no folder specified")
# 	quit()
# # Otherwise, store the pathname provided as an argument
# else:
# 	path = sys.argv[1]
# 	print("Analyzing: ",path)

class NrrdConverterLogic(object):

	def __init__(self, pathToDicoms, pathToConverter):
		self.pathToDicoms = os.path.normpath(pathToDicoms)
		self.converter = os.path.normpath(pathToConverter)
		if not os.path.exists(self.pathToDicoms) or not os.path.exists(self.converter):
			print("DICOMs or Converter does not exist")
			quit()

	# Loop through directory given to find DICOM directories
	def getDicomDirs(self):
		pathWalk = os.walk(self.pathToDicoms)
		dicomDirs = []
		for root, dirs, files in pathWalk:
			for file in files:
				if file.endswith(".dcm"):
					dicomDirs.append(root)
		return list(set(dicomDirs))

	def convertToNrrd(self):
		dicomDirs = self.getDicomDirs()
		for dicomDir in dicomDirs:
			# Specify the output nrrd file name as the directory name
			nrrdFile = os.path.split(dicomDir)[1]
			documentsDir = os.path.expanduser(r"~\\Documents")
			execString = "runner.bat " + self.converter + " --inputDicomDirectory " + dicomDir + " --outputVolume " + documentsDir + "\\NrrdOutput\\" + nrrdFile + ".nrrd"
			os.system(execString)


class StatsCollectorLogic(object):
	# Constructor to store the segmentation in the object definition
	def __init__(self, segmentationFile):
		self.segFile = os.path.normpath(segmentationFile)
		self.segNode = loadSegmentation(self.segFile,returnNode=True)[1]

	def getStatForVol(self, volFile, csvFileName):
		# --Load master volumes--
		volNode = slicer.util.loadVolume(volFile,returnNode=True)[1]

		# Compute statistics
		segStatLogic = SegmentStatisticsLogic()
		segStatLogic.computeStatistics(self.segNode, volNode)

		# Export results to string
		# logging.info(segStatLogic.exportToString())

		# Export results to CSV file
		outputFile = csvFileName
		if not csvFileName.endswith('.csv'):
			outputFile += '.csv'
		segStatLogic.exportToCSVFile(outputFile)

		return segStatLogic.exportToString()

	def exportStats(self, segStatLogic, csvFileName, header=""):
		fp = open(csvFileName, "a")
		fp.write(header)
	    fp.write(segStatLogic.exportToString(nonEmptyKeysOnly))
	    fp.close()

    def exportAllStats(self, converterLogic, csvFileName):
    	