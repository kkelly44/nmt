from data import TestData
import re, numpy
from datetime import datetime
from common import isNotEmptyString
def loadTestFile(filename, fileformat, dateformat):
	# Get info from filename
	matchresult = re.search(fileformat, filename)
	testdate = datetime.strptime(matchresult.group(1), dateformat)
	testtype = matchresult.group(2)
	testduration = int(matchresult.group(3))
	print 'Loaded file {0} \nRun on {1}\nOf type {2}\nDuration {3} seconds'.format(filename, testdate, testtype, testduration) 
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
	
def loadTestFileWithBackgroundAndCalculateCountErr(datafilename, bkgfilename, fileformat, dateformat):
	rawData, dataduration = loadTestFile(datafilename, fileformat, dateformat)
	background, bkgduration = loadTestFile(bkgfilename, fileformat, dateformat)
	#scale background counts to time length of actual test run: scaledbkgcounts = bkgcounts * (dataduration/bkgduration)
	scaledbkgcounts = numpy.multiply(background['Count'],dataduration/bkgduration)
	#calculate countErr:
	#rawData = sqrt(count_raw)
	#background = sqrt(count_back)
	#combined = sqrt( raw_err**2 + back_err**2 ) = sqrt(sqrt(count_raw)**2 + sqrt(count_back)**2) = sqrt(abs(count_raw) + abs(count_back))
	countErr = 	numpy.sqrt(
					numpy.add(
						numpy.absolute(rawData['Count']), numpy.absolute(scaledbkgcounts)
					)
				)
	#subtract real background
	correctedData = rawData.subtractFromColumn('Count', scaledbkgcounts)
	correctedDataWithCountErr = correctedData.withColumn('CountErr',countErr)
	return correctedDataWithCountErr
