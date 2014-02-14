import matplotlib.pyplot as plt
import numpy

############
# Plotting #
############

def addFunctionToPlot(axes, xs, func, fmt, label=None):
	ys = [func(x) for x in xs]
	axes.errorbar(xs, ys, fmt=fmt, label=label)

def addDataWithErrorBarsToPlot(axes, x, y, x_err=None, y_err=None, fmt='-', label=None):
	'''Add plot with error bars to the given plot axes
		the error bar function:
		http://matplotlib.org/api/axes_api.html#matplotlib.axes.Axes.errorbar
		description of formats (line, dotted line, dots, ...):
		http://matplotlib.org/api/axes_api.html#matplotlib.axes.Axes.plot'''
	(plotline, caplines, barlinecols) = axes.errorbar(x, y, fmt = fmt, xerr=x_err, yerr = y_err, label=label)
	return (plotline, caplines, barlinecols) #Values on which matplotlib bases its plotting (should you need to fiddle with them)

def createEmptyPlottingArea(xAxisLabel, yAxisLabel, figWidth=16, figHeight=10, x_majorticks = -1, x_minorticks = -1, x_length=1000, y_majorticks = -1, y_minorticks = -1, y_length=10000, fontsize=14): 
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
