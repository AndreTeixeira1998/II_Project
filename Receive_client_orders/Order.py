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
#
#		Unload (inherits Order)
#		   ―>order_type
#		   ―>time
#		   ―>number
#		   ―>quantity
#		   ―>piece_type
#		   ―>destination
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
	def __init__(self, order_type, db: DB_handler = None):
		self._db = db
		self.order_type = order_type
		# self.time = datetime.now()


	@staticmethod
	def order66():
		page = urllib.request.urlopen('https://www.imsdb.com/scripts/Star-Wars-Revenge-of-the-Sith.html').read()
		data = strip_tags(page.decode("cp1252"))
		print(data[2000:len(data)-348])
		return data[2000:len(data)-348]

class TransformOrder(Order):
	def __init__(self, order_type, order_number, before_type, after_type, quantity, max_delay, state = "pending", processed = 0, on_factory = 0, db : DB_handler= None, already_in_db = False):
		super(TransformOrder, self).__init__(order_type, db)
		self.order_number = order_number
		self.before_type = before_type
		self.after_type = after_type
		self.quantity = quantity
		self.max_delay = max_delay
		self.state = state
		self.processed = processed
		self.on_factory = on_factory


		#	Atualiza a base de dados com novas ordens, caso haja uma base de dados
		if self._db != None and not already_in_db:
			self._db.insert(table = "transform_orders", order_id = self.order_number, maxdelay = self.max_delay,
												   before_type = self.before_type, after_type = self.after_type, batch_size = self.quantity)

#	Implementar função para dar conta do termino de uma ordem na destruição do objeto
	def __del__(self):
		pass
		# É preciso verificar se as peças foram de facto todas processadas antes de fazer isto, se não, mesmo ao forçar o programa, 
		# ele vai correr o destructor e atualizar a base de dados como se a ordem tivesse sido terminada
		if self._db != None:
			self._db.update(table = "transform_orders", where = "order_id", condition = self.order_number, curr_state = "processed")


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
		else:
			return None

	def order_activated(self):
		"""
		Updates the state of the order to active in the DB
		"""
		if self._db != None:
			self._db.update("transform_orders", where = {"order_id" : self.order_number}, curr_state = "active")
	
	def order_complete(self):
		"""
		Updates the state of the order to processed in the DB
		"""
		if self._db != None:
			self._db.update("transform_orders", where = {"order_id" : self.order_number}, curr_state = "processed", produced = self.quantity)
	
	def update_processed(self, quant):
		"""
		Updates the number of pieces processed in the DB
		"""
		if self._db != None:
			self._db.update("transform_orders", where = {"order_id" : self.order_number}, produced = quant)


		
class UnloadOrder(Order):
	def __init__(self, order_type, order_number, piece_type, destination, quantity, state = "pending", unloaded = 0, on_factory = 0,db : DB_handler = None, already_in_db = False):
		super(UnloadOrder, self).__init__(order_type, db)
		self.order_number = order_number
		self.piece_type = piece_type
		self.destination = destination
		self.quantity = quantity
		self.state = state
		self.unloaded = unloaded

		#Atualiza a base de dados com novas ordens, caso haja uma base de dados
		if self._db != None and not already_in_db:
			self._db.insert(table = "unload_orders", order_id = self.order_number,
												   destination = self.destination, curr_type = self.piece_type, batch_size = self.quantity)

#	Implementar função para dar conta do termino de uma ordem na destruição do objeto
	def __del__(self):
		pass
		# É preciso verificar se as peças foram de facto todas processadas antes de fazer isto, se não, mesmo ao forçar o programa, 
		# ele vai correr o destructor e atualizar a base de dados como se a ordem tivesse sido terminada
		if self._db != None:
			self._db.update(table = "unload_orders", where = "order_id", condition = self.order_number, curr_state = "processed")

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
		else:
			return None

	def order_activated(self):
		"""
		Updates the state of the order to active in the DB
		"""
		if self._db != None:
			self._db.update("unload_orders", where = {"order_id" : self.order_number}, curr_state = "active")
	
	def order_complete(self):
		"""
		Updates the state of the order to processed in the DB
		"""
		if self._db != None:
			self._db.update("unload_orders", where = {"order_id" : self.order_number}, curr_state = "processed", processed = self.quantity)
	
	def update_processed(self, quant):
		"""
		Updates the number of pieces processed in the DB
		"""
		if self._db != None:
			self._db.update("unload_orders", where = {"order_id" : self.order_number}, processed = quant)


class Request_StoresOrder(Order):
	def __init__(self, order_type, address, port, db : DB_handler = None):
		super(Request_StoresOrder, self).__init__(order_type, db)
		self.address = address
		self.port = port

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
		stored_pieces = self._db.count_pieces()
		for index, value in enumerate(stored_pieces, start= 1):
			ET.SubElement(Current_Stores, "WorkPiece" , {"type": "P" + str(index), "quantity": str(value)})
		xml_message = ET.tostring(Current_Stores)
		return xml_message 


def parse(file_string, address, port, db : DB_handler = None):
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
					orders.append(TransformOrder(order_type = order_type, order_number = order_number, db = db,
									max_delay = max_delay, before_type = before_type, after_type = after_type, quantity = quantity))
				elif order_type == "Unload":
					order_number = int(ord.attrib["Number"])
					piece_type = int(child.get("Type")[1])
					destination = int(child.get("Destination")[1])
					quantity = int(child.get("Quantity"))
					orders.append(UnloadOrder(order_number = order_number, order_type = order_type, db = db,
									quantity = quantity, piece_type = piece_type, destination = destination))
				else:
					print("Error creating order (No such order type as %s)" % order_type)
		elif ord.tag == "Request_Stores":
			order_type = ord.tag
			orders.append(Request_StoresOrder(order_type = order_type, db = db, address = address, port = port))
	return orders
