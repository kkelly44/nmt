#!/usr/bin/python
import math, re, os, numpy, sys
import configLoadDataSetWithEnergy as config
import matplotlib.pyplot as plt
from datetime import datetime
from scipy.optimize import curve_fit
if __name__ == '__main__':
	#Make sure it doesn't matter where things are executed from
	PROJECT_DIR = os.path.abspath(os.path.dirname(__file__))
	os.chdir(PROJECT_DIR)
	sys.path.append(PROJECT_DIR)
	sys.path.append(os.path.join(PROJECT_DIR,'codelibs')) #add files in codelibs
from correlateenergydialog import showCorrelateEnergyDialog
from common import isNotEmptyString, debug
from fitting import fittedOdrFunction, lineOdr, fitFunctionOdr
from data import TestData, FitData
from file import loadTestFileAndCalculateEnergy
from plotting import addFunctionToPlot, createEmptyPlottingArea, addDataWithErrorBarsToPlot
from interactiveGaussianFitter import InteractiveGaussianFitTestDataFigure

def printHello():
	print "Hello, I'm working!"

class MainGuiController(InteractiveGaussianFitTestDataFigure):
	
	def __init__(self, data, basefilename, start, end):
		super(MainGuiController, self).__init__(
			data, 
			'Energy',
			'EnergyErr',
			'Count',
			'CountErr',
			basefilename, 
			start, 
			end, 
			config.test_x_axis_label, 
			config.test_y_axis_label, 
			x_majorticks=config.test_x_majorticks, 
			x_minorticks=config.test_x_minorticks, 
			x_length=end-start, 
			fontsize = config.fontsize, 
			figWidth=config.plotwidth, 
			figHeight=config.plotheight, 
			config=config)

if __name__ == '__main__': #means it's only gonna work when run from the command line
	#Start script
	printHello()
	datafilename = config.datafile
	bkgfilename = config.backgroundfile
	energycalibrationfilename = config.energycalibrationfile
	data = loadTestFileAndCalculateEnergy(datafilename, bkgfilename, energycalibrationfilename, config.durationRegex)
	basefilename = os.path.basename(datafilename)[0:-4] #basename gets just the filename, [0:-4] gets the part without the extension
	mgc = MainGuiController(data, basefilename, config.datastart, config.dataend)
	mgc.printInstructions(intro="Remember: its:", prefix='\t')
	mgc.show()
