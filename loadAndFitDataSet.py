#!/usr/bin/python
import math, re, os, numpy, sys
import loadAndFitDataSetconfig as config
import matplotlib.pyplot as plt
from datetime import datetime
from scipy.optimize import curve_fit
from matplotlib.widgets import Button, SpanSelector, RectangleSelector
if __name__ == '__main__':
	#Make sure it doesn't matter where things are executed from
	PROJECT_DIR = os.path.abspath(os.path.dirname(__file__))
	os.chdir(PROJECT_DIR)
	sys.path.append(PROJECT_DIR)
	sys.path.append(os.path.join(PROJECT_DIR,'codelibs')) #add files in codelibs
from startingvaluesdialog import showStartingValuesDialog
from correlateenergydialog import showCorrelateEnergyDialog
from common import isNotEmptyString, debug
from fitting import fittedOdrFunction, getDefaultsForGaussianFit, lineOdr, gaussianOdr, fitFunctionOdr, fittedFunction, fitFunctionLeastSq, gaussian, line, removeDC
from data import TestData, FitData
from file import loadTestFileWithBackgroundAndCalculateCountErr
from plotting import addFunctionToPlot, createEmptyPlottingArea, addDataWithErrorBarsToPlot

def printHello():
	print "Hello, I'm working!"
	print "Remember: its:"
	print "\t C to start the selector. Drag and drop over the area. The selection will show up in commandline. You can keep selecting until the desired invertal is selected. Click C again to stop the selector (useful when zooming in)."
	print "\t G to run the Gaussian fit for the current selection. Press G again without making a new selection to run again (you can change starting values and iterations)"
	print "\t \t Select the next peak and press G. You only need to click C once to start the selector."
	print "\t A to Add the gaussian fit calculations."
	print "\t E to start the Energy calibration (saves energy calibration and gaussian fits to file)."
	print "\t S will open a dialog to save the plot."

#def getDefaultsForGaussianFit(interval): # beacuse 111 is not going to be a decent starting point, we feed it common sense starting values
#	# a should be max of count in interval, b should be channel of max count, c should be half of elements in interval
#	maxCount = getDataRowWithMaxForField('Count', interval)
#	a = maxCount['Count']
#	b = maxCount['Channel']
#	c = len(interval)/6
#	return (a,b,c)

def plotTestData(dataWithCountErr, start, end): 
	(fig, axes) = createEmptyPlottingArea(config.test_x_axis_label, config.test_y_axis_label, x_majorticks=config.test_x_majorticks, x_minorticks=config.test_x_minorticks, x_length=end-start, fontsize = config.fontsize, figWidth=config.plotwidth, figHeight=config.plotheight)

	axes.set_title(config.testdatatitle)

	channel = dataWithCountErr['Channel'][start:end]
	count = dataWithCountErr['Count'][start:end]
	countErr = dataWithCountErr['CountErr'][start:end]

	addDataWithErrorBarsToPlot(axes, channel, count, y_err=countErr, fmt=config.testdataplotformat, label=config.testdatalabel)
	axes.legend()
	return (fig,axes)

	
#def fitGaussianAndAddToPlotLeastSq(interval, startingGaussianParameters, max_iterations, fig, axes):
#	x = interval['Channel']
#	y = interval['Count']
#	x_err = None #Just making it explicit that we don't have an x_err at this point
#	y_err = interval['CountErr']
#	
#	(x,y,x_err,y_err) = removeDC(x,y,x_err,y_err)
#	countSum = numpy.sum(y)
#	
#	(popt, pcov, fit_errors, infodict, errmsg, success) = fitFunctionLeastSq(gaussian, x, y, startingGaussianParameters, y_err=y_err, max_iterations=max_iterations)
#	if success:
#		(a,b,c) = popt
#		(err_a, err_b, err_c) = fit_errors
#		gaussParams = ({'a':a, 'b':b, 'c':c},pcov,{'a':err_a, 'b':err_b, 'c':err_c},countSum)
#		(params, variance_matrix, fit_errors) = gaussParams
#		print 'params: {0}'.format(params)
#		print 'fit_errors: {0}'.format(fit_errors)
#		fittedGaussian = fittedFunction(gaussian,a,b,c)
#		addFunctionToPlot(axes, interval['Channel'], fittedGaussian, fmt=config.fittedformat)
#		fig.show()
#		return gaussParams
#	else:
#		print 'Error creating gaussian fit: {0}'.format(errmsg)
#		return None

def fitGaussianAndAddToPlotOdr(interval, startingGaussianParameters, max_iterations, fig, axes, nb_of_fits):
	x = interval['Channel']
	y = interval['Count']
	x_err = None #Just making it explicit that we don't have an x_err at this point
	y_err = interval['CountErr']
	
	(x,y,x_err,y_err) = removeDC(x,y,x_err,y_err)
	countSum = numpy.sum(y)
	
	output = fitFunctionOdr(x, y, x_err, y_err, fitFunction=gaussianOdr, startingParameters=startingGaussianParameters)
	params = output.beta
	param_std_dev = output.sd_beta #seems to calculated this for us already	
	print 'Params: ', params, '\nParam Std Dev: ', param_std_dev
#	(a,b,c) = params
#	(err_a, err_b, err_c) = fit_errors
	gaussParams = FitData(TestData(['Param','Value','Std Dev'], ['a','b','c'], params, param_std_dev), output.cov_beta, interval, 'Channel', residualVariance=output.res_var, inverseConditionNumber=output.inv_condnum, relativeError=output.rel_error, haltingReasons='\n'.join(output.stopreason))
#	gaussParams = ({'a':a, 'b':b, 'c':c},variance_matrix,{'a':err_a, 'b':err_b, 'c':err_c},countSum)
	fittedGaussian = fittedOdrFunction(gaussianOdr, params)
	addFunctionToPlot(axes, interval['Channel'], fittedGaussian, fmt=config.gaussianfitformats[nb_of_fits%len(config.gaussianfitformats)], label=config.gaussianlabelbase+'{0} --> {1}'.format(interval[0]['Channel'],interval[-1]['Channel']))
	axes.legend()
	fig.show()
	return (gaussParams, countSum)

def processAndPlotEnergyCalibrationData(energyCalibrationData):
	x = energyCalibrationData['Peak']
	x_err = energyCalibrationData['PeakErr']
	y = energyCalibrationData['Energy']
	y_err = energyCalibrationData['EnergyErr']
	(fig, axes) = createEmptyPlottingArea(config.energy_x_axis_label, config.energy_y_axis_label, fontsize = config.fontsize, figWidth=config.plotwidth, figHeight=config.plotheight)
	axes.set_title(config.energytitle)
	addDataWithErrorBarsToPlot(axes, x, y, x_err=x_err, y_err=y_err, fmt=config.energyplotformat, label=config.energyplotlabel)
	axes.legend()
	fig.show()
	
	#find fit for energy calibration
	output = fitFunctionOdr(x, y, x_err, y_err, fitFunction=lineOdr, startingParameters=[0.2,10.0])
	
	params = output.beta
	param_std_dev = output.sd_beta #seems to calculated this for us already
	
	print (params, param_std_dev)
	energyCalibrationFit = FitData(TestData(['Param','Value','Std Dev'], ['a','b'], params, param_std_dev), output.cov_beta, energyCalibrationData, 'Peak', residualVariance=output.res_var, inverseConditionNumber=output.inv_condnum, relativeError=output.rel_error, haltingReasons='\n'.join(output.stopreason))
	
	(a,b) = params #fits for line
	fittedLine = fittedOdrFunction(lineOdr, params)
	addFunctionToPlot(axes, x, fittedLine, config.energyfitplotformat, label=config.energyfitplotlabel)
	axes.legend()
	fig.show()
	return energyCalibrationFit

# See http://matplotlib.org/api/widgets_api.html for info on the widgets
#	Selector example (also deals with key press): http://matplotlib.org/examples/widgets/rectangle_selector.htmls
class MainGuiController(object):
	#Variables
	currentStartEnd = None #last selected start and end with the spanselector
	currentInterval = None #last chosen interval
	currentGaussParams = None
	currentEnergyCalibrationFit = None
	gaussianFits = [] #list of chosen intervals and fit parameters
	spanSelector = None #the thingie that helps you select a part of the graph
	fig = None # the figure on which the plot is drawn
	axes = None # this is basically the plot
	dataWithCountErr = [] #our data (Channel, Count, CountErr)
	peakData = None

	def run(self, dataWithCountErr, basefilename, start, end):
		(fig,axes) = plotTestData(dataWithCountErr, start, end) #(data, save file name, start range data, end range data)
		self.fig = fig
		self.axes = axes
		self.dataWithCountErr = dataWithCountErr
		self.basefilename = basefilename
		fig.canvas.mpl_connect('key_press_event', self.handle_key) #make it so we handle keypress events
		self.peakData = TestData(['Param','Peak','PeakErr'],[], [],[])
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
			self.currentInterval = self.dataWithCountErr.extractRows(self.currentStartEnd[0],self.currentStartEnd[1], byFieldName='Channel')
			#print 'currentInterval set to \n {0}'.format(self.currentInterval)
			(a,b,c) = getDefaultsForGaussianFit(x = self.currentInterval['Channel'], y = self.currentInterval['Count'])
			showStartingValuesDialog({'a':a, 'b':b, 'c':c, 'iterations': 1000},self.calculateGaussian)
	def calculateGaussian(self, parameters):
		start_a = float(parameters['a'])
		start_b = float(parameters['b'])
		start_c = float(parameters['c'])
		max_iterations = int(parameters['iterations'])
		self.currentGaussParams = fitGaussianAndAddToPlotOdr(self.currentInterval, [start_a,start_b,start_c], max_iterations, self.fig, self.axes, nb_of_fits=len(self.gaussianFits))
	def addGaussianToList(self):
		if self.currentGaussParams == None or self.currentInterval == None:
			print 'Error, no gaussian fit calculated'
		else:
			(fitData, countSum) = self.currentGaussParams
			self.peakData = self.peakData.withRow(fitData.params.extractRow('b','Param'))
			self.gaussianFits.append((fitData, countSum))
			print 'Gaussian fit added to list with {0} and interval {1} --> {2}'.format(fitData.params['Value'],self.currentInterval[0],self.currentInterval[-1])
			#after adding to list, clear our temporary values
			self.currentGaussParams = None
			self.currentInterval = None
	def calibrateEnergy(self):
		showCorrelateEnergyDialog(self.peakData, self.processCalibratedEnergy)
	def processCalibratedEnergy(self, energyCalibrationData):
		self.peakData = TestData(['Param','Peak','PeakErr'],[], [],[]) #reset peak data
		#print [{	'params' : f['params'], 'fit_errors' : f['fit_errors'], 'energy' : f['energy'], 'interval' : getIntervalString(f['interval'])}for f in fitData]
		self.currentEnergyCalibrationFit = processAndPlotEnergyCalibrationData(energyCalibrationData)
		self.saveSelectedGaussianFits()
		self.saveEnergyCalibration()
	def saveSelectedGaussianFits(self):
		f = open(self.basefilename + config.gaussianFitDataSuffix + '.txt', 'w')
		for fit in self.gaussianFits:
			(fitdata, countsum) = fit
			f.write(fitdata.text(config.tabWidth))
			f.write('\n\n')
			f.write('Area under selected interval: {0}'.format(countsum))
			f.write('\n\n\n')
		f.close()
		print 'Selected gaussian fits saved'
			
	def saveEnergyCalibration(self):
		fit = self.currentEnergyCalibrationFit
		f = open(self.basefilename + config.energyFitDataSuffix + '.txt', 'w')
		f.write(fit.text(config.tabWidth))
		f.close()
		f = open(self.basefilename + config.energyFitCsvSuffix + '.csv', 'w')
		f.write(fit.params.text(fieldSeparator=';'))
		f.close()
		print 'Energy calibration saved'
	
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
	#Start script
	printHello()
	datafilename = config.datafile
	bkgfilename = config.backgroundfile
	data = loadTestFileWithBackgroundAndCalculateCountErr(datafilename, bkgfilename, config.durationRegex)
	basefilename = os.path.basename(datafilename)[0:-4] #basename gets just the filename, [0:-4] gets the part without the extension
	MainGuiController().run(data, basefilename, start=config.datastart, end=config.dataend)
