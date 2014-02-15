from plotting import createFigure
import matplotlib.pyplot as plt

# See http://matplotlib.org/api/widgets_api.html for info on the widgets
#	Selector example (also deals with key press): http://matplotlib.org/examples/widgets/rectangle_selector.htmls
class InteractiveFigure(object):
	#Variables
	keybindings = {} #Expected format: {'key1':(function, description), 'key2':(function, description), ...}
	fig = None
	
	
	def __init__(self, keybindings, *figargs, **figkwargs):
		self.keybindings = keybindings
		fig = createFigure(*figargs, **figkwargs)
		self.fig = fig
		fig.canvas.mpl_connect('key_press_event', self.handle_key) #make it so we handle keypress events
		
	#Handle key presses
	def handle_key(self, event):
		if event.key in self.keybindings:
			self.keybindings[event.key][0]()
		else:
			print 'Detected keypress {0}, unknown command'.format(event.key)
			
	def printInstructions(self, intro='', prefix=''):
		print intro
		for (f, desc) in self.keybindings.values():
			print prefix, desc
		self.printDefaultInstructions(prefix)
	
	def printDefaultInstructions(self, prefix=''):
		print prefix, "'s' will open a dialog to save the plot."
		
	def show(self):
		plt.show()


# Function in form: func(B, x) with B a vector of parameters
# Add label to update or create the legend (leave empty to not update or create the legend)
def fitFunctionAndAddToPlot(function, x, y, startingParameters, max_iterations, fig, axes, fmt, x_err=None, y_err=None, label=None):
	x = interval['Channel']
	y = interval['Count']
	x_err = None #Just making it explicit that we don't have an x_err at this point
	y_err = interval['CountErr']
	
	#(x,y,x_err,y_err) = removeDC(x,y,x_err,y_err)
	countSum = numpy.sum(y)
	
	output = fitFunctionOdr(x, y, x_err, y_err, fitFunction=function, startingParameters=startingParameters)
	params = output.beta
	param_std_dev = output.sd_beta #seems to calculated this for us already	
	print 'Params: ', params, '\nParam Std Dev: ', param_std_dev
	gaussParams = FitData(TestData(['Param','Value','Std Dev'], ['a','b','c'], params, param_std_dev), output.cov_beta, interval, 'Channel', residualVariance=output.res_var, inverseConditionNumber=output.inv_condnum, relativeError=output.rel_error, haltingReasons='\n'.join(output.stopreason))
	fittedFunction = fittedOdrFunction(function, params)
	addFunctionToPlot(axes, interval['Channel'], fittedFunction, fmt=config.gaussianfitformats[nb_of_fits%len(config.gaussianfitformats)], label=config.gaussianlabelbase+'{0} --> {1}'.format(interval[0]['Channel'],interval[-1]['Channel']))
	axes.legend()
	fig.show()
	return (gaussParams, countSum)
	
	
