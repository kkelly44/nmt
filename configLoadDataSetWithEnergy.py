from generalconfig import *
#######################
# Input configuration #
#######################
datafile = 'g/2013.10.29-11:46_data_st_10us_29-10-2013_11u46_3656s.csv'
backgroundfile = 'g/2013.10.28-10:13_bkg_background_no source_28-10-2013_10u13_2785s.csv'
energycalibrationfile = '2013.10.29-11:46_data_st_10us_29-10-2013_11u46_3656senergyFits.csv'
datastart = 0 #set to 0 to start from first channel
dataend = 4096 #set to a number most definitely higher than the max channel to get all (f.e. 99999999)

######################
# Plot configuration #
######################
# General config
plotwidth = 16
plotheight = 10
fontsize = 16


# Plotting the data from  the testfiles and the gaussian fits
testdatatitle = 'Energy data and fits'
test_x_axis_label = 'Energy'
test_y_axis_label = 'Count'
test_x_majorticks = 10
test_x_minorticks = 2

testdataplotformat = 'go' #green dots, see http://matplotlib.org/api/axes_api.html#matplotlib.axes.Axes.plot for plot formats
testdatalabel = 'Experimental data'
gaussianfitformats = ['bo', 'ro', 'co', 'mo', 'yo', 'ko']
gaussianlabelbase = 'Gaussian fit from channel ' #code will add xxxx -> yyyy (with xxxx and yyyy the starting and ending channel of the interval for which the fit was calculated)
