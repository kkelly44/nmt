#!/usr/bin/python
import math, re, os, numpy, sys
import loadAndFitDataSetconfig as config
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
from file import loadTestFileWithBackgroundAndCalculateCountErr
from plotting import addFunctionToPlot, createEmptyPlottingArea, addDataWithErrorBarsToPlot
from interactiveGaussianFitter import InteractiveGaussianFitTestDataFigure

def printHello():
	print "Hello, I'm working!"

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

class MainGuiController(InteractiveGaussianFitTestDataFigure):
	#Variables
	currentEnergyCalibrationFit = None
	peakData = TestData(['Param','Peak','PeakErr'],[], [],[])
	
	def __init__(self, data, basefilename, start, end):
		super(MainGuiController, self).__init__(
			data, 
			'Channel',
			None,
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
			extraKeybindings = {'e': (self.calibrateEnergy,"'e' to start the Energy calibration (saves energy calibration and gaussian fits to file after calibration).")}, 
			config=config)
		
	def calibrateEnergy(self):
		if self.peakData == None:
			print 'Add a gaussian fit first, before trying to calibrate energy'
		else:
			showCorrelateEnergyDialog(self.peakData, self.processCalibratedEnergy)
	def processCalibratedEnergy(self, energyCalibrationData):
		self.peakData = TestData(['Param','Peak','PeakErr'],[], [],[]) #reset peak data
		#print [{	'params' : f['params'], 'fit_errors' : f['fit_errors'], 'energy' : f['energy'], 'interval' : getIntervalString(f['interval'])}for f in fitData]
		self.currentEnergyCalibrationFit = processAndPlotEnergyCalibrationData(energyCalibrationData)
		self.saveSelectedGaussianFits()
		self.saveEnergyCalibration()
	def saveEnergyCalibration(self):
		fit = self.currentEnergyCalibrationFit
		f = open(os.path.join(config.energyFitDir, self.basefilename + config.energyFitDataSuffix + '.txt'), 'w')
		f.write(fit.text(config.tabWidth))
		f.close()
		f = open(os.path.join(config.energyFitDir, self.basefilename + config.energyFitCsvSuffix + '.csv'), 'w')
		f.write(fit.params.text(fieldSeparator=';'))
		f.close()
		print 'Energy calibration saved'

if __name__ == '__main__': #means it's only gonna work when run from the command line
	#Start script
	datafilename = config.datafile
	bkgfilename = config.backgroundfile
	data = loadTestFileWithBackgroundAndCalculateCountErr(datafilename, bkgfilename, config.durationRegex)
	basefilename = os.path.basename(datafilename)[0:-4] #basename gets just the filename, [0:-4] gets the part without the extension
	mgc = MainGuiController(data, basefilename, config.datastart, config.dataend)
	mgc.printInstructions(intro="Remember: its:", prefix='\t')
	mgc.show()
