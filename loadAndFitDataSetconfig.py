from generalconfig import *

# Input configuration
datafile = 'g/2013.10.29-11:46_data_st_10us_29-10-2013_11u46_3656s.csv'
backgroundfile = 'g/2013.10.28-10:13_bkg_background_no source_28-10-2013_10u13_2785s.csv'
datastart = 0 #set to 0 to start from first channel
dataend = 4096 #set to a number most definitely higher than the max channel to get all (f.e. 99999999)

# Plot configuration
plotwidth = 16
plotheight = 10
testdataplotformat = 'go' #green dots, see http://matplotlib.org/api/axes_api.html#matplotlib.axes.Axes.plot for plot formats
energyplotformat = 'go'
energyfitplotformat = 'ro-'
fontsize = 16
fittedformat = 'ro'
test_x_axis_label = 'Channel'
test_y_axis_label = 'Count'
test_x_majorticks = 300
test_x_minorticks = 100
energy_x_axis_label = 'Channel'
energy_y_axis_label = 'Energy'
