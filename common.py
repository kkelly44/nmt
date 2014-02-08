import numpy, math, config
from scipy.optimize import leastsq
import scipy.odr as odr
import matplotlib.pyplot as plt
from datetime import datetime
#################
# Data handling #
#################		

def extractDataRows(data, startChannel, endChannel):
	return [row for row in data if row['Channel'] >= startChannel and row['Channel'] <= endChannel]

def extractDataColumn(data, dataName): #returns an array of 1 element of the main data (extracts a single column into a new array)
	return [datum[dataName] for datum in data]

def getDataRowWithMaxForField(fieldName, data):
	def maxOfRows(row1,row2):
		if row1[fieldName] > row2[fieldName]:
			return row1
		else:
			return row2
	return reduce(maxOfRows,data,data[0]) #applies maxOfRows to each row in the array with row1 being the previous result of maxOfRows (first time data[0] is used) and row2 being the next element in the array


############
# Plotting #
############

def addFunctionToPlot(axes, xs, func, fmt=config.standardplotformat):
	ys = [func(x) for x in xs]
	axes.errorbar(xs, ys, fmt=fmt)

def addDataWithErrorBarsToPlot(axes, x, y, x_err=None, y_err=None, fmt=config.errorbarplotformat):
	'''Add plot with error bars to the given plot axes
		the error bar function:
		http://matplotlib.org/api/axes_api.html#matplotlib.axes.Axes.errorbar
		description of formats (line, dotted line, dots, ...):
		http://matplotlib.org/api/axes_api.html#matplotlib.axes.Axes.plot'''
	(plotline, caplines, barlinecols) = axes.errorbar(x, y, fmt = fmt, xerr=x_err, yerr = y_err)
	return (plotline, caplines, barlinecols) #Values on which matplotlib bases its plotting (should you need to fiddle with them)

def createEmptyPlottingArea(xAxisLabel, yAxisLabel, figWidth=config.plotwidth, figHeight=config.plotheight, x_majorticks = -1, x_minorticks = -1, x_length=1000, y_majorticks = -1, y_minorticks = -1, y_length=10000, fontsize = config.fontsize): 
	fig = plt.figure(figsize=(16, 10)) # open empty image
	ax = fig.add_subplot(111) #change the values to add more plots #add a (sub)plot
	
	ax.set_xlabel(xAxisLabel, fontsize = fontsize) #set axis name
	if x_majorticks != -1:
		ax.set_xticks(numpy.arange(0,x_length,x_majorticks), False) #set major ticks
	if x_minorticks != -1:
		ax.set_xticks(numpy.arange(0,x_length,x_minorticks), True) #set minor ticks

	ax.set_ylabel(yAxisLabel, fontsize = fontsize)
	if y_majorticks != -1:
		ax.set_yticks(numpy.arange(0,y_length,y_majorticks), False) #set major ticks
	if x_minorticks != -1:
		ax.set_yticks(numpy.arange(0,y_length,y_minorticks), True) #set minor ticks

	return (fig,ax)


#########################
# Fitting and functions #
#########################

def line(x, a, b):
	return x*a + b

def lineOdr(B, x):
	return B[0]*x + B[1]

def gaussian(x, a, b, c):
	val = a * numpy.exp(-(x - b)**2 / c**2)
	return val
	
def gaussianOdr(B, x):
	val = B[0] * numpy.exp(-(x - B[1])**2 / B[2]**2)
	return val

def fittedFunction(func, *parameters):
	def resultFunc(x):
		return func(x, *parameters)
	return resultFunc

#TODO: make this independant of testdata	
#def getDefaultsForGaussianFit(x,y): # beacuse 111 is not going to be a decent starting point, we feed it common sense starting values
#	# a should be max of count in interval, b should be channel of max count, c should be half of elements in interval
#	maxCount = getDataRowWithMaxForField('Count', interval)
#	a = maxCount['Count']
#	b = maxCount['Channel']
#	c = len(interval)/6
#	return (a,b,c)

def _general_function(params, xdata, ydata, function):
	return function(xdata, *params) - ydata

def _weighted_general_function(params, xdata, ydata, function, weights):
	return weights * (function(xdata, *params) - ydata)

def fitFunction(func, x, y, startingParameters, y_err=None, max_iterations=1000):
	'''Fit given function func to the data in x and y, taking y_err into consideration. Startingparameters are required.
		See http://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.leastsq.html for more options for least squares
		If extra options are needed. add them to the end of the function parameters with a default value (this makes them optional 
		and will avoid breaking existing code). If you don't know what to pick for default value, pick the one given in at the top
		of the page in leastsq.html (that's the one we've been using so far anyways for those options).
		Prepare input for leastsq function'''
	args = (numpy.array(x), numpy.array(y), func)
	if y_err is None:
		function_to_optimize = _general_function #gets func passed as an argument via args
	else:
		function_to_optimize = _weighted_general_function #gets func passed as an argument via args
		args += (1.0/numpy.asarray(y_err),) #add weights to args
	maxFuncEvaluations = (len(x)+1)*max_iterations

	#Call leastsq function
	try:
		(paramEstimates, paramCovariance, infodict, errmsg, ier) = leastsq(function_to_optimize, numpy.array(startingParameters), args=args, full_output=True, maxfev=maxFuncEvaluations)
	
		#Process results from leastsq function
		paramStdDev = paramCovariance
		paramStdDev = numpy.sqrt(numpy.diag(paramCovariance))
		success = ier in [1,2,3.4]
		if not success:
			debugMsg = errmsg
			debugMsg = debugMsg + '\n\n' + '--> when calling leastsq with: function_to_optimize\n, {0}\n, args={1}, full_output=True, maxfev={2}'.format(numpy.array(startingParameters),args, maxFuncEvaluations)
			debug(dbugMsg)
		return (paramEstimates, paramCovariance, paramStdDev, infodict, errmsg, success)
	except Exception as v: #catch error and try to save some useful info
		errmsg = 'Error when calling leastsq with: function_to_optimize\n, {0}\n, args=args, full_output=True, maxfev={1}'.format(numpy.array(startingParameters), maxFuncEvaluations)
		debugmsg = 'Error when calling leastsq with: function_to_optimize\n, {0}\n, args={1}, full_output=True, maxfev={2}'.format(numpy.array(startingParameters),args, maxFuncEvaluations)
		import traceback
		debugmsg = debugmsg + '\n\n' + traceback.format_exc() #print stacktrace
		debug(debugmsg)
		return ([],[],[],{},errmsg, False)

def fitFunctionWithDoubleErr(x, y, x_err, y_err, fitFunction, startingParameters):
	linear = odr.Model(fitFunction)
	mydata = odr.RealData(x, y, sx=x_err, sy=y_err)
	myodr = odr.ODR(mydata, linear, beta0=startingParameters)
	myoutput = myodr.run()
	return myoutput

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


################
# Experimental #
################

class TestDataException(Exception):
	pass

class TestData:
	def __init__(self, header, *data):
		if len(header) != len(data): #data is not a matrix with len(header) columns
			if len(zip(*data)) == len(header): #data is not a matrix with len(header) rows? (switch rows and columns and try again)
				self.__init__(header, *zip(*data))
			elif len(data) == 1: #someone just gave us a matrix instead of a set of rows or columns, just roll with it and see if the matrix is the correct size
				self.__init__(header, *data[0])
			else:
				debug('ERROR: number of header elements ({0}) not the same as number of columns ({1}).\nHeader: {2}\n\n Data (truncated to 25 rows):{3}\n\n'.format(len(header),len(data),header,recursiveSlice(data,25)))
				raise TestDataException('ERROR: number of header elements ({0}) not the same as number of columns ({1}). Expecting a X by {0} or {0} by X matrix for data. Can also be given as rows or columns'.format(len(header),len(data)))
		else:
			self.header = header
			self.length = len(data[0])
			if not reduce(lambda x,y: x and y == self.length, [len(col) for col in data], True):
				raise TestDataException('ERROR: columns not all same length {0}'.format(self.length))
			self._items = zip(*data)
		
	#function important for syntactic sugar and for internal workings
	def __getitem__(self, key):
		if isinstance(key, slice ):
			(start, end, step) = key.indices(len(self))
			return self.extractRows(self.header[0],start, end)
		elif isinstance( key, int ):
			return dict(zip(self.header,self._items[key]))
		elif isinstance( key, str ):	
			return self.getColumn(key)
	
	#function important for syntactic sugar
	def __len__(self):
		return self.length
			
	def addToColumn(self, fieldName, other):
		return self.applyFunctionToColumn(lambda x,y: x+y, fieldName, other)	
		
	def subtractFromColumn(self, fieldName, other):
		return self.applyFunctionToColumn(lambda x,y: x-y, fieldName, other)	
		
	
	#debug('Columns in withoutcolumn: \n {0} \n\n'.format(recursiveSlice(columns, 25)))
	
	def applyFunctionToColumn(self, func, fieldName, *args):
		c = self.getColumn(fieldName)
		seqLength = len(c)
		seqs = [c]
		for other in args:
			if isinstance(other, TestData ):
				if(fieldName in other.header):
					seqs.append(other.getColumn(fieldName))
				else:
					raise TestDataException('ERROR: Column {0} missing from one of the argument TestData'.format(fieldName))
			elif (isinstance(other, list) or isinstance(other, tuple)):
				seqs.append(other)
		allSameLength = reduce(lambda x,y: x and len(y)==seqLength, seqs, True)
		if allSameLength:
			c_ = [func(*x) for x in zip(*seqs)]
			return self.withoutColumn(fieldName).withColumn(fieldName, c_)
		else:
			raise TestDataException('ERROR: Arguments do not all have same length')
			
	def getHeader(self):
		return self.header
		
	#function important to internal workings
	def getColumn(self, fieldName):
		index = self.header.index(fieldName)
		return self.getColumns()[index]
	
	#function important to internal workings
	def getColumns(self):
		return zip(*self._items)
	
	#function important to internal workings
	def extractRows(self, fieldName, start, end, step=1):
		fieldColumn = self.getColumn(fieldName)
		s = fieldColumn.index(start)
		e = fieldColumn.index(end)
		extracted = zip(*self._items[s:e:step])
		return TestData(self.header, *extracted)
		
	#function important to internal workings
	def withRow(self, *row):
		if(len(row)==len(self.header)):
			print 'self._items', self._items
			if self._items == []:
				return TestData(self.header, *[[r] for r in row])
			else:
				items = self._items + [tuple(row)]
				print 'Items', items
				return TestData(self.header, *zip(*items))
		else:
			raise TestDataException('ERROR: number of header elements ({0}) not the same as number of columns ({1}) when adding row'.format(len(header),len(data)))
		
	def withColumn(self, fieldName, columnData):
		if len(columnData) != self.length:
			raise TestDataException('ERROR: added column has different length')
		header = self.header + [fieldName]
		data = self.getColumns() + [columnData]
		return TestData(header, *data)
			
	def renameColumn(self, fieldName, newName):
		index = self.header.index(fieldName)
		header = list(self.header)
		header[index] = newName
		data = self.getColumns()
		return TestData(header, *data)
		
	def withoutColumn(self, fieldName):
		index = self.header.index(fieldName)
		header = self.header[:index] + self.header[index+1:]
		columns = self.getColumns()
		data = columns[:index] + columns[index+1:]
		return TestData(header, *data)
		
	def concatenate(self, other):
		if isinstance( other, TestData ):
			if(self.header == other.header):
				c1 = self.getColumns()
				c2 = other.getColumns()
				if(len(c1) == len(c2)):
					c = [l1+l2 for (l1,l2) in zip(c1,c2)]
					return TestData(self.header, *c)
				else:
					raise TestDataException('ERROR: Trying to concatenate TestData with different number of data lists together')
			else:
				raise TestDataException('ERROR: Trying to concatenate TestData with different headers together')
		elif isinstance( other, sequence ):
			c1 = self.getColumns()
			c2 = other
			if(len(c1) == len(c2)):
				c = [l1+l2 for (l1,l2) in zip(c1,c2)]
				return TestData(self.header, *c)
			else:
				raise TestDataException('ERROR: Trying to concatenate sequence to TestData with different number of data lists')
		else:
			raise TestDataException('ERROR: Trying to concatenate object of type {0} to TestData object'.format(type(other)))

