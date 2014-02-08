#!/usr/bin/python
import math
import numpy
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from matplotlib.widgets import Button, SpanSelector, RectangleSelector
import config
from startingvaluesdialog import showStartingValuesDialog
from correlateenergydialog import showCorrelateEnergyDialog
from common import TestData, gaussian, line, isNotEmptyString, fitFunction, addFunctionToPlot, createEmptyPlottingArea, addDataWithErrorBarsToPlot, fittedFunction, debug, lineOdr, gaussianOdr, fitFunctionWithDoubleErr, getDataRowWithMaxForField

def printHello():
	print "Hello, I'm working!"
	print "Remember: its:"
	print "\t C to start the selector. Drag and drop over the area. The selection will show up in commandline. You can keep selecting until the desired invertal is selected. Click C again to stop the selector (in case you ever need it)."
	print "\t G to run the Gaussian fit for the current selection. Press G again without making a new selection to run again (you can change starting values and iterations)"
	print "\t \t Select the next peak and press G. You only need to click C once to start the selector."
	print "\t A to Add the gaussian fit calculations."
	print "\t E to start the Energy calibration."
	print "\t F to save the energy calibration to File"
	print "\t S will open a dialog to save the plot."

def getDataRows(filename):
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
	return data

#def removeZeroCountsAndWarn(data):
#	f = open(config.errordatafile,'w')
#	def filterFunc(row):
#		if row['Count'] != 0:
#			return True
#		else:
#			f.write('{Channel};{Count}'.format(**row))
#			return False
#	result = [row for row in data if filterFunc(row)]
#	f.close()
#	return result

def addCountErr(data): # adds the Y error to the data array
	counts = data['Count']
	return data.withColumn('CountErr',numpy.sqrt(counts))

def getDefaultsForGaussianFit(interval): # beacuse 111 is not going to be a decent starting point, we feed it common sense starting values
	# a should be max of count in interval, b should be channel of max count, c should be half of elements in interval
	maxCount = getDataRowWithMaxForField('Count', interval)
	a = maxCount['Count']
	b = maxCount['Channel']
	c = len(interval)/6
	return (a,b,c)

def plotRangeTo(dataWithCountErr, start, end): 
	(fig, axes) = createEmptyPlottingArea('Channel', 'Count', x_majorticks = 300, x_minorticks = 100, x_length=4096)

	channel = dataWithCountErr['Channel'][start:end]
	count = dataWithCountErr['Count'][start:end]
	countErr = dataWithCountErr['CountErr'][start:end]

	addDataWithErrorBarsToPlot(axes, channel, count, y_err=countErr)
	return (fig,axes)

# WARNING: does not take x_err or y_err into account (just returns them unchanged).
def removeDC(x,y,x_err,y_err):
	firstX = x[0]
	lastX = x[-1]	
	firstY = y[0]
	lastY = y[-1]
	dcA = (lastY-firstY)/(lastX-firstX)
	dcB = firstY - dcA*firstX
	fittedLine = fittedFunction(line, dcA, dcB)
	dcY = [fittedLine(xi) for xi in x]
	#substract dcY from y -> ATTENTION: should we change y_err or does it stay the same?
	y = numpy.subtract(y,dcY)
	return (x,y,x_err,y_err)

	
def fitGaussianAndAddToPlot(interval, startingGaussianParameters, max_iterations, fig, axes):
	x = interval['Channel']
	y = interval['Count']
	x_err = None #Just making it explicit that we don't have an x_err at this point
	y_err = interval['CountErr']
	
	(x,y,x_err,y_err) = removeDC(x,y,x_err,y_err)
	
	(popt, pcov, fit_errors, infodict, errmsg, success) = fitFunction(gaussian, x, y, startingGaussianParameters, y_err=y_err, max_iterations=max_iterations)
	if success:
		(a,b,c) = popt
		(err_a, err_b, err_c) = fit_errors
		gaussParams = ({'a':a, 'b':b, 'c':c},pcov,{'a':err_a, 'b':err_b, 'c':err_c})
		(params, variance_matrix, fit_errors) = gaussParams
		print 'params: {0}'.format(params)
		print 'fit_errors: {0}'.format(fit_errors)
		fittedGaussian = fittedFunction(gaussian,a,b,c)
		addFunctionToPlot(axes, interval['Channel'], fittedGaussian)
		fig.show()
		return gaussParams
	else:
		print 'Error creating gaussian fit: {0}'.format(errmsg)
		return None

def processAndPlotEnergyCalibrationData(energyCalibrationData):
	x = energyCalibrationData['Peak']
	x_err = energyCalibrationData['PeakErr']
	y = energyCalibrationData['Energy']
	y_err = energyCalibrationData['EnergyErr']
	(fig, axes) = createEmptyPlottingArea('Channel', 'Energy')
	print 'Energy Calibration'
	print x
	print y
	print x_err
	print y_err
	addDataWithErrorBarsToPlot(axes, x, y, x_err=x_err, y_err=y_err)
	fig.show()
	
	#find fit for energy calibration
	output = fitFunctionWithDoubleErr(x, y, x_err, y_err, fitFunction=lineOdr, startingParameters=[0.2,10.0])
	
	params = output.beta
	variance_matrix = output.cov_beta
	fit_errors = output.sd_beta #seems to calculated this for us already
	
	print (params, variance_matrix, fit_errors)
	(a,b) = params #fits for line
	print variance_matrix
	fittedLine = fittedFunction(line, a, b)
	addFunctionToPlot(axes, x, fittedLine, config.gaussianformat)
	fig.show()
	energyCalibrationFit = {'params':params, 'variance_matrix':variance_matrix, 'fit_errors':fit_errors, 'x':x, 'x_err': x_err, 'y':y, 'y_err':y_err}
	return energyCalibrationFit

# See http://matplotlib.org/api/widgets_api.html for info on the widgets
#	Selector example (also deals with key press): http://matplotlib.org/examples/widgets/rectangle_selector.htmls
class MainGuiController(object):
	#Variables
	currentStartEnd = None #last selected start and end with the spanselector
	currentInterval = None #last chosen interval
	currentGaussParams = None
	currentEnergyCalibrationFit = None
	gaussianFits = [] #list of chosen intervals
	spanSelector = None #the thingie that helps you select a part of the graph
	fig = None # the figure on which the plot is drawn
	axes = None # this is basically the plot
	dataWithCountErr = [] #our data (Channel, Count, CountErr)
	peakData = None

	def run(self, dataWithCountErr, start=0, end=4096):
		(fig,axes) = plotRangeTo(dataWithCountErr, start, end) #(data, save file name, start range data, end range data)
		self.fig = fig
		self.axes = axes
		self.dataWithCountErr = dataWithCountErr
		fig.canvas.mpl_connect('key_press_event', self.handle_key) #make it so we handle keypress events
		self.peakData = TestData(['Peak','PeakErr'],[], [])
		plt.show()

	#Callback functions
	def selectInterval(self, start_x, end_x): #function called by span selector with start and end of selection
		start_channel = int(numpy.round(start_x))
		end_channel = int(numpy.round(end_x))
		print ("Selected range: %3.2f --> %3.2f" % (start_channel, end_channel))
		self.currentStartEnd = (start_channel,end_channel)
	def choosecurrentStartEndForGaussianFit(self):
		if self.currentStartEnd == None:
			print 'Error: no range selected'
		else:
			self.currentGaussParams = None #reset gaussian params before we change the interval (just in case someone tries to save the interval and gaussians: we'd get the new interval with the gaussian parameters of the previous interval)
			print 'Range %3.2f --> %3.2f selected for gaussian fit' % (self.currentStartEnd[0], self.currentStartEnd[1])
			self.currentInterval = self.dataWithCountErr[self.currentStartEnd[0]:self.currentStartEnd[1]]
			print 'currentInterval set to {0}'.format(self.currentInterval)
			#self.currentInterval is the interval your gaussian will go on, you can change this with backgrounds as you want
			#SUBSTRACT linear BACKGROUND HERE
			(a,b,c) = getDefaultsForGaussianFit(self.currentInterval)
			showStartingValuesDialog({'a':a, 'b':b, 'c':c, 'iterations': 1000},self.calculateGaussian)
	def calculateGaussian(self, parameters):
		start_a = float(parameters['a'])
		start_b = float(parameters['b'])
		start_c = float(parameters['c'])
		max_iterations = int(parameters['iterations'])
		self.currentGaussParams = fitGaussianAndAddToPlot(self.currentInterval, [start_a,start_b,start_c], max_iterations, self.fig, self.axes)
	def addGaussianToList(self):
		if self.currentGaussParams == None or self.currentInterval == None:
			print 'Error, no gaussian fit calculated'
		else:
			(params, variance_matrix, fit_errors) = self.currentGaussParams
			self.peakData = self.peakData.withRow(params['b'], fit_errors['b'])
			self.gaussianFits.append({'params':params, 'variance_matrix':variance_matrix, 'fit_errors':fit_errors, 'interval':self.currentInterval})
			print 'Gaussian fit added to list with {0} and interval {1} --> {2}'.format(params,self.currentInterval[0],self.currentInterval[-1])
			#after adding to list, clear our temporary values
			self.currentGaussParams = None
			self.currentInterval = None
	def calibrateEnergy(self):
		showCorrelateEnergyDialog(self.peakData, self.processCalibratedEnergy)
	def processCalibratedEnergy(self, energyCalibrationData):
		self.peakData = TestData(['Peak','PeakErr'],[], []) #reset peak data
		#print [{	'params' : f['params'], 'fit_errors' : f['fit_errors'], 'energy' : f['energy'], 'interval' : getIntervalString(f['interval'])}for f in fitData]
		self.currentEnergyCalibrationFit = processAndPlotEnergyCalibrationData(energyCalibrationData)
	def saveEnergyCalibration(self):
		if self.currentEnergyCalibrationFit != None:
			fit = self.currentEnergyCalibrationFit
			f = open(energycalibrationparamsavefile, 'w')
			f.write('Params:\n{params}\n\nVariance matrix:\n{variance_matrix}\n\nFit errors:\n{fit_errors\n\n}'.format(fit))
			f.close()
			
			csvLines = [';'.join(row) for row in zip(fit['x'],fit['x_err'],fit['y'],fit['y_err'])]
			csvData = '\n'.join(csvLines)
			f = open(energycalibrationdatasavefile,'w')
			f.write(csvData)
			f.close()
		
	
	#Handle key presses
	def handle_key(self, event):
		if event.key in ['C', 'c'] and self.spanSelector == None:
			print 'Span selector activated'
			self.spanSelector = SpanSelector(self.axes, self.selectInterval, 'horizontal')
		elif event.key in ['C', 'c'] and self.spanSelector != None:
			print 'Span selector deactivated'
			self.spanSelector = None
		elif event.key in ['G','g']:
			self.choosecurrentStartEndForGaussianFit()
		elif event.key in ['A','a']:
			self.addGaussianToList()
		elif event.key in ['E','e']:
			self.calibrateEnergy()
		elif event.key in ['F','f']:
			self.saveEnergyCalibration()
		else:
			print 'Detected keypress {0}, unknown command'.format(event.key)



if __name__ == '__main__': #means it's only gonna work when run from the command line
	printHello()
	#execute this if this file gets executed
	rawData = getDataRows(config.datafile)
	background = getDataRows(config.backgroundfile)
	#calculate countErr:
	#rawData = sqrt(count_raw)
	#background = sqrt(count_back)
	#combined = sqrt( raw_err**2 + back_err**2 ) = sqrt(sqrt(count_raw)**2 + sqrt(count_back)**2) = sqrt(abs(count_raw) + abs(count_back))
	countErr = 	numpy.sqrt(
					numpy.add(
						numpy.absolute(rawData['Count']), numpy.absolute(background['Count'])
					)
				)
	#subtract real background
	correctedData = rawData.subtractFromColumn('Count', background)
	correctedDataWithCountErr = correctedData.withColumn('CountErr',countErr)
	MainGuiController().run(correctedDataWithCountErr, start=0, end=4096)













