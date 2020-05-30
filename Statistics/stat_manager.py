import sys
from datetime import datetime

sys.path.insert(0, "..")
sys.path.insert(0, "DB")	# Juro só assim é que me começou a funcionar
from db_handler import *




class StatMan:
	def __init__(self, columns_orders, columns_machines, columns_unload, db : DB_handler = None, optimizer = None):
		self._db = db
		self._optimizer = optimizer
		self._columns_orders = columns_orders
		self._columns_machines = columns_machines
		self._columns_unload = columns_unload

		self.tempo_as_GVL = False
		if self.tempo_as_GVL:
			self._node_id = "|var|CODESYS Control Win V3 x64.Application."
		else:	
			self._node_id = "|var|CODESYS Control Win V3 x64.Application.tapetes."

		self._machine_node = {"A1" : "c1t3", "A2" : "c3t3", "A3" : "c5t3", "B1" : "c1t4", "B2" : "c3t4", "B3" : "c5t4", "C1" : "c1t5", "C2" : "c3t5", "C3" : "c5t5"}
		self._machine_vars = {"A" : ["tempo", "p1", "p2", "p6" , "p8", "ptotal"], "B" : ["tempo", "p1", "p3", "p7", "ptotal"], "C" : ["tempo", "p1", "p2", "p4", "p8", "ptotal"]}

		self._translator = {"Total time" : "tempo", "P1" : "p1", "P2": "p2", "P3": "p3", "P4" : "p4", "P5" : "p5", "P6" : "p6", "P7" : "p7", "P8" : "p8", "P9" : "p9", "Total" : "ptotal"}

	def stat_orders(self, print_table = False):
		filtered_data = []
		# columns_orders = ["Id", "Type", "State", "Produced", "In production", "Pending", "Reception time", "Beggining", "End", "Slack"]

		# https://stackoverflow.com/questions/5259882/subtract-two-times-in-python

		#	Informação para as transformation orders
		data = self._db.select("transform_orders", print_table = print_table, order_by = "order_id")
		for item in data:
			time_rec = item[1].time().strftime("%H:%M:%S")
			if item[2] != None: time_beg = item[2].time().strftime("%H:%M:%S")
			else: time_beg = None
			if item[3] == None: 
				slack =  datetime.now() - item[1].replace(tzinfo = None) ##### Por algum motivo, a base de dados dá uma hora a menos, é preciso compensar
				slack = item[4] - int(slack.total_seconds()) + 1*60*60
				time_end = None
			else:
				slack = item[3].replace(tzinfo = None) - item[1].replace(tzinfo = None)
				time_end = item[3].time().strftime("%H:%M:%S")
				slack = item[4] - int(slack.total_seconds())

			filtered_data.append([item[0], "Transform", item[5], item[9], item[10], item[11], time_rec, time_beg, time_end, slack])

		#	Informação para as unload orders
		data = self._db.select("unload_orders", print_table = print_table, order_by = "order_id")
		for item in data:
			time_rec = item[1].time().strftime("%H:%M:%S")
			if item[2] != None: time_beg = item[2].time().strftime("%H:%M:%S")
			else: time_beg = None
			if item[3] == None: 
				slack =  datetime.now() - item[1].replace(tzinfo = None)
				slack = item[4] - int(slack.total_seconds()) + 1*60*60
				time_end = None
			else:
				slack = item[3].replace(tzinfo = None) - item[1].replace(tzinfo = None)
				slack = item[4] - int(slack.total_seconds())
				time_end = item[3].time().strftime("%H:%M:%S")

			filtered_data.append([item[0], "Unload", item[5], item[9], "-", item[8]-item[9], time_rec, time_beg, time_end, slack])

		#	Informação para as Request Stores
		data = self._db.select("stock_orders", print_table = print_table, order_by = "order_id")
		for item in data:
			time_rec = item[1].time().strftime("%H:%M:%S")
			if item[2] != None: time_beg = item[2].time().strftime("%H:%M:%S")
			else: time_beg = None
			if item[3] == None: 
				slack =  datetime.now() - item[1].replace(tzinfo = None)
				slack = item[4] - int(slack.total_seconds()) + 1*60*60
				time_end = None
			else:
				slack = item[3].replace(tzinfo = None) - item[1].replace(tzinfo = None)
				slack = item[4] - int(slack.total_seconds())
				time_end = item[3].time().strftime("%H:%M:%S")
			
			filtered_data.append([item[0], "Request", item[5], "-", "-", "-", time_rec, time_beg, time_end, slack])

		return filtered_data
	
	def stat_machines(self, print_table = False, from_db = False):
		if not from_db:
			filtered_data = []
			to_database = []
			for id in self._machine_node.keys():
				v = [id]
				vars = self._machine_vars[id[0]]
				for columns in self._translator.keys():
					if self._translator[columns] in vars:
						#print(self._node_id + self._machine_node[id] + "." + self._translator[columns])
						#print(self._optimizer.factory_state.keys())
						try:
							if self.tempo_as_GVL:
								if self._translator[columns] == "tempo":
									v.append(self._optimizer.factory_state[self._node_id + "GVL.tempo_" + id])
									v[-1] = int(v[-1]/1000)
								else:	
									v.append(self._optimizer.factory_state[self._node_id + "tapetes." + self._machine_node[id] + "." + self._translator[columns]])
							else:
								v.append(self._optimizer.factory_state[self._node_id + self._machine_node[id] + "." + self._translator[columns]])
								if self._translator[columns] == "tempo":
									v[-1] = int(v[-1]/1000)
						except Exception as error:
							# print("OPC UA ainda a ler a subscrever(", error, ")")
							v.append(0)
					else:
						v.append(0)
				filtered_data.append(v)

				# to_database.append(dict(zip( list(self._translator.keys()) , v)))
				# print(to_database)
				# self._db.insert_machine_stats(to_database)

		else:
			data = self._db.select("machines", order_by = "machine_id", print_table = print_table)
			filtered_data = []
			for item in data:
				f = [item[1] + str(item[2])]
				[f.append(x) for x in item[3:]]
				filtered_data.append(f)
		
		return filtered_data
	
	def stat_unload(self, print_table = False):
		data = self._db.select("unloading_zones", order_by = "area_id", print_table = print_table)
		filtered_data = data
		return filtered_data

	def update_warehouse(self):
		for i in range(1,10):
			amount = self._optimizer.factory_state["|var|CODESYS Control Win V3 x64.Application.GVL.p" + str(i)]
			self._db.update_stored_pieces(i, amount)

if __name__ == "__main__":
	columns_orders = ["Id", "Type", "State", "Produced", "In production", "Pending", "Reception time", "Beggining", "End", "Slack"]
	columns_machines = ["Machine Id", "Total time", "P1", "P2", "P3", "P4", "P5", "P6", "P7", "P8", "P9", "Total"]
	columns_unload = ["Unload Zone", "P1", "P2", "P3", "P4", "P5", "P6", "P7", "P8", "P9"]

	db = DB_handler()

	# db.update(table = "transform_orders", where = {"order_id": 1} , end_time = "NOW()")
	# db.insert("unload_orders", order_id = 12, curr_type = 2, destination = 1, batch_size = 5)
	st = StatMan(columns_orders, columns_machines, columns_unload, db)

	data = st.stat_machines()
	print(data)