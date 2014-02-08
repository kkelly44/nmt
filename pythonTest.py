#!/usr/bin/python
import math
import numpy
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from matplotlib.widgets import Button, SpanSelector, RectangleSelector

def printHello():
	print "Hello, I'm working!"
	print "Remember: its:"
	print "\t C to start the selector. Drag and drop over the area. The selection will show up in commandline. You can keep selecting until the desired invertal is selected."
	print "\t G to add the current selection to the selection for Gaussian fit calculations."
	print "\t \t Select the next peak and press G. You only need to click C once."
	print "\t R to Run the gaussian fit calculations."
	print "\t S will open a dialog to save the plot."

def isNotEmptyString(string):
	return string != ''

def getDataRows():
	# Read file contents into contents
	dataFile = open('data/23-10-2013_16u29_7160s.csv')
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
	# Make sure data is interpreted as the correct types and remove unecessary data
	data = [{'Channel':int(channel), 'Count':float(value)} for (channel, calibration, value) in dataAsStrings]
	# Return the data
	return data
	
def addCountErr(data): # adds the Y error to the data array
	return [{'Channel': row['Channel'], 'Count': row['Count'], 'CountErr': math.sqrt(row['Count']) } for row in data]	

def extractDataColumn(data, dataName): #returns an array of 1 element of the main data (extracts a single column into a new array)
	return [datum[dataName] for datum in data]

#the error bar function:
#http://matplotlib.org/api/axes_api.html#matplotlib.axes.Axes.errorbar
#description of formats (line, dotted line, dots, ...):
#http://matplotlib.org/api/axes_api.html#matplotlib.axes.Axes.plot
def plotRangeTo(dataWithCountErr, saveFileName, start, end): 
	fig = plt.figure(figsize=(16, 10)) # open empty image
	ax = fig.add_subplot(111) #change the values to add more plots #add a (sub)plot
	
	ax.set_xlabel('Channel', fontsize = 16) #set axis name
	ax.set_xticks(numpy.arange(start,end,300), False) #set major ticks
	ax.set_xticks(numpy.arange(start,end,100), True) #set minor ticks

	ax.set_ylabel('Count', fontsize = 16)
	
	channel = extractDataColumn(dataWithCountErr, 'Channel')[start:end]
	count = extractDataColumn(dataWithCountErr, 'Count')[start:end]
	countErr = extractDataColumn(dataWithCountErr, 'CountErr')[start:end]
	
	#plot just points with error bars
	(plotline, caplines, barlinecols) = ax.errorbar(channel, count, fmt = 'go', yerr = countErr) #this both plots AND returns the values on which it bases its plotting
	#plotline.set_picker(True)
	#ax.plot(channel, count) #plots a line between the points and not the points themselves
	#ax.plot(channel, count, fmt='o') #plots a line of points
	#plt.show()
	return (fig,ax)


def fitGaussian(interval, dataWithCountErr, startingGaussianParameters):
	def gaussian(x, a, b, c):
		val = a * numpy.exp(-(x - b)**2 / c**2)
		return val
	start = int(numpy.round(interval[0])) #get the values for where the chosen interval start/stops
	end = int(numpy.round(interval[1]))
	x = extractDataColumn(dataWithCountErr, 'Channel')[start:end]
	y = extractDataColumn(dataWithCountErr, 'Count')[start:end]
	err = extractDataColumn(dataWithCountErr, 'CountErr')[start:end]

	popt, pcov = curve_fit(gaussian, x, y, sigma=err, p0=startingGaussianParameters)
	fit_errors = []
	for i in range(0,3):
		fit_errors.append(math.sqrt(pcov[i,i]))
	print 'popt: {0}'.format(popt)
	print 'pcov: {0}'.format(pcov)
	print 'fit_errors: {0}'.format(fit_errors)

	return popt, pcov

# See http://matplotlib.org/api/widgets_api.html for info on the widgets
#	Selector example (also deals with key press): http://matplotlib.org/examples/widgets/rectangle_selector.htmls
def interactiveDataSetSelector(fig,ax,dataWithCountErr):
	#Variables
	global currentInterval, intervals
	currentInterval = None
	intervals = []

	#Callback functions
	def selectInterval(x1, x2):
		global currentInterval
		print ("Selected range: %3.2f --> %3.2f" % (x1, x2))
		currentInterval = (x1,x2)
	def calculateGaussians():
		global intervals
		#spit the gaussian fit and covarrience matrix PER FIT out
		print  'Chosen intervals: {0}'.format(intervals)
		fitGaussian(intervals[0],dataWithCountErr,[2000,200,30])
	def choosecurrentIntervalForGaussianFit():
		global currentInterval
		if currentInterval == None:
			print 'Error: no range selected'
		else:
			print 'Range %3.2f --> %3.2f added to intervals for gaussian fit' % (currentInterval[0], currentInterval[1])
			intervals.append(currentInterval)
	
	#Handle key presses
	def handle_key(event):
		if event.key in ['C', 'c'] and handle_key.spanSelector == None:
			print 'Span selector activated'
			handle_key.spanSelector = SpanSelector(ax, selectInterval, 'horizontal')
		elif event.key in ['C', 'c'] and handle_key.spanSelector != None:
			print 'Span selector deactivated'
			handle_key.spanSelector = None
		elif event.key in ['G','g']:
			choosecurrentIntervalForGaussianFit()
		elif event.key in ['R', 'r']:
			calculateGaussians()
		else:
			print 'Detected keypress {0}, unknown command'.format(event.key)
	
	handle_key.spanSelector = None
			
	fig.canvas.mpl_connect('key_press_event', handle_key)



if __name__ == '__main__': #means it's only gonna work when run from the command line
	printHello()
	#execute this if this file gets executed
	rawData = getDataRows()
	dataWithCountErr = addCountErr(rawData)
	#print out the first 10 rows
	#print dataWithCountErr[0:10] #can leave off 0 and it will automatically take the start
	(fig,ax) = plotRangeTo(dataWithCountErr, saveFileName='testFull.png', start=0, end=4096) #(data, save file name, start range data, end range data)
	interactiveDataSetSelector(fig,ax,dataWithCountErr)
	#fig.savefig(saveFileName, bbox_inches=0)
	#def onpick(event):
	#	# Get specific data for the pick
	#	thisline = event.artist
	#	xdata = thisline.get_xdata()
	#	ydata = thisline.get_ydata()
	#	ind = event.ind
	#	print 'onpick points:', zip(xdata[ind], ydata[ind])

	#fig.canvas.mpl_connect('pick_event', onpick)
	#fig.canvas.mpl_connect('key_press_event', handle_key)
	#print cid
	plt.show()


##### OLD CODE
def plotRangeTo_old(dataWithCountErr, saveFileName, start, end):
	plt.ylabel('Count', fontsize = 16)
	plt.xlabel('Channel', fontsize = 16)
	#channel = [data['Channel'] for data in dataWithCountErr][start:end] # uncomment the range for testing purposes
	channel = extractDataColumn(dataWithCountErr, 'Channel')[start:end]
	count = extractDataColumn(dataWithCountErr, 'Count')[start:end]
	countErr = extractDataColumn(dataWithCountErr, 'CountErr')[start:end]
	plt.errorbar(channel, count, fmt = 'ro', yerr = countErr) #plots just points with error bars
	#plt.show()
	plt.savefig(saveFileName, bbox_inches=0)












