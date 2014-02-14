# Plot configuration
plotwidth = 16
plotheight = 10
errorbarplotformat = 'go' #green dots, see http://matplotlib.org/api/axes_api.html#matplotlib.axes.Axes.plot for plot formats
energybarplotformat = 'ro-'
fontsize = 16
fittedformat = 'ro'
standardplotformat = 'r-'

# Data set configuration
datastart = 0
dataend = 4096
#errordatafile = 'zero_counts.csv' #Warning: this will be overwritten each run (doesn't need to be though)
datafile = 'g/2013.10.29-11:46_data_st_10us_29-10-2013_11u46_3656s.csv'
backgroundfile = 'g/2013.10.28-10:13_bkg_background_no source_28-10-2013_10u13_2785s.csv'
# Data file format: yyyy.mm.dd-HH:MM_type_name_of_testrun_xxxxs.csv 
#	with yyyy.mm.dd-HH:MM the time of the run and yyyy year (4 digits), mm month (2 digits), dd day (2 digits), HH hour (2 digits 24h notation), MM minutes (2 digits), ssss seconds/100 (1-4 digits)
#	with type being data or bkg (data file or background file)
#	with xxxxx the duration of the test run in seconds (2 or more digits)
datafileformatregex = r'(\d{4}\.\d{2}\.\d{2}\-\d{2}:\d{2})_(data|bkg)_.*_(\d{2}\d*)s\.csv'
dateformat = '%Y.%m.%d-%H:%M' #see http://docs.python.org/2/library/time.html#time.strftime
energycalibrationparamsavefile = 'energy_calibration.txt'
energycalibrationdatasavefile = 'energy_calibration.csv'

# Output files configuration
gaussianFitDataSuffix = 'gaussianFits'
energyFitDataSuffix = 'energyFits'
energyFitCsvSuffix = 'energyFits'
tabWidth = 4 #number of spaces a tab is expected to be, used for lining up values

# Debugging
debugfile = 'debug.txt' #to print things to large or unwieldy for commandline purposes (function is in common called debug)
