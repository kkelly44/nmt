
from Tkinter import Tk, W, E
from ttk import Frame, Button, Label, Style
from ttk import Entry
from tkMessageBox import askyesno, YES


class CorrelateEnergyDialog(Frame):
  
	def __init__(self, parent, *args, **kwargs):
		Frame.__init__(self, parent)   
		self.parent = parent
		self.initUI(*args, **kwargs)


        
	def initUI(self, peakData, callback):

		self.parent.title("Calibrate energy to peaks")

		Style().configure("TButton", padding=(0, 5, 0, 5), 
			font='serif 10')

		self.columnconfigure(0, pad=3)
		self.columnconfigure(1, pad=3)
		self.columnconfigure(2, pad=3)
		self.columnconfigure(3, pad=3)

		rowNb = 0
		count = 0
		self.energyEntries = []
		self.energyErrEntries = []
		self.peakData = peakData
		self.callback = callback
		for rowNb in range(0,len(self.peakData)): #why not just iterate over fitData instead of over a range? Because we want to be sure of the ordering for adding energy levels later
			row = self.peakData[rowNb]

			self.rowconfigure(count, pad=3)
			label = Label(self, text="Peak {}".format(rowNb+1))
			label.grid(row=count, column=0, columnspan=4)
			count = count + 1

			self.rowconfigure(count, pad=3)
			label = Label(self, text='Peak')
			label.grid(row=count, column=0)
			label = Label(self, text=row['Peak'])
			label.grid(row=count, column=1)
			label = Label(self, text='Err')
			label.grid(row=count, column=2)
			label = Label(self, text=row['PeakErr'])
			label.grid(row=count, column=3)
			count = count + 1

			self.rowconfigure(count, pad=3)
			label = Label(self, text='Energy')
			label.grid(row=count, column=0)
			entryEnergy = Entry(self)
			entryEnergy.grid(row=count, column=1)
			label = Label(self, text='Err')
			label.grid(row=count, column=2)
			entryError = Entry(self)
			entryError.grid(row=count, column=3)
			count = count + 1

			self.energyEntries.append(entryEnergy)
			self.energyErrEntries.append(entryError)

		self.parent.bind("<Return>", self.buttonCallback)
		self.parent.bind("<KP_Enter>", self.buttonCallback)
		run = Button(self, text="Process calibration", command=self.buttonCallback)
		run.grid(row=count, column=0)
		count = count + 1
		self.pack()
	def buttonCallback(self,*args): #the *args here is needed because the Button needs a function without an argument and the callback for function takes an event as argument
		try:
			energy = [float(e.get()) for e in self.energyEntries]
			energyErr = [float(e.get()) for e in self.energyErrEntries]
			peakData = self.peakData.withColumn('Energy', energy).withColumn('EnergyErr', energyErr)
			self.callback(peakData)
			self.parent.withdraw()
			self.parent.destroy()
		except Exception as e:
			import traceback
			traceback.print_exc()
			self.parent.destroy()

def doNothing():
	pass


def showCorrelateEnergyDialog(peakData, callback):
	root = Tk()
	try:
		app = CorrelateEnergyDialog(root, peakData, callback)
		root.mainloop()  	
	except Exception as e:
		root.destroy()
		import traceback
		traceback.print_exc()
