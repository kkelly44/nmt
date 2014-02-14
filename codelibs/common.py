from datetime import datetime
import numpy

##################
# Random utility #
##################

def isNotEmptyString(string):
	return string != ''

def getIntervalString(interval):
	return '{0}-->{1}'.format(interval[0]['Channel'],interval[-1]['Channel'])

def debug(msg):
	f = open(config.debugfile, 'a')
	f.write('Timestamp {0}\n\n'.format(datetime.today()))
	f.write(msg)
	f.write('\n\n\n\n')
	f.close()

def recursiveSlice(array, length=25, start = 0):
	if isinstance(array, list) or isinstance(array, tuple):
		return [recursiveSlice(el, length, start) for el in array[start:length-start]]
	else:
		return array

def getSpaceLengthInTabs(length, tabwidth):
	return (numpy.ceil(float(length)/float(tabwidth)), length%tabwidth==0)

def padWithTabsToLength(target, tabwidth, length, extraTabs):
	string = str(target)
	(maxLengthInTabs, maxFull) = getSpaceLengthInTabs(length,tabwidth)
	(stringLengthInTabs, stringFull) = getSpaceLengthInTabs(len(string),tabwidth)
	nbTabs = maxLengthInTabs + 1*maxFull - stringLengthInTabs - 1*stringFull
	return string + '\t'*nbTabs + '\t'*extraTabs



