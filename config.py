# Plot configuration
plotwidth = 16
plotheight = 10
errorbarplotformat = 'go' #green dots, see http://matplotlib.org/api/axes_api.html#matplotlib.axes.Axes.plot for plot formats
fontsize = 16
gaussianformat = 'r-'
standardplotformat = 'r-'

# Data set configuration
datastart = 0
dataend = 4096
errordatafile = 'zero_counts.csv' #Warning: this will be overwritten each run (doesn't need to be though)
datafile = 'g/st_10us_29-10-2013_11u46_3656s.csv'
backgroundfile = 'g/background_no source_28-10-2013_10u13_2785s.csv'
energycalibrationparamsavefile = 'energy_calibration.txt'
energycalibrationdatasavefile = 'energy_calibration.csv'

# Debugging
debugfile = 'debug.txt' #to print things to large or unwieldy for commandline purposes (function is in common called debug)
