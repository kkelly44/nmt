from data import TestData
import re, numpy
from datetime import datetime
from common import isNotEmptyString
def loadTestFile(filename, durationRegex):
	# Get info from filename
	matchresult = re.search(durationRegex, filename)
	testduration = int(matchresult.group(1))
	print 'Loaded file {0} with duration {1} seconds'.format(filename, testduration) 
	# Read file contents into contents
	dataFile = open(filename)
	contents = dataFile.read()
	dataFile.close()
	
	# Split lines into rows of data
	(head, tail) = contents.split('\r',1) #first line has a \r instead of a \n, so we split on the first \r, then treat it normally
	rows = [head] + tail.split('\n')
	# Filter out empty rows (should only be the very last one, but we look for other ones anyway)
	filteredRows = filter(isNotEmptyString, rows)
	# instead of using the function isNotEmptyString, we could have also used an inline function: filter(lambda x: x != '', rows)
	# Split comma seperated values
	splitRows = [row.split(';') for row in filteredRows]
	# Split header and data
	header = splitRows[0] #we probably don't need this
	dataAsStrings = splitRows[1:]
	# Make sure data is interpreted as the correct types
	#dataAsFloats = [[float(el) for el in row] for row in dataAsStrings]
	# Remove unecessary data
	data = TestData(header,*dataAsStrings)
	data = data.withoutColumn('Calibration')
	data = data.applyFunctionToColumn(float, 'Channel')
	data = data.applyFunctionToColumn(float, 'Value')
	data = data.renameColumn('Value','Count')
	# Return the data
	return (data, testduration)
	
def loadTestFileWithBackgroundAndCalculateCountErr(datafilename, bkgfilename, durationRegex, scaleToDuration=-1):
	rawData, dataduration = loadTestFile(datafilename, durationRegex)
	background, bkgduration = loadTestFile(bkgfilename, durationRegex)
	if scaleToDuration <= 0:
		#scale background counts to time length of actual test run: scaledbkgcounts = bkgcounts * (dataduration/bkgduration)
		scaledbkgcounts = numpy.multiply(background['Count'],float(dataduration)/float(bkgduration))
		data = rawData
	else:
		scaledbkgcounts = numpy.multiply(background['Count'],float(scaleToDuration)/float(bkgduration))
		data = rawData.applyFunctionToColumn(lambda x: x*float(scaleToDuration)/float(dataduration), 'Count')
	#calculate countErr:
	#data = sqrt(count_data)
	#scaledbackground = sqrt(count_back)
	#combined = sqrt( data_err**2 + back_err**2 ) = sqrt(sqrt(count_data)**2 + sqrt(count_back)**2) = sqrt(abs(count_data) + abs(count_back))
	countErr = 	numpy.sqrt(
					numpy.add(
						numpy.absolute(data['Count']), numpy.absolute(scaledbkgcounts)
					)
				)
	#subtract real background
	correctedData = data.subtractFromColumn('Count', scaledbkgcounts)
	correctedDataWithCountErr = correctedData.withColumn('CountErr',countErr)
	return correctedDataWithCountErr
