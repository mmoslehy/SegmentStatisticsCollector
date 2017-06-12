import vtkSegmentationCorePython as vtkSegmentationCore
import vtkSlicerSegmentationsModuleLogicPython as vtkSlicerSegmentationsModuleLogic
import slicer
from SegmentStatistics import SegmentStatisticsLogic
import logging
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
		noDuplicates = list(set(dicomDirs))
		noDuplicates.sort()
		return noDuplicates

	def convertToNrrd(self):
		dicomDirs = self.getDicomDirs()
        # TEMP - CHANGE NAME
		dcmDictionary = {}
		for dicomDir in dicomDirs:
			# Specify the output nrrd file name as the directory name
			nrrdFile = os.path.split(dicomDir)[1]
			parentDir = os.path.split(os.path.split(dicomDir)[0])
			# This is the directory above the directory containing the DICOMs (e.g. if PyBy6/8001/x.dcm then this is PyBy6) 
			folderName = parentDir[1]
			grandParentDir = os.path.split(parentDir[0])[1]
			documentsDir = os.path.normpath(os.path.expanduser(r"~\\Documents\\StatsCollector\\NrrdOutput"))
			if not os.path.exists(documentsDir):
				os.mkdir(documentsDir)
			outputFileName = os.path.normpath(documentsDir + "\\" + grandParentDir + "-" + folderName + "_" + nrrdFile + ".nrrd")
			runnerPath = os.path.split(self.converter)[0] + '\\runner.bat'
			execString = runnerPath + " " + self.converter + " --inputDicomDirectory " + dicomDir + " --outputVolume " + outputFileName
			os.system(execString)
			if not dcmDictionary.has_key(folderName):
				dcmDictionary[folderName] = []
			dcmDictionary[folderName].append(outputFileName)
		return dcmDictionary

class StatsCollectorLogic(object):
	# Constructor to store the segmentation in the object definition
	def __init__(self, segmentationFile):
		self.segFile = os.path.normpath(segmentationFile)
		self.segNode = slicer.util.loadSegmentation(self.segFile,returnNode=True)[1]


	def exportStats(self, segStatLogic, csvFileName, header=""):
		outputFile = csvFileName
		if not csvFileName.endswith('.csv'):
			outputFile += '.csv'

		fp = open(outputFile, "a")
		fp.write(header+'\n')
		fp.write(segStatLogic.exportToString())
		fp.write("\n")
		fp.close()

	def getStatForVol(self, volFile, csvFileName):
		# --Load master volumes--
		volNode = slicer.util.loadVolume(volFile,returnNode=True)[1]
		if volNode is None:
			print("Volume could not be loaded from: " + volFile)
			quit()

		# Compute statistics
		segStatLogic = SegmentStatisticsLogic()
		segStatLogic.computeStatistics(self.segNode, volNode)

		documentsDir = os.path.normpath(os.path.expanduser(r"~\\Documents\\StatsCollector\\SegmentStatistics"))
		if not os.path.exists(documentsDir):
			os.mkdir(documentsDir)
		csvFilePath = os.path.normpath(documentsDir + "\\" + csvFileName)
		self.exportStats(segStatLogic, csvFilePath, volNode.GetName())

		return segStatLogic.exportToString()

class MetaExporter(object):
	def __init__(self, pathToDicoms, pathToConverter, segmentationFile):
		self.converter = NrrdConverterLogic(pathToDicoms, pathToConverter)
		self.sc = StatsCollectorLogic(segmentationFile)

		# Get all stats
		dcmDictionary = self.converter.convertToNrrd()
		for folderName, nrrdList in dcmDictionary.items():
			for nrrd in nrrdList:
				self.sc.getStatForVol(nrrd, folderName)
