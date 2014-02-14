from generalconfig import *

# Input configuration
background = r'g/2013.10.28-10:13_bkg_background_no source_28-10-2013_10u13_2785s.csv'
#see http://matplotlib.org/api/axes_api.html#matplotlib.axes.Axes.plot for plot formats
inputfiles = [   #add (r'filelocation', 'label', format) for each file to be processed (colors: b, g, r, c, m, y, k)
	(r'g/2013.10.23-16:29_data_23-10-2013_16u29_7160s.csv', 'Label 2', 'bo-'),
	(r'g/2013.10.29-11:46_data_st_10us_29-10-2013_11u46_3656s.csv', 'Label 1', 'go-'),
]
title = 'Put title here'
datastart = 0 #set to 0 to start from first channel
dataend = 4096 #set to a number most definitely higher than the max channel to get all (f.e. 99999999)'

# Plot configuration
plotwidth = 16
plotheight = 10

fontsize = 16
test_x_axis_label = 'Channel'
test_y_axis_label = 'Count'
test_x_majorticks = 300
test_x_minorticks = 100
