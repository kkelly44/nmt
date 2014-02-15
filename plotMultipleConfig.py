from generalconfig import *

# Input configuration
background = r'g/12-12-2013_17u34_background_2283s_cg500_1us.csv'
# add (r'filelocation', 'label', format) for each file to be processed (colors: b, g, r, c, m, y, k)
# filelocation: the path to the testfile (relative to the python files or an absolute path)
# label: the label for the line (shwon in legend)
# format: the type and color of the line, see http://matplotlib.org/api/axes_api.html#matplotlib.axes.Axes.plot for plot formats
inputfiles = [   
	(r'g/16-12-2013_10u06_1800s_st1u_cg500_fg0_d42_ang45.csv', 'd42 ang45', 'bo-'),
	(r'g/16-12-2013_11u09_3613s_st1u_cg500_fg0_d42_ang90.csv', 'd42 ang90', 'go-'),
	(r'g/16-12-2013_11u49_2155s_st1u_cg500_fg0_67cm_45deg.csv', '67cm 45deg', 'ro-'),
]
title = 'Scale to 4000s'
datastart = 0 #set to 0 to start from first channel
dataend = 4096 #set to a number most definitely higher than the max channel to get all (f.e. 99999999)'
# Rescale all test data to a set number of seconds (set to 0 or a negative number to not rescale data)
rescaletoduration = 4000

# Plot configuration
plotwidth = 16
plotheight = 10

fontsize = 16
test_x_axis_label = 'Channel'
test_y_axis_label = 'Count'
test_x_majorticks = 300
test_x_minorticks = 100
