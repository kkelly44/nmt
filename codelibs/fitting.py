from scipy.optimize import leastsq
import scipy.odr as odr
import numpy
from common import debug

#########################
# Fitting and functions #
#########################

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

def line(x, a, b):
	return x*a + b

def lineOdr(B, x):
	return B[0]*x + B[1]

def gaussian(x, a, b, c):
	val = a * numpy.exp(-(x - b)**2 / (2*(c**2)))
	return val

def gaussianOdr(B, x):	
	val = B[0] * numpy.exp(-(x - B[1])**2 / (2*(B[2]**2)))
	return val

def fittedOdrFunction(func, parameterVector):
	def resultFunc(x):
		return func(parameterVector, x)
	return resultFunc

def fittedFunction(func, *parameters):
	def resultFunc(x):
		return func(x, *parameters)
	return resultFunc
	
def getDefaultsForGaussianFit(x,y): # because 111 is not going to be a decent starting point, we feed it common sense starting values
	# a should be max of y, b should be x value corresponding to max y, c should be 1/6th of number of elements in interval
	a = max(y)
	b = x[y.index(a)]
	c = len(x)/6
	return (a,b,c)	

# Just to avoid defining functions twice	
# gaussianOdr = toOdrFunction(gaussian)
# gaussian = toNonOdrFunction(gaussianOdr)
def toOdrFunction(func):
	def odrFunc(B, x):
		return func(x, *B)
	return odrFunc

def toNonOdrFunction(odrFunc):
	def nonOdrFunc(x, *args):
		return odrFunc(args, x)
	return nonOdrFunc

def _general_function(params, xdata, ydata, function):
	return function(xdata, *params) - ydata

def _weighted_general_function(params, xdata, ydata, function, weights):
	return weights * (function(xdata, *params) - ydata)

def fitFunctionLeastSq(func, x, y, startingParameters, y_err=None, max_iterations=1000):
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

# See http://docs.scipy.org/doc/scipy/reference/generated/scipy.odr.ODR.html#scipy.odr.ODR
#  class scipy.odr.ODR(data, model, beta0=None, delta0=None, ifixb=None, ifixx=None, job=None, iprint=None, errfile=None, rptfile=None, ndigit=None, taufac=None, sstol=None, partol=None, maxit=None, stpb=None, stpd=None, sclb=None, scld=None, work=None, iwork=None)
def fitFunctionOdr(x, y, x_err, y_err, fitFunction, startingParameters):
	model = odr.Model(fitFunction)
	mydata = odr.RealData(x, y, sx=x_err, sy=y_err)
	myodr = odr.ODR(mydata, model, beta0=startingParameters)
	myoutput = myodr.run()
	return myoutput
