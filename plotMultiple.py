#!/usr/bin/python
import os, numpy, sys
import plotMultipleConfig as config
import matplotlib.pyplot as plt
if __name__ == '__main__':
	#Make sure it doesn't matter where things are executed from
	PROJECT_DIR = os.path.abspath(os.path.dirname(__file__))
	os.chdir(PROJECT_DIR)
	sys.path.append(PROJECT_DIR)
	sys.path.append(os.path.join(PROJECT_DIR,'codelibs')) #add files in codelibs
from plotting import createEmptyPlottingArea, addDataWithErrorBarsToPlot
from file import loadTestFileWithBackgroundAndCalculateCountErr

def printHello():
	print "Hello, I'm working!"

# See http://matplotlib.org/api/widgets_api.html for info on the widgets
#	Selector example (also deals with key press): http://matplotlib.org/examples/widgets/rectangle_selector.htmls
class MainGuiController(object):
	#Variables

	def init(self, start, end):
		(fig,axes) = createEmptyPlottingArea(config.test_x_axis_label, config.test_y_axis_label, x_majorticks=config.test_x_majorticks, x_minorticks=config.test_x_minorticks, x_length=end-start, fontsize = config.fontsize, figWidth=config.plotwidth, figHeight=config.plotheight)
		self.fig = fig
		self.axes = axes
		self.start = start
		self.end = end
		
	def addPlot(self, data, label, fmt, start=-1, end=-1):
		if start == -1:
			start = self.start
		if end == -1:
			end = self.end
		addDataWithErrorBarsToPlot(self.axes, data['Channel'][start:end], data['Count'][start:end], y_err=data['CountErr'][start:end], fmt=fmt, label=label)
	
	def generateLegend(self):
		self.axes.legend()
		
	def setTitle(self, title):
		self.axes.set_title(title)
		
	def show(self):
		plt.show()

	#Callback functions
	def addTestData(self): 
		pass
	def deleteLastPlot(self):
		pass
	
	#Handle key presses
	def handle_key(self, event):
		if event.key in ['A', 'a']:
			addTestData()
		elif event.key in ['D', 'd']:
			deleteLastPlot()
		else:
			print 'Detected keypress {0}, unknown command'.format(event.key)



if __name__ == '__main__':
	mgc = MainGuiController()
	mgc.init(config.datastart, config.dataend)
	mgc.setTitle(config.title)
	for (filepath, background, label, fmt) in config.inputfiles:
		data = loadTestFileWithBackgroundAndCalculateCountErr(filepath, background, config.durationRegex, config.rescaletoduration)
		mgc.addPlot(data, label, fmt)
	mgc.generateLegend()
	mgc.show()
