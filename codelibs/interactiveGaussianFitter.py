import numpy
from interactive import InteractiveFigure
from plotting import addDataWithErrorBarsToPlot, addSinglePlottingArea, addFunctionToPlot
from matplotlib.widgets import SpanSelector
from fitting import fittedOdrFunction, getDefaultsForGaussianFit, gaussianOdr, fitFunctionOdr, removeDC
from startingvaluesdialog import showStartingValuesDialog
from data import TestData, FitData

# Passing config is a hack TODO fix this more cleanly later
def fitGaussianAndAddToPlotOdr(interval, startingGaussianParameters, max_iterations, fig, axes, nb_of_fits, config):
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

# Passing config is a hack TODO fix this more cleanly later	
class InteractiveGaussianFitTestDataFigure(InteractiveFigure):
	#Variables
	testData = []
	currentStartEnd = None #last selected start and end with the spanselector
	currentInterval = None #last chosen interval
	currentGaussParams = None
	gaussianFits = [] #list of chosen intervals and fit parameters
	spanSelector = None #the thingie that helps you select a part of the graph
	axes = None # this is basically the plot
	
	def __init__(self, testData, basefilename, start, end, xAxisLabel, yAxisLabel, x_majorticks = -1, x_minorticks = -1, x_length=10000, y_majorticks = -1, y_minorticks = -1, y_length=10000, fontsize=14, extraKeybindings = None, config=None, figWidth=16, figHeight=10):
		self.testData = testData
		internalKeyBindings = {
			'c': (self.toggleSpanSelector, "'c' to start the selector. Drag and drop over the area. The selection will show up in commandline. You can keep selecting until the desired invertal is selected. Click C again to stop the selector (useful when zooming in).  You only need to click 'c' once to start the selector."),
			'g': (self.choosecurrentStartEndForGaussianFit,"'g' to run the Gaussian fit for the current selection. Press 'g' again without making a new selection to run again (you can change starting values and iterations). Select the next peak and press 'g'."),
			'a': (self.addGaussianToList,"'a' to Add the gaussian fit for later calculations."),
		}
		if extraKeybindings != None:
			keybindings = dict(internalKeyBindings.items() + extraKeybindings.items())
		else:
			keybindings = internalKeyBindings
		super(InteractiveGaussianFitTestDataFigure, self).__init__(keybindings, figsize=(figWidth, figHeight))
		self.axes = addSinglePlottingArea(self.fig, xAxisLabel, yAxisLabel, x_majorticks, x_minorticks, x_length, y_majorticks, y_minorticks, y_length, fontsize)
		self.testData = testData
		self.basefilename = basefilename
		self.config = config
		self.axes.set_title(config.testdatatitle)

		channel = testData['Channel'][start:end]
		count = testData['Count'][start:end]
		countErr = testData['CountErr'][start:end]

		addDataWithErrorBarsToPlot(self.axes, channel, count, y_err=countErr, fmt=config.testdataplotformat, label=config.testdatalabel)
		self.axes.legend()

	#Callback functions
	def toggleSpanSelector(self):
		if self.spanSelector == None:
			print 'Span selector activated'
			self.spanSelector = SpanSelector(self.axes, self.selectInterval, 'horizontal')
		else:
			print 'Span selector deactivated'
			self.spanSelector = None
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
			self.currentInterval = self.testData.extractRows(self.currentStartEnd[0],self.currentStartEnd[1], byFieldName='Channel')
			#print 'currentInterval set to \n {0}'.format(self.currentInterval)
			(a,b,c) = getDefaultsForGaussianFit(x = self.currentInterval['Channel'], y = self.currentInterval['Count'])
			showStartingValuesDialog({'a':a, 'b':b, 'c':c, 'iterations': 1000},self.calculateGaussian)
	def calculateGaussian(self, parameters):
		start_a = float(parameters['a'])
		start_b = float(parameters['b'])
		start_c = float(parameters['c'])
		max_iterations = int(parameters['iterations'])
		self.currentGaussParams = fitGaussianAndAddToPlotOdr(self.currentInterval, [start_a,start_b,start_c], max_iterations, self.fig, self.axes, nb_of_fits=len(self.gaussianFits), config = self.config)
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
	def saveSelectedGaussianFits(self):
		config = self.config
		f = open(self.basefilename + config.gaussianFitDataSuffix + '.txt', 'w')
		for fit in self.gaussianFits:
			(fitdata, countsum) = fit
			f.write(fitdata.text(config.tabWidth))
			f.write('\n\n')
			f.write('Area under selected interval: {0}'.format(countsum))
			f.write('\n\n\n')
		f.close()
		print 'Selected gaussian fits saved'
