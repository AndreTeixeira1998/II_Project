from tkinter import *
from tkinter import ttk
from threading import Thread
import time

from stat_manager import *

columns_orders = ["Id", "Type", "State", "Produced", "In production", "Pending", "Reception time", "Beggining", "End", "Slack"]
columns_machines = ["Type/Cell", "Total time", "P1", "P2", "P3", "P4", "P5", "P6", "P7", "P8", "P9", "Total"]
columns_unload = ["Unload Zone", "P1", "P2", "P3", "P4", "P5", "P6", "P7", "P8", "P9"]


# https://pythonhosted.org/tkintertable/tkintertable.Tables.TableCanvas-class.html

#from pandastable import Table
#import pandas as pd
#class GUI:
#	def __init__(self, db = None, dimensions = "1000x900"):
#
#		self.stat_man = StatMan(columns_orders, columns_machines, columns_unload, db)		# To fetch the statistics from the database
#		
#		# Only initializes the window
#		self.window = Tk()
#
#		self.window.title("Factory Statistics")
#		self.window.geometry(dimensions)
#
#		self.tab_control = ttk.Notebook(self.window)
#
#		tab_orders = ttk.Frame(self.tab_control) 		## Frame inside a Tab; We will display the DataFrame here
#		tab_machines = ttk.Frame(self.tab_control) 		## Frame inside a Tab; We will display the DataFrame here
#		tab_unload = ttk.Frame(self.tab_control)		## Frame inside a Tab; We will display the DataFrame here
#
#		self.tab_control.add(tab_orders, text='Orders')
#		self.tab_control.add(tab_machines, text='Machines')
#		self.tab_control.add(tab_unload, text='Unloaded Pieces')
#
#		self.lbl_orders = Label(tab_orders, text= 'label1')
#		self.lbl_orders.grid(column=0, row=0)
#
#		self.lbl_machines = Label(tab_machines, text= 'label2')
#		self.lbl_machines.grid(column=0, row=0)
#
#		self.lbl_unload = Label(tab_unload, text= 'label3')
#		self.lbl_unload.grid(column=0, row=0)
#
#		self.tab_control.pack(expand=1, fill='both')
#
#		self.tabs = [tab_orders , tab_machines, tab_unload]
#
#		self._glob_flag = False
#
#	def open_GUI(self):
#		"""
#		Opens the GUI. The GUI class must have a data base attributed, otherwise it won't work
#		"""
#		self._glob_flag = True
#		self.pts = []
#		threads = []
#		thread_names = ["tab_orders", "tab_machines", "tab_unload"]
#		
#		
#		#	Prepares the Orders tab
#		self.pts.append(Table(self.tabs[0]))											## Populate list of Tables
#		self.pts[-1].show()																## Tell TKINter to show the table
#		threads.append(Thread(target=self.statistics_orders, args=(self.pts[-1],))) 	## Build Thread that generates random data in the Table
#		threads[-1].name = thread_names[0]												# Just to rename the thread
#
#		#	Prepares the Machines tab
#		self.pts.append(Table(self.tabs[1]))											## Populate list of Tables
#		self.pts[-1].show()																## Tell TKINter to show the table
#		threads.append(Thread(target=self.statistics_machines, args=(self.pts[-1],))) 	## Build Thread that generates random data in the Table
#		threads[-1].name = thread_names[1]												# Just to rename the thread
#
#		#	Prepares the Unload tab
#		self.pts.append(Table(self.tabs[2]))											## Populate list of Tables
#		self.pts[-1].show()																## Tell TKINter to show the table
#		threads.append(Thread(target=self.statistics_unload, args=(self.pts[-1],))) 	## Build Thread that generates random data in the Table
#		threads[-1].name = thread_names[2]												# Just to rename the thread
#
#		## start the Threads
#		for t in threads:
#			t.start() 					
#
#		# Opens the window
#		self.window.mainloop()
#		# If the user closes the window, the program perform the next instructions
#		
#		self._glob_flag=False
#
#		## Joints all the threads
#		map(lambda x:x.join(),threads)
#
#
#	def statistics_orders(self, table_obj):
#		"""
#		Creates the content to display in the orders tab
#		"""
#		while self._glob_flag:
#			df = pd.DataFrame(columns = columns_orders)
#			# Constantly asks the database for new info
#			data = self.stat_man.stat_orders()
#			df_to_append = pd.DataFrame(data, columns = columns_orders)
#			df = df.append(df_to_append, ignore_index = True)
#
#			# Updates the content of the table every 2 seconds
#			table_obj.model.df = df
#			table_obj.redraw()
#			time.sleep(5)
#
#	def statistics_machines(self, table_obj):
#		"""
#		Creates the content to display in the machines tab
#		"""
#		df = pd.DataFrame(columns = columns_machines)
#		# Constantly asks the database for new info
#		ex_A = [["A1", 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],["A2", 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],["A3", 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]
#		ex_B = [["B1", 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],["B2", 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],["B3", 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]
#		ex_C = [["C1", 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],["C2", 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],["C3", 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]
#		df_to_append = pd.DataFrame(ex_A + ex_B + ex_C, columns = columns_machines)
#		df = df.append(df_to_append, ignore_index = True)
#
#		# Updates the content of the table every 5 seconds
#		table_obj.model.df = df
#		while self._glob_flag:
#			table_obj.redraw()
#			time.sleep(5)
#
#	def statistics_unload(self, table_obj):
#		"""
#		Creates the content to display in the unload tab
#		"""
#		while self._glob_flag:
#			df = pd.DataFrame(columns = columns_unload)
#			# Constantly asks the database for new info
#
#
#			# Updates the content of the table every 2 seconds
#			table_obj.model.df = df
#			table_obj.redraw()
#			time.sleep(5)
#
#
#	def stats(self, table_obj_orders, table_obj_machines, table_obj_unload):
#		while self._glob_flag:
#			df_orders = pd.DataFrame(columns = columns_orders)
#			# Ask database for information on orders
#			data = self.stat_man.stat_orders()
#			df_to_append = pd.DataFrame(data, columns = columns_orders)
#			df_orders = df_orders.append(df_to_append, ignore_index = True)
#
#			table_obj_orders.model.df = df_orders
#
#			df_machines = pd.DataFrame(columns = columns_machines)
#			# Ask database for information on machines
#			ex_A = [["A1", 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],["A2", 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],["A3", 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]
#			ex_B = [["B1", 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],["B2", 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],["B3", 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]
#			ex_C = [["C1", 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],["C2", 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],["C3", 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]
#			df_to_append = pd.DataFrame(ex_A + ex_B + ex_C, columns = columns_machines)
#			df_machines = df_machines.append(df_to_append, ignore_index = True)
#
#			
#			table_obj_machines.model.df = df_machines
#
#
#			df_unload = pd.DataFrame(columns = columns_unload)
#			# Ask database for information on unload
#			
#
#
#			table_obj_unload.model.df = df_unload
#
#
#			# Redraw the content for all the tables (Can't find anything to update single cell. This way is far less efficient)
#			table_obj_orders.redraw()
#			table_obj_machines.redraw()
#			table_obj_unload.redraw()
#			time.sleep(5)
			

class GUI_V2:
	def __init__(self, db = None, dimensions = "1000x900"):

		self.stat_man = StatMan(columns_orders, columns_machines, columns_unload, db)		# To fetch the statistics from the database
		
		# Only initializes the window
		self.window = Tk()

		self.window.title("Factory Statistics")
		self.window.geometry(dimensions)

		frame = Frame(self.window)
		frame.pack(fill="both")

		self.tab_control = ttk.Notebook(frame)

		tab_orders = ttk.Frame(self.tab_control) 		## Frame inside a Tab; We will display the DataFrame here
		tab_machines = ttk.Frame(self.tab_control) 		## Frame inside a Tab; We will display the DataFrame here
		tab_unload = ttk.Frame(self.tab_control)		## Frame inside a Tab; We will display the DataFrame here

		self.tab_control.add(tab_orders, text='Orders')
		self.tab_control.add(tab_machines, text='Machines')
		self.tab_control.add(tab_unload, text='Unloaded Pieces')

		self.tab_control.pack(expand=1, fill='both')

		self.tabs = [tab_orders , tab_machines, tab_unload]
		# self.tabs = {lbl_orders : tab_orders, lbl_machines : tab_machines, lbl_unload : tab_unload}

		self._glob_flag = False


	def open_GUI(self):
		"""
		Opens the GUI. The GUI class must have a data base attributed, otherwise it won't work
		"""
		self._glob_flag = True
		
		thread = Thread(target=self._draw_statistics, args=())
		
		thread.start()
		# Opens the window
		self.window.mainloop()
		# If the user closes the window, the program perform the next instructions
		
		self._glob_flag=False

		thread.join()
	
	def _refresh_tab(self, tab, data):
		for row_index,row in enumerate(data):
			for column_index,column in enumerate(row):
				label = Label(self.tabs[tab], text = str(column), bg="white",fg="black",padx=3,pady=3)
				label.grid(row=row_index + 1,column=column_index,sticky="nsew",padx=1,pady=1)
				self.tabs[tab].grid_columnconfigure(column_index, weight=1)

	def _draw_statistics(self):
		for index,col in enumerate(columns_orders):
			label = Label(self.tabs[0], text = col, bg="white", fg="black", padx=3, pady=3)
			label.config(font=('Arial', 12))
			label.grid(row=0, column=index, sticky="nsew", padx=1, pady=1)
			self.tabs[0].grid_columnconfigure(index, weight=1)
		
		for index,col in enumerate(columns_machines):
			label = Label(self.tabs[1], text = col, bg="white", fg="black", padx=3, pady=3)
			label.config(font=('Arial', 12))
			label.grid(row=0, column=index, sticky="nsew", padx=1, pady=1)
			self.tabs[1].grid_columnconfigure(index, weight=1)

		for index,col in enumerate(columns_unload):
			label = Label(self.tabs[2], text = col, bg="white", fg="black", padx=3, pady=3)
			label.config(font=('Arial', 12))
			label.grid(row=0, column=index, sticky="nsew", padx=1, pady=1)
			self.tabs[2].grid_columnconfigure(index, weight=1)

		while self._glob_flag:
			data = self.stat_man.stat_orders()
			self._refresh_tab(0, data)

			data = self.stat_man.stat_machines()	
			self._refresh_tab(1, data)

			data = self.stat_man.stat_unload()
			self._refresh_tab(2, data)

			time.sleep(5)


if __name__ == "__main__":
	db = DB_handler()
	win = GUI_V2(db)

	db.insert("transform_orders", order_id = 500, maxdelay=500, start_time = "NOW()",before_type = 1, after_type = 3)

	win.open_GUI()