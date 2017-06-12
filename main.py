import statscollector
import sys

# If the number of arguments entered is less than 2 (by default, the first argument is the script name), throw an error
if len(sys.argv) < 3:
	print("INVALID SYNTAX FOR SEGMENTSTATISTICS COLLECTOR, USAGE: " + sys.argv[0] + " pathToDicoms segmentationFile saveName")
	exit(1)
# Otherwise, store the pathname provided as an argument
else:
	pathToDicoms = sys.argv[1]
	pathToConverter = os.path.join(os.path.split(sys.argv[0])[0], "DicomToNrrdConverter.exe")
	print("HELLO WORLD" + pathToConverter)
	quit()
	segmentationFile = sys.argv[2]

	statscollector.MetaExporter(pathToDicoms, pathToConverter, segmentationFile)