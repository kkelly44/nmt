
from Tkinter import Tk, W, E
from ttk import Frame, Button, Label, Style
from ttk import Entry
from tkMessageBox import askyesno, YES


class ChooseParameterDialog(Frame):
  
	def __init__(self, parent, *args, **kwargs):
		Frame.__init__(self, parent)   
		self.parent = parent
		self.initUI(*args, **kwargs)


        
	def initUI(self, parameterDict, callback, validate, undoCallback):

		self.parent.title("Choose parameters for fit")

		Style().configure("TButton", padding=(0, 5, 0, 5), 
			font='serif 10')

		self.columnconfigure(0, pad=3)
		self.columnconfigure(1, pad=3)

		count = 0
		entries = {}
		for key, value in parameterDict.iteritems():
			self.rowconfigure(count, pad=3)
			label = Label(self, text=key)
			label.grid(row=count, column=0)
			entry = Entry(self)
			entry.grid(row=count, column=1)
			entry.insert(0, value)
			entries[key] = entry
			count = count + 1

		def buttonCallback(*args): #the *args here is needed because the Button needs a function without an argument and the callback for function takes an event as argument
			try:
				newParameterDict = {}
				for key, value in entries.iteritems():
					newParameterDict[key] = value.get()
				self.parent.withdraw() #hide window
				feedback = callback(newParameterDict)
				if validate:
					if(askyesno("Validate", feedback,  default=YES)):
						self.parent.destroy() #clean up window
					else:
						undoCallback() #rollback changes done by callback
						self.parent.deiconify() #show the window again
				else:
					self.parent.withdraw()
					self.parent.destroy()
			except Exception as e:
				import traceback
				traceback.print_exc()
				self.parent.destroy()

		self.parent.bind("<Return>", buttonCallback)
		self.parent.bind("<KP_Enter>", buttonCallback)
		run = Button(self, text="Run fit", command=buttonCallback)
		run.grid(row=count, column=0)
		count = count + 1
		self.pack()

def doNothing():
	pass

# This function 
def showStartingValuesDialog(parameterDict, callback, validate=False, undoCallback=doNothing):
	root = Tk()
	try:
		app = ChooseParameterDialog(root, parameterDict, callback, validate, undoCallback)
		root.mainloop()  	
	except Exception as e:
		root.destroy()
		import traceback
		traceback.print_exc()
