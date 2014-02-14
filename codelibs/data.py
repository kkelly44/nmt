import numpy, config
from common import padWithTabsToLength, debug
	
################################
# Internal data representation #
################################

class FitData:
	# Params is expected to be an instance of type TestData (first column could be param names if you want them printed in the text function). Example header: ['Param','Value','Error']
	def __init__(self, params, covariance_matrix, interval, x_field, residualVariance, inverseConditionNumber, relativeError, haltingReasons):
		self.params = params
		self.covariance_matrix = covariance_matrix
		self.interval = interval
		self.x_field = x_field
		self.residualVariance = residualVariance
		self.inverseConditionNumber = inverseConditionNumber
		self.relativeError = relativeError
		self.haltingReasons = haltingReasons
	def intervalText(self):
		return 'Interval: {0} -> {1}'.format(self.interval[0][self.x_field], self.interval[-1][self.x_field])
	def informationTexts(self):
		return '''Residual variance: {0}
			'Inverse condition number: {1}
			'Relative error in function values: {2}
			'Reason(s) for Halting: {3}'''.format(self.residualVariance, self.inverseConditionNumber, self.relativeError, self.haltingReasons)
	def paramText(self, tabWidth):
		return self.params.textTabOutlined(tabWidth)
	def covarianceText(self):
		return 'Covariance matrix: \n{0}'.format('\n'.join(['\t'.join([str(el) for el in row]) for row in self.covariance_matrix]))
	def text(self, tabWidth):
		return self.intervalText()+'\n'+self.informationTexts()+'\n'+self.covarianceText()+'\n\n'+self.paramText(tabWidth)
		

class TestDataException(Exception):
	pass

# Takes a header and 
#	either a set of columns e.g. t = TestData(['head1','head2'],column1,column2) with the columns having the same length and the number of columns equal to the number of elements in the header
#	or a set of rows e.g. t = TestData(['head1','head2'],row1,row2,row3,row4) with all rows having 2 elements
# WARNING: will take *data as columns in case the number of rows is equal to the number of columns in data (and equal to the length of the header) e.g. TestData(['head1','head2'],row1,row2) would interpret the data as TestData(['head1','head2'],column1,column2)
class TestData:
	def __init__(self, header, *data):
		if len(header) != len(data): #data is not a matrix with len(header) columns
			if len(zip(*data)) == len(header): #data is a matrix with len(header) rows? (switch rows and columns and try again)
				self.__init__(header, *zip(*data))
			elif len(data) == 1: #someone just gave us a matrix instead of a set of rows or columns, just roll with it and see if the matrix is the correct size
				self.__init__(header, *data[0])
			else:
				debug('ERROR: number of header elements ({0}) not the same as number of columns ({1}).\nHeader: {2}\n\n Data (truncated to 25 rows):{3}\n\n'.format(len(header),len(data),header,recursiveSlice(data,25)))
				raise TestDataException('ERROR: number of header elements ({0}) not the same as number of columns ({1}). Expecting a X by {0} or {0} by X matrix for data. Can also be given as rows or columns'.format(len(header),len(data)))
		else:
			self.header = header
			self.length = len(data[0])
			if not reduce(lambda x,y: x and y == self.length, [len(col) for col in data], True):
				raise TestDataException('ERROR: columns not all same length {0}'.format(self.length))
			self._items = zip(*data)
		
	#function important for syntactic sugar and for internal workings
	def __getitem__(self, key):
		if isinstance(key, slice ):
			(start, end, step) = key.indices(len(self))
			return self.extractRows(start, end)
		elif isinstance( key, int ):
			return self.extractRow(key, returnDict=True)
		elif isinstance( key, str ):	
			return self.getColumn(key)
	
	#function important for syntactic sugar
	def __len__(self):
		return self.length
			
	def addToColumn(self, fieldName, other):
		return self.applyFunctionToColumn(lambda x,y: x+y, fieldName, other)	
		
	def subtractFromColumn(self, fieldName, other):
		return self.applyFunctionToColumn(lambda x,y: x-y, fieldName, other)	
		
	
	#debug('Columns in withoutcolumn: \n {0} \n\n'.format(recursiveSlice(columns, 25)))
	
	def applyFunctionToColumn(self, func, fieldName, *args):
		c = self.getColumn(fieldName)
		seqLength = len(c)
		seqs = [c]
		for other in args:
			if isinstance(other, TestData ):
				if(fieldName in other.header):
					seqs.append(other.getColumn(fieldName))
				else:
					raise TestDataException('ERROR: Column {0} missing from one of the argument TestData'.format(fieldName))
			elif hasattr(other, "__iter__") or hasattr(other, "__getitem__"):
				seqs.append(other)
			else:
				print 'WARNING: Expecting some type of iterable, got: {1} of type {0}'.format(type(other), other)
		allSameLength = reduce(lambda x,y: x and len(y)==seqLength, seqs, True)
		if allSameLength:
			c_ = [func(*x) for x in zip(*seqs)]
			return self.withoutColumn(fieldName).withColumn(fieldName, c_)
		else:
			raise TestDataException('ERROR: Arguments do not all have same length')
			
	def getHeader(self):
		return self.header
		
	def getNbColumns(self):
		return len(self.header)
		
	#function important to internal workings
	def getColumn(self, fieldName):
		index = self.header.index(fieldName)
		return self.getColumns()[index]
	
	#function important to internal workings
	def getColumns(self):
		return zip(*self._items)
		
	def getRows(self):
		return self._items
	
	#function important to internal workings
	#unpredictable results if the column indicated by fieldname is not monotonously increasing
	def extractRows(self, start, end, byFieldName=None, step=1):
		if byFieldName == None:
			s = start
			e = end
		else:
			fieldColumn = self.getColumn(byFieldName)
			s = fieldColumn.index(start)
			e = fieldColumn.index(end)
		extracted = zip(*self._items[s:e:step])
		return TestData(self.header, *extracted)
	
	#function important to internal workings	
	def extractRow(self, value, byFieldName=None, returnDict=False):
		if byFieldName == None:
			i = value
		else:
			fieldColumn = self.getColumn(byFieldName)
			i = fieldColumn.index(value)
		if returnDict:
			return dict(zip(self.header,self._items[i]))
		else:
			return self._items[i]
		
		
	#function important to internal workings
	def withRow(self, *row):
		if len(row) == 1 and len(self.header) != 1: #someone just gave us an array instead of multiple arguments
			return self.withRow(*row[0])
		if(len(row)==len(self.header)):
			print 'self._items', self._items
			if self._items == []:
				return TestData(self.header, *[[r] for r in row])
			else:
				items = self._items + [tuple(row)]
				print 'Items', items
				return TestData(self.header, *zip(*items))
		else:
			raise TestDataException('ERROR: number of header elements ({0}) not the same as number of columns ({1}) when adding row'.format(len(self.header),len(row)))
		
	def withColumn(self, fieldName, columnData):
		if len(columnData) != self.length:
			raise TestDataException('ERROR: added column has different length')
		header = self.header + [fieldName]
		data = self.getColumns() + [columnData]
		return TestData(header, *data)
			
	def renameColumn(self, fieldName, newName):
		index = self.header.index(fieldName)
		header = list(self.header)
		header[index] = newName
		data = self.getColumns()
		return TestData(header, *data)
		
	def withoutColumn(self, fieldName):
		index = self.header.index(fieldName)
		header = self.header[:index] + self.header[index+1:]
		columns = self.getColumns()
		data = columns[:index] + columns[index+1:]
		return TestData(header, *data)
		
	def concatenate(self, other):
		if isinstance( other, TestData ):
			if(self.header == other.header):
				c1 = self.getColumns()
				c2 = other.getColumns()
				if(len(c1) == len(c2)):
					c = [l1+l2 for (l1,l2) in zip(c1,c2)]
					return TestData(self.header, *c)
				else:
					raise TestDataException('ERROR: Trying to concatenate TestData with different number of data lists together')
			else:
				raise TestDataException('ERROR: Trying to concatenate TestData with different headers together')
		elif isinstance( other, sequence ):
			c1 = self.getColumns()
			c2 = other
			if(len(c1) == len(c2)):
				c = [l1+l2 for (l1,l2) in zip(c1,c2)]
				return TestData(self.header, *c)
			else:
				raise TestDataException('ERROR: Trying to concatenate sequence to TestData with different number of data lists')
		else:
			raise TestDataException('ERROR: Trying to concatenate object of type {0} to TestData object'.format(type(other)))
	
	def text(self, fieldSeparator='\t', rowSeparator='\n', showHeader=True):
		result = ''
		if showHeader:
			result = result + fieldSeparator.join(self.getHeader()) + rowSeparator
		result = result + rowSeparator.join([fieldSeparator.join(row) for row in [[str(el) for el in r] for r in self.getRows()]])
		return result
	
	def textTabOutlined(self, tabWidth, rowSeparator='\n'):
		longestStrings = []
		for i in range(0, self.getNbColumns()):
			header = self.getHeader()[i]
			column = self[header]
			stringColumn = [str(el) for el in column]
			stringColumn.append(header)
			longestStrings.append(max(stringColumn,key=len))
		maxLengths = [len(s) for s in longestStrings]
		zippedLines = [zip(line, maxLengths) for line in [self.getHeader()] + self.getRows()]
		# zippedLines = array of (field1, maxlengthField1),(field2, maxlengthField2),...
		#reduce on a single zippedLine hence works as field1 + necessary tabs + field2 + necessary tabs + ...
		paddedLines = [reduce(lambda x,y: x+padWithTabsToLength(y[0],tabWidth, y[1], extraTabs=1),zippedLine,'') for zippedLine in zippedLines]
		return rowSeparator.join(paddedLines)
	
	#function important to internal workings
	def toString(self, maxlength, showHeader=True):
		if self.length > maxlength:
			return self[0, maxlength/2].text(maxlength, showHeader) + '\n...\n' + self[self.length-maxlength/2,self.length].text(maxlength, False)
		else:
			result = ''
			if showHeader:
				 result = result + '\t'.join(self.header) + '\n'
			result = result + '\n'.join(['\t'.join([str(field) for field in item]) for item in self._items])
			return result
			
	def __str__(self):
		return self.toString(3)
	
	def __unicode__(self):
		return self.__str__()
