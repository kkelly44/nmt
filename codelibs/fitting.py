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
# See http://docs.scipy.org/doc/scipy/reference/generated/scipy.odr.Output.html
def fitFunctionOdr(x, y, x_err, y_err, fitFunction, startingParameters):
	model = odr.Model(fitFunction)
	mydata = odr.RealData(x, y, sx=x_err, sy=y_err)
	myodr = odr.ODR(mydata, model, beta0=startingParameters)
	myoutput = myodr.run()
	print myoutput.stopreason
	return myoutput
	
#def calculateOdrChiSquared(fitOutput):
#	 eps and delta would be needed if we wanted to calculate chi squared
#	eps = fitOutput.eps y
#	delta = fitOutput.delta x
#	 reduced chi squared is given as residual variance (multiple sources claim this is exactly the same)
#	 see http://mail.scipy.org/pipermail/scipy-user/2012-May/032207.html <-- this one also tells us how to calculate chi squared (not reduced)
#	 see for curve_fit http://stackoverflow.com/questions/14854339/in-scipy-how-and-why-does-curve-fit-calculate-the-covariance-of-the-parameter-es
#	 see also gnuplot: http://gnuplot.sourceforge.net/docs_4.2/node86.html
#	reduced_chi_square = fitOutput.res_var
#	return reduced_chi_square
	
#############################################################################################
### Extract from future version of scipy (0.11):                             ################
### https://github.com/scipy/scipy/blob/master/scipy/signal/_peak_finding.py ################
#############################################################################################

def _boolrelextrema(data, comparator,
                  axis=0, order=1, mode='clip'):
    """
Calculate the relative extrema of `data`.

Relative extrema are calculated by finding locations where
``comparator(data[n], data[n+1:n+order+1])`` is True.

Parameters
----------
data : ndarray
Array in which to find the relative extrema.
comparator : callable
Function to use to compare two data points.
Should take 2 numbers as arguments.
axis : int, optional
Axis over which to select from `data`. Default is 0.
order : int, optional
How many points on each side to use for the comparison
to consider ``comparator(n,n+x)`` to be True.
mode : str, optional
How the edges of the vector are treated. 'wrap' (wrap around) or
'clip' (treat overflow as the same as the last (or first) element).
Default 'clip'. See numpy.take

Returns
-------
extrema : ndarray
Boolean array of the same shape as `data` that is True at an extrema,
False otherwise.

See also
--------
argrelmax, argrelmin

Examples
--------
>>> testdata = numpy.array([1,2,3,2,1])
>>> _boolrelextrema(testdata, numpy.greater, axis=0)
array([False, False, True, False, False], dtype=bool)

"""
    if((int(order) != order) or (order < 1)):
        raise ValueError('Order must be an int >= 1')

    datalen = data.shape[axis]
    locs = numpy.arange(0, datalen)

    results = numpy.ones(data.shape, dtype=bool)
    main = data.take(locs, axis=axis, mode=mode)
    ############################################
    ### Changed xrange to arange ###############
    ############################################
    for shift in numpy.arange(1, order + 1):
        plus = data.take(locs + shift, axis=axis, mode=mode)
        minus = data.take(locs - shift, axis=axis, mode=mode)
        results &= comparator(main, plus)
        results &= comparator(main, minus)
        if(~results.any()):
            return results
    return results


def argrelmin(data, axis=0, order=1, mode='clip'):
    """
Calculate the relative minima of `data`.

.. versionadded:: 0.11.0

Parameters
----------
data : ndarray
Array in which to find the relative minima.
axis : int, optional
Axis over which to select from `data`. Default is 0.
order : int, optional
How many points on each side to use for the comparison
to consider ``comparator(n, n+x)`` to be True.
mode : str, optional
How the edges of the vector are treated.
Available options are 'wrap' (wrap around) or 'clip' (treat overflow
as the same as the last (or first) element).
Default 'clip'. See numpy.take

Returns
-------
extrema : tuple of ndarrays
Indices of the minima in arrays of integers. ``extrema[k]`` is
the array of indices of axis `k` of `data`. Note that the
return value is a tuple even when `data` is one-dimensional.

See Also
--------
argrelextrema, argrelmax

Notes
-----
This function uses `argrelextrema` with numpy.less as comparator.

Examples
--------
>>> x = numpy.array([2, 1, 2, 3, 2, 0, 1, 0])
>>> argrelmin(x)
(array([1, 5]),)
>>> y = numpy.array([[1, 2, 1, 2],
... [2, 2, 0, 0],
... [5, 3, 4, 4]])
...
>>> argrelmin(y, axis=1)
(array([0, 2]), array([2, 1]))

"""
    return argrelextrema(data, numpy.less, axis, order, mode)


def argrelmax(data, axis=0, order=1, mode='clip'):
    """
Calculate the relative maxima of `data`.

.. versionadded:: 0.11.0

Parameters
----------
data : ndarray
Array in which to find the relative maxima.
axis : int, optional
Axis over which to select from `data`. Default is 0.
order : int, optional
How many points on each side to use for the comparison
to consider ``comparator(n, n+x)`` to be True.
mode : str, optional
How the edges of the vector are treated.
Available options are 'wrap' (wrap around) or 'clip' (treat overflow
as the same as the last (or first) element).
Default 'clip'. See `numpy.take`.

Returns
-------
extrema : tuple of ndarrays
Indices of the maxima in arrays of integers. ``extrema[k]`` is
the array of indices of axis `k` of `data`. Note that the
return value is a tuple even when `data` is one-dimensional.

See Also
--------
argrelextrema, argrelmin

Notes
-----
This function uses `argrelextrema` with numpy.greater as comparator.

Examples
--------
>>> x = numpy.array([2, 1, 2, 3, 2, 0, 1, 0])
>>> argrelmax(x)
(array([3, 6]),)
>>> y = numpy.array([[1, 2, 1, 2],
... [2, 2, 0, 0],
... [5, 3, 4, 4]])
...
>>> argrelmax(y, axis=1)
(array([0]), array([1]))
"""
    return argrelextrema(data, numpy.greater, axis, order, mode)


def argrelextrema(data, comparator, axis=0, order=1, mode='clip'):
    """
Calculate the relative extrema of `data`.

.. versionadded:: 0.11.0

Parameters
----------
data : ndarray
Array in which to find the relative extrema.
comparator : callable
Function to use to compare two data points.
Should take 2 numbers as arguments.
axis : int, optional
Axis over which to select from `data`. Default is 0.
order : int, optional
How many points on each side to use for the comparison
to consider ``comparator(n, n+x)`` to be True.
mode : str, optional
How the edges of the vector are treated. 'wrap' (wrap around) or
'clip' (treat overflow as the same as the last (or first) element).
Default is 'clip'. See `numpy.take`.

Returns
-------
extrema : tuple of ndarrays
Indices of the maxima in arrays of integers. ``extrema[k]`` is
the array of indices of axis `k` of `data`. Note that the
return value is a tuple even when `data` is one-dimensional.

See Also
--------
argrelmin, argrelmax

Examples
--------
>>> x = numpy.array([2, 1, 2, 3, 2, 0, 1, 0])
>>> argrelextrema(x, numpy.greater)
(array([3, 6]),)
>>> y = numpy.array([[1, 2, 1, 2],
... [2, 2, 0, 0],
... [5, 3, 4, 4]])
...
>>> argrelextrema(y, numpy.less, axis=1)
(array([0, 2]), array([2, 1]))

"""
    results = _boolrelextrema(data, comparator,
                              axis, order, mode)
    return numpy.where(results)
