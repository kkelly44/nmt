# Data set configuration
# Data file format: yyyy.mm.dd-HH:MM_type_name_of_testrun_xxxxs.csv 
#	with yyyy.mm.dd-HH:MM the time of the run and yyyy year (4 digits), mm month (2 digits), dd day (2 digits), HH hour (2 digits 24h notation), MM minutes (2 digits), ssss seconds/100 (1-4 digits)
#	with type being data or bkg (data file or background file)
#	with xxxxx the duration of the test run in seconds (2 or more digits)
datafileformatregex = r'(\d{4}\.\d{2}\.\d{2}\-\d{2}:\d{2})_(data|bkg)_.*_(\d{2}\d*)s\.csv'
dateformat = '%Y.%m.%d-%H:%M' #see http://docs.python.org/2/library/time.html#time.strftime

# Output files configuration
gaussianFitDataSuffix = 'gaussianFits'
energyFitDataSuffix = 'energyFits'
energyFitCsvSuffix = 'energyFits'
tabWidth = 4 #number of spaces a tab is expected to be, used for lining up values

# Debugging
debugfile = 'debug.txt' #to print things to large or unwieldy for commandline purposes (function is in common called debug)
