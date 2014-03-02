# Data set configuration
# Duration regex: regular expression to get duration out of filename
# Will look for underscore followed by a number, followed by s, followed by either another underscore or .csv
durationRegex = r'_(\d{2}\d*)s(_|\.csv)'

# Output files configuration
gaussianFitDataSuffix = 'gaussianFits'
gaussianFitDir = 'g/gaussianfits'
energyFitDataSuffix = 'energyFits'
energyFitCsvSuffix = 'energyFits'
energyFitDir = 'g/energycalibrations'
tabWidth = 4 #number of spaces a tab is expected to be, used for lining up values

# Debugging
debugfile = 'debug.txt' #to print things to large or unwieldy for commandline purposes (function is in common called debug)
