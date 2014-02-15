from data import TestData
import re, numpy
from datetime import datetime
from common import isNotEmptyString

def extractDuration(filename, durationRegex):
	# Get info from filename
	matchresult = re.search(durationRegex, filename)
	testduration = int(matchresult.group(1))
	return testduration

def loadDataFileAsStrings(filename):
	# Read file contents into contents
	dataFile = open(filename)
	contents = dataFile.read()
	dataFile.close()	
	# Split lines into rows of data
	if contents.find('\r') != -1:
		(head, tail) = contents.split('\r',1) #first line has a \r instead of a \n, so we split on the first \r, then treat it normally
		rows = [head] + tail.split('\n')
	else:
		rows = contents.split('\n') #normal filem treat the easier way :-)
	
	# Filter out empty rows (should only be the very last one, but we look for other ones anyway)
	filteredRows = filter(isNotEmptyString, rows)
	# instead of using the function isNotEmptyString, we could have also used an inline function: filter(lambda x: x != '', rows)
	# Split comma seperated values
	splitRows = [row.split(';') for row in filteredRows]
	# Split header and data
	header = splitRows[0] #we probably don't need this
	dataAsStrings = splitRows[1:]
	return TestData(header,*dataAsStrings)

def loadTestFile(filename):	
	data = loadDataFileAsStrings(filename)
	# Make sure data is interpreted as the correct types and remove unecessary data
	data = data.withoutColumn('Calibration')
	data = data.applyFunctionToColumn(float, 'Channel')
	data = data.applyFunctionToColumn(float, 'Value')
	data = data.renameColumn('Value','Count')
	# Return the data
	return data
	
def loadEnergyFitFile(filename):
	data = loadDataFileAsStrings(filename)
	data = data.applyFunctionToColumn(float, 'Value')
	data = data.applyFunctionToColumn(float, 'Std Dev')
	return data
	
def loadTestFileWithBackgroundAndCalculateCountErr(datafilename, bkgfilename, durationRegex, scaleToDuration=-1):
	rawData = loadTestFile(datafilename)
	dataduration = extractDuration(datafilename, durationRegex)
	background = loadTestFile(bkgfilename)
	bkgduration = extractDuration(bkgfilename, durationRegex)
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
	
def loadTestFileAndCalculateEnergy(datafilename, bkgfilename, energycalibrationfilename, durationRegex, scaleToDuration=-1):
	testData = loadTestFileWithBackgroundAndCalculateCountErr(datafilename, bkgfilename, durationRegex, scaleToDuration)
	energyfitData = loadEnergyFitFile(energycalibrationfilename)
	(a,b) = energyfitData['Value']
	(a_err,b_err) = energyfitData['Std Dev']
	# energy = a * channel + b
	energy = numpy.add(
				numpy.multiply(testData['Channel'], a), b
			)
	# energy error = sqrt( (a_err*channel)**2 + (b_err)**2)
	energyErr = numpy.sqrt(
					numpy.add(
						numpy.square(numpy.multiply(testData['Channel'], a_err)), numpy.square(b_err)
					)
				)
	return testData.withColumn('Energy',energy).withColumn('EnergyErr',energyErr)
