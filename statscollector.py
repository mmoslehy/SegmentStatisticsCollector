import vtkSegmentationCorePython as vtkSegmentationCore
import vtkSlicerSegmentationsModuleLogicPython as vtkSlicerSegmentationsModuleLogic
from slicer import util
from SegmentStatistics import SegmentStatisticsLogic

import os

#--DEBUGGING--
# import ptvsd
# ptvsd.enable_attach(secret='slicer')
# ptvsd.wait_for_attach()
# -----------

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
		convertedList = []
		for dicomDir in dicomDirs:
			# Specify the output nrrd file name as the directory name
			nrrdFile = os.path.split(dicomDir)[1]
			documentsDir = os.path.expanduser(r"~\\Documents")
			outputFileName = documentsDir + "\\NrrdOutput\\" + nrrdFile + ".nrrd"
			execString = "runner.bat " + self.converter + " --inputDicomDirectory " + dicomDir + " --outputVolume " + outputFileName
			os.system(execString)
			convertedList.append(outputFileName)
		return convertedList

class StatsCollectorLogic(object):
	# Constructor to store the segmentation in the object definition
	def __init__(self, segmentationFile):
		self.segFile = os.path.normpath(segmentationFile)
		self.segNode = util.loadSegmentation(self.segFile,returnNode=True)[1]


	def exportStats(self, segStatLogic, csvFileName, header=""):
		outputFile = csvFileName
		if not csvFileName.endswith('.csv'):
			outputFile += '.csv'

		fp = open(outputFile, "a")
		fp.write(header+'\n')
		fp.write(segStatLogic.exportToString())
		fp.write("\n")
		fp.close()

	def getStatForVol(self, volFile):
		# --Load master volumes--
		volNode = util.loadVolume(volFile,returnNode=True)[1]
		if volNode is None:
			print("Volume could not be loaded from: " + volFile)
			quit()

		# Compute statistics
		segStatLogic = SegmentStatisticsLogic()
		segStatLogic.computeStatistics(self.segNode, volNode)

		# Export results to string
		# logging.info(segStatLogic.exportToString())

		# Export results to CSV file
		# outputFile = csvFileName
		# if not csvFileName.endswith('.csv'):
		# 	outputFile += '.csv'
		# segStatLogic.exportToCSVFile(outputFile)

		csvFileName = volNode.GetName()
		csvFilePath = os.path.normpath(os.path.expanduser(r"~\\Documents\\SegmentStatistics\\" + csvFileName))
		self.exportStats(segStatLogic, csvFilePath, csvFileName)

		return segStatLogic.exportToString()

class MetaExporter(object):
	def __init__(self, pathToDicoms, pathToConverter, segmentationFile):
		self.converter = NrrdConverterLogic(pathToDicoms, pathToConverter)
		self.sc = StatsCollectorLogic(segmentationFile)

		# Get all stats
		convertedList = self.converter.convertToNrrd()
		for nrrd in convertedList:
			self.sc.getStatForVol(nrrd)
