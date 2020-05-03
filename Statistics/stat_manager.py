import sys

sys.path.insert(0, "..")
# from OPC_UA.opc_client import *
from DB.db_handler import *




class StatMan:
	def __init__(self, columns_orders, columns_machines, columns_unload, db : DB_handler = None):
		self._db = db
		self._columns_orders = columns_orders
		self._columns_machines = columns_machines
		self._columns_unload = columns_unload

	def stat_orders(self, print_table = False):
		filtered_data = []
		# columns_orders = ["Id", "Type", "State", "Produced", "In production", "Pending", "Reception time", "Beggining", "End", "Slack"]

		# https://stackoverflow.com/questions/5259882/subtract-two-times-in-python

		#	Informação para as transformation orders
		data = self._db.select("transform_orders", print_table = print_table)
		for item in data:
			time_rec = item[1].time().strftime("%H:%M:%S")
			if item[2] != None: time_beg = item[2].time().strftime("%H:%M:%S")
			else: time_beg = None
			if item[3] != None: time_end = item[3].time().strftime("%H:%M:%S")
			else: time_end = None
			filtered_data.append([item[0], "Transform", item[5], item[9], "*in prod*", "*pend*", time_rec, time_beg, time_end, "*slack*"])

		#	Informação para as unload orders
		data = self._db.select("unload_orders", print_table = print_table)
		for item in data:
			time_rec = item[1].time().strftime("%H:%M:%S")
			if item[2] != None: time_beg = item[2].time().strftime("%H:%M:%S")
			else: time_beg = None
			if item[3] != None: time_end = item[3].time().strftime("%H:%M:%S")
			else: time_end = None
			filtered_data.append([item[0], "Unload", item[5], item[9], "*in prod*", "*pend*", time_rec, time_beg, time_end, "*slack*"])

		#	Informação para as Request Stores
		data = self._db.select("stock_orders", print_table = print_table)
		for item in data:
			time_rec = item[1].time().strftime("%H:%M:%S")
			if item[2] != None: time_beg = item[2].time().strftime("%H:%M:%S")
			else: time_beg = None
			if item[3] != None: time_end = item[3].time().strftime("%H:%M:%S")
			else: time_end = None
			filtered_data.append([item[0], "Unload", item[5], "-", "-", "-", time_rec, time_beg, time_end, "*slack*"])

		return filtered_data
	
	def stat_machines(self, print_table = False):
		data = self._db.select("machines", print_table = print_table)
		filtered_data = data
		return filtered_data
	
	def stat_unload(self, print_table = False):
		data = self._db.select("", print_table = print_table)
		filtered_data = data
		return filtered_data

if __name__ == "__main__":
	columns_orders = ["Id", "Type", "State", "Produced", "In production", "Pending", "Reception time", "Beggining", "End", "Slack"]
	columns_machines = ["Machine Id", "Total time", "P1", "P2", "P3", "P4", "P5", "P6", "P7", "P8", "P9"]
	columns_unload = ["Unload Zone", "P1", "P2", "P3", "P4", "P5", "P6", "P7", "P8", "P9"]

	db = DB_handler()

	# db.insert("unload_orders", order_id = 12, curr_type = 2, destination = 1, batch_size = 5)
	st = StatMan(columns_orders, columns_machines, columns_unload, db)

	data = st.stat_orders(print_table = True)
	print(data)