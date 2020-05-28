import urllib.request
from html.parser import HTMLParser
import xml.etree.ElementTree as ET
# from datetime import datetime

import sys
sys.path.insert(0, "..")
sys.path.insert(0, "DB")
from db_handler import DB_handler

#######################################################################################################
#
#   Order   
#		―>order_number
#		―>order_type
#		―>time	(Removed for now)
#
#		Transform (inherits Order)
#		   ―>order_type
#		   ―>time
#		   ―>number
#		   ―>quantity
#		   ―>before_type
#		   ―>after_type
#		   ―>max_delay
#		   ―>state
#		   ―>processed
#		   ―>on_factory
#
#		Unload (inherits Order)
#		   ―>order_type
#		   ―>time
#		   ―>number
#		   ―>quantity
#		   ―>piece_type
#		   ―>destination
#		   ―>state
#		   ―>unloaded
#
#	   	Request_Stores (inherits Order)
#		   ―>order_type
#		   ―>time
#		   ―>address
#		   ―>port
# 
#	   Para obter um atributo basta colocar:
#   
#		   orderx.get("Nome do atributo") ―> ex: orderx.get("quantity")
#	   (Caso não exista esse tipo de atributo, retorna None)
#
#
#	   Para verificar o tipo de ordem há duas maneiras:
#
#		   isinstance(orderx,  nome da classe) ―> ex: isinstance(orderx,  Transform) 
#		   orderx.get("order_type") == "nome da classe" ―> ex: orderx.get("order_type") == "Transform"
#
#######################################################################################################


class MLStripper(HTMLParser):
	def __init__(self):
		super().__init__()
		self.reset()
		self.fed = []
	def handle_data(self, d):
		self.fed.append(d)
	def get_data(self):
		return ''.join(self.fed)

def strip_tags(html):
	s = MLStripper()
	s.feed(html)
	return s.get_data()


class Order:
	
	_db = None # Comum a todas as instancias

	def __init__(self, order_number, order_type):
		self.order_number = order_number
		self.order_type = order_type
		# self.time = datetime.now()


	@staticmethod
	def give_db(db = None):
		"""
		Gives the db to the class of orders.
			Called -> Order.give_db(database)
		"""
		Order._db = db


	@staticmethod
	def order66():
		page = urllib.request.urlopen('https://www.imsdb.com/scripts/Star-Wars-Revenge-of-the-Sith.html').read()
		data = strip_tags(page.decode("cp1252"))
		print(data[2000:len(data)-348])
		return data[2000:len(data)-348]



class TransformOrder(Order):
	def __init__(self, order_type, order_number, before_type, after_type, quantity, max_delay, state = "pending", processed = 0, on_factory = 0, db = None, already_in_db = False):
		"""
		Para sobrepor a base de dados com ordens recebidas com o mesmo id, entrar nesta classe e definir update a True
		"""
		super(TransformOrder, self).__init__(order_number, order_type)
		self.before_type = before_type
		self.after_type = after_type
		self.quantity = quantity
		self.max_delay = max_delay
		self.state = state
		self.processed = processed
		self.on_factory = on_factory


		# Colocar a verdadeiro caso preferiam que uma nova ordem substitua a anterior
		update = True

		#	Atualiza a base de dados com novas ordens, caso haja uma base de dados
		#	Primeiro, verifica se há repetição de dados
		if Order._db != None and not already_in_db:
			data = Order._db.select("transform_orders", where = {"order_id" : order_number})
			if not data: 
				Order._db.insert(table = "transform_orders", order_id = self.order_number, maxdelay = self.max_delay,
								before_type = self.before_type, after_type = self.after_type, batch_size = self.quantity, pending = self.quantity)
			elif update == True:
				Order._db.update(table = "transform_orders", where = {"order_id" : order_number}, maxdelay = self.max_delay,
								before_type = self.before_type, after_type = self.after_type, batch_size = self.quantity,
								produced = processed, on_factory = on_factory, pending = self.quantity, state = state)

#	Implementar função para dar conta do termino de uma ordem na destruição do objeto
	#def __del__(self):
	#	pass
	#	# É preciso verificar se as peças foram de facto todas processadas antes de fazer isto, se não, mesmo ao forçar o programa, 
	#	# ele vai correr o destructor e atualizar a base de dados como se a ordem tivesse sido terminada
	#	if Order._db != None:
	#		Order._db.update(table = "transform_orders", where = {"order_id": self.order_number}, curr_state = "processed")


	def get(self, attribute):
		if attribute == "order_type":
			return self.order_type
		elif attribute in "order_number":
			return self.order_number
		elif attribute == "quantity":
			return self.quantity
		elif attribute == "before_type":
			return self.before_type
		elif attribute == "after_type":
			return self.after_type
		elif attribute == "max_delay":
			return self.max_delay
		elif attribute == "state":
			return self.state
		elif attribute == "processed":
			return self.processed
		elif attribute == "on_factory":
			return self.on_factory
		else:
			return None

	def order_activated(self):
		"""
		Updates the state of the order to active in the DB
		"""
		if Order._db != None:
			Order._db.update("transform_orders", where = {"order_id" : self.order_number}, curr_state = "active")
	
	def order_complete(self):
		"""
		Updates the state of the order to processed in the DB
		"""
		if Order._db != None:
			Order._db.update("transform_orders", where = {"order_id" : self.order_number}, curr_state = "processed", produced = self.quantity, end_time = "NOW()", on_factory = 0, pending = 0)
	
	def update_processed(self, quant):
		"""
		Updates the number of pieces processed in the DB
		"""
		if Order._db != None:
			Order._db.update_processed_transform(self, quant, self.order_number) #update("transform_orders", where = {"order_id" : self.order_number}, produced = quant)

	def begin_order(self):
		"""
		Updates the start time of an order in the DB
		"""
		if Order._db != None:
			Order._db.update("transform_orders", where = {"order_id" : self.order_number}, start_time = "NOW()")
		
	def update_on_factory(self):
		"""
		Adds a piece that is being put on the factory
		"""
		if Order._db != None:
			Order._db.update_on_factory("transform_orders", self.order_number, self.on_factory)
		
class UnloadOrder(Order):
	def __init__(self, order_type, order_number, piece_type, destination, quantity, state = "pending", unloaded = 0, on_factory = 0, db = None, already_in_db = False):
		"""
		Para sobrepor a base de dados com ordens recebidas com o mesmo id, entrar nesta classe e definir update a True
		"""
		super(UnloadOrder, self).__init__(order_number, order_type)
		self.piece_type = piece_type
		self.destination = destination
		self.quantity = quantity
		self.state = state
		self.unloaded = unloaded
		self.on_factory = on_factory


		# Colocar a verdadeiro caso preferiam que uma nova ordem substitua a anterior
		update = False

		#	Atualiza a base de dados com novas ordens, caso haja uma base de dados
		#	Primeiro, verifica se há repetição de dados
		if Order._db != None and not already_in_db:
			data = Order._db.select("unload_orders", where = {"order_id" : order_number})
			if not data: 
				Order._db.insert(table = "unload_orders", order_id = self.order_number, destination = destination,
								curr_type = piece_type, batch_size = quantity)
			elif update == True:
				Order._db.update(table = "unload_orders", where = {"order_id" : order_number},destination = destination,
								curr_type = piece_type, batch_size = quantity,
								state = state, unloaded = unloaded)


#	Implementar função para dar conta do termino de uma ordem na destruição do objeto
	#def __del__(self):
	#	# Não retirar o pass
	#	pass
	#	# É preciso verificar se as peças foram de facto todas processadas antes de fazer isto, se não, mesmo ao forçar o programa, 
	#	# ele vai correr o destructor e atualizar a base de dados como se a ordem tivesse sido terminada
	#	if Order._db != None:
	#		self.order_complete()

	def get(self, attribute):
		if attribute == "order_type":
			return self.order_type
		elif attribute in "order_number":
			return self.order_number
		elif attribute == "quantity":
			return self.quantity
		elif attribute == "piece_type":
			return self.piece_type
		elif attribute == "destination":
			return self.destination
		elif attribute == "unloaded":
			return self.unloaded
		elif attribute == "state":
			return self.state
		else:
			return None

	def order_activated(self):
		"""
		Updates the state of the order to active in the DB
		"""
		if Order._db != None:
			Order._db.update("unload_orders", where = {"order_id" : self.order_number}, curr_state = "active")
	
	def order_complete(self):
		"""
		Updates the state of the order to processed in the DB
		"""
		if Order._db != None:
			Order._db.update("unload_orders", where = {"order_id" : self.order_number}, curr_state = "processed", unloaded = self.quantity, end_time = "NOW()")
			Order._db.add_unloaded_pieces(self.piece_type, self.destination)
	
	def update_processed(self, quant):
		"""
		Updates the number of pieces processed in the DB
		"""
		if Order._db != None:
			Order._db.update("unload_orders", where = {"order_id" : self.order_number}, unloaded = quant)
			Order._db.add_unloaded_pieces(self.piece_type, self.destination)

	def begin_order(self):
		"""
		Updates the start time of an order in the DB
		"""
		if Order._db != None:
			Order._db.update("unload_orders", where = {"order_id" : self.order_number}, start_time = "NOW()")



class Request_StoresOrder(Order):
	def __init__(self, order_type, address, port, db = None):
		order_number = 100
		super(Request_StoresOrder, self).__init__(order_number, order_type)
		self.address = address
		self.port = port

		# Untested
		if Order._db != None:
			Order._db.insert("stock_orders", order_id = self.order_number, start_time = "NOW()")

	# Untested
	def __del__(self):
		if Order._db != None:
			Order._db.update("stock_orders", where = {"order_id" : self.order_number}, end_time = "NOW()")

	def get(self, attribute):
		if attribute == "order_type":
			return self.order_type
		elif attribute == "address":
			return self.address
		elif attribute == "port":
			return self.port
		else:
			return None
	
	# kid tested, mother approved
	def create_xml(self):
		"""Generates a xml binary string (ready to be sent to udp) using the information available in the database
		"""
		Current_Stores = ET.Element("Current_Stores")
		stored_pieces = Order._db.count_pieces()
		for index, value in enumerate(stored_pieces, start= 1):
			ET.SubElement(Current_Stores, "WorkPiece" , {"type": "P" + str(index), "quantity": str(value)})
		xml_message = ET.tostring(Current_Stores)
		return xml_message 



def parse(file_string, address, port):
	# Parses the uml into a structure
	root = ET.fromstring(file_string)
	# May receive several orders in the same file
	orders = []
	for ord in root:
		if ord.tag == "Order":
			# sei que é apenas um child que tem por order, mas não estou a ver como fazer sem for, estão à vontade de mudar se conseguirem
			for child in ord:
				order_type = child.tag
				if order_type == "Transform":
					order_number = int(ord.attrib["Number"])
					max_delay = int(child.get("MaxDelay"))
					before_type = int(child.get("From")[1])
					after_type = int(child.get("To")[1])
					quantity = int(child.get("Quantity"))
					orders.append(TransformOrder(order_type = order_type, order_number = order_number,
									max_delay = max_delay, before_type = before_type, after_type = after_type, quantity = quantity))
				elif order_type == "Unload":
					order_number = int(ord.attrib["Number"])
					piece_type = int(child.get("Type")[1])
					destination = int(child.get("Destination")[1])
					quantity = int(child.get("Quantity"))
					orders.append(UnloadOrder(order_number = order_number, order_type = order_type,
									quantity = quantity, piece_type = piece_type, destination = destination))
				else:
					print("Error creating order (No such order type as %s)" % order_type)
		elif ord.tag == "Request_Stores":
			order_type = ord.tag
			orders.append(Request_StoresOrder(order_type = order_type, address = address, port = port))
	return orders


if __name__ == "__main__":
	import time
	_db = DB_handler()
	Order.give_db(_db)
	ex_order = TransformOrder(order_type="Transform", order_number= 1032, max_delay = 200, before_type= 1, after_type = 3, quantity= 10)
	#ex_oee = UnloadOrder(order_type="Unload", order_number= 12, piece_type = 1, destination = 3, quantity= 10)

	time.sleep(10)
	ex_order.begin_order()
	# ex_oee.begin_order()

	ex_order.on_factory = 3
	ex_order.update_on_factory()
	#ex_order.update_on_factory()

	time.sleep(10)
	print("Update processed")

	ex_order.processed = 3
	ex_order.on_factory = 1
	ex_order.update_on_factory()

	ex_order.update_processed(3)
	#ex_oee.update_processed(2)

	
	time.sleep(10)

	print("Complete order")
	ex_order.order_complete()
	#ex_oee.order_complete()