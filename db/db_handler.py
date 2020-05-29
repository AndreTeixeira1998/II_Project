import psycopg2
import threading

class DB_handler:
	def __init__(self, host = "127.0.0.1", port = "5432"):
		try:
			self._connection = psycopg2.connect(user = "ii",
									password = "iisuckz",
									host = host,
									port = port) #https://stackoverflow.com/questions/32812463/setting-schema-for-all-queries-of-a-connection-in-psycopg2-getting-race-conditi


			self._cursor = self._connection.cursor()

			# Print PostgreSQL Connection properties
			print(self._connection.get_dsn_parameters())

			#   Print PostgreSQL version
			self._cursor.execute("SELECT version();")
			record = self._cursor.fetchone()
			print("You are connected to - ", record,"\n")
			pgsql = """ 
			+------------------------+
			|   ____  ______  ___    |
			|  /    )/      \\/   \\   |
			| (     / __    _\\    )  |
			|  \\    (/ o)  ( o)   )  |
			|   \\_  (_  )   \\ )  /   |
			|     \\  /\\_/    \\)_/    |
			|      \\/  //|  |\\\\      |
			|          v |  | v      |
			|            \\__/        |
			|                        |
			+------------------------+
			"""
			print(pgsql)
			self.tables = ("pieces", "transform_orders", "unload_orders", "stock_orders", "orders", "operations","machines", "transformations", "transform_operations", "unloading_zones", "unload_operations")
			
			self._column_dict = {}
			for table in self.tables:
				Query = "SELECT * FROM factory." + table + " LIMIT 0"
				self._cursor.execute(Query)
				colnames = [names[0] for names in self._cursor.description]
				self._column_dict[table] = colnames
			
			check_unloadig_zones = self.select("unloading_zones")
			if not check_unloadig_zones:
				for i in range(1 ,4):
					Query = "INSERT INTO factory.unloading_zones (area_id) VALUES (%s)"
					self._cursor.execute(Query,tuple(str(i)))
					self._connection.commit()
		
			self.mutex = threading.Lock()

		except(Exception, psycopg2.Error) as error:
			print("Error while connecting to PostgreSQL", error) 

	def __del__(self):
		self.close()

	def _get_columns(self, table):
		if table in self._column_dict:
			colnames = self._column_dict[table]
		else:
			Query = "SELECT * FROM factory." + table + " LIMIT 0"
			############################# Abre mutex
			with self.mutex:
				self._cursor.execute(Query)
				colnames = [names[0] for names in self._cursor.description]
			############################# Fecha mutex
			self._column_dict[table] = colnames
		return colnames

	def close(self):
		"""Termina a conecção"""
		if (self._connection):
			self._cursor.close()
			self._connection.close()
			print("Database connection closed")
	
	def select_query(self, query, tup = None):
		############################# Abre mutex
		with self.mutex: 
			try:
				if tup == None:
					self._cursor.execute(query)
					data = self._cursor.fetchall()
				else:
					self._cursor.execute(query, tuple(tup))
					data = self._cursor.fetchall()
			except(Exception, psycopg2.Error) as error:
					print("Error while connecting to PostgreSQL", error)

		############################# Fecha mutex
		return data

	def insert_update_query(self, query, tup = None):
		############################# Abre mutex
		with self.mutex:
			try:
				if tup == None:
					self._cursor.execute(query)
					self._connection.commit()
				else:
					self._cursor.execute(query, tuple(tup))
					self._connection.commit()
			except(Exception, psycopg2.Error) as error:
					print("Error while connecting to PostgreSQL", error)
		############################# Fecha mutex



	def delete_all_content(self, tables_to_delete = None):
		"""Apaga o conteudo das tabelas indicadas, se vazio, apaga todas
		################# Há problemas com as dependências, é preciso ser revisto ##################"""
		if tables_to_delete == None:
			for table in self.tables:
				self._cursor.execute("DELETE FROM factory." + table)
				self._connection.commit()
		for table in self.tables:
			if table in tables_to_delete:
				self._cursor.execute("DELETE FROM factory." + table)
				self._connection.commit()

	def insert(self, table, **kwargs):
		"""Insere na tabela os valores dados. 
		Atenção, se a Primary key não for serial é preciso fornecê-la.\n
		Nos kwards é preciso fornecer o nome especifico da coluna da tabela.\n
		Exemplo de uso:
			db.insert(table = "machines", machine_type = "D", transformation_cell = 1)"""
		Query = "INSERT INTO factory." + table + "("
		colnames = self._get_columns(table)
		count_args = 0
		values = []
		for key, vals in kwargs.items():
			if key in colnames:
				count_args = count_args + 1
				Query = Query + key + ","
				values.append(vals)
		Query = Query[:-1] + ") VALUES ("

		for _ in range(count_args):
		   Query = Query + "%s,"
		Query = Query[:-1] + ")"

		self.insert_update_query(Query, values)
		
	def update(self, table, where, **kwargs):
		"""Faz update de valores num determinado lugar.
		De preferência, fornecer a primary key no where, visto o contexto do trabalho.\n 
		Nos kwargs é preciso fornecer o nome especifico da coluna da tabela.\n
		Exemplos de usos:
			db.update(table = "machines", where = {"machine_id": 1} , machine_type = "D", transformation_cell = 2)
		Para várias condições:
			db.update("transform_orders", where = {"maxdelay" : 300, "before_type" : 1}, before_type = 2)
		"""
		Query = "UPDATE factory." + table + " SET "
		colnames = self._get_columns(table)
		values = []
		debug = None
		for key, vals in kwargs.items():
			if key in colnames:
				Query += key + " = %s,"
				values.append(str(vals))
				debug = 1
		Query = Query[:-1]

		if debug == None:
			print("Colunas não iseridas ou não existentes")
			print("Tabela : ", table)
			print("Onde : ", where)
			print("Conteudo : ")
			for k in kwargs.keys():
				print("\t", k, " = ", kwargs[k])

			return

		condition = []
		Query += " WHERE "
		for key,value in where.items():
			Query += key + "=%s AND "
			condition.append(str(value))
		Query = Query[:-5]

		values_condition = values + condition

		self.insert_update_query(Query, values_condition)

	def select(self, table, content = "*", where = None,  order_by = "", operand = "AND", print_table = False):
		"""Retorna dados da tabela. Está como default retirar todas as colunas. É possível selecionar vários dados especificos com o where.\n
		O print_table permite imprimir a tabela no terminal (mais para efeitos de debugging ou demonstrativos)\n
		Exemplo de uso:
			data = db.select(table= "machines", content = ["machine_type", "transformation_cell"], order_by= "machine_id", print_table = True)\n
		Para várias condições:
			data = db.select("transform_orders", where = {"maxdelay" : 300, "batch_size" : 10})
		Para várias condições na mesma coluna, é preciso colocar a condição com um numero à frente da coluna
		(O digito tem que ser diferentes se forem mais que 2 repetições):
			where = {"curr_state" : "pending", "curr_state1" : "active"} e usar o operand = "OR"
		"""
		colnames = self._get_columns(table)

		Query = "SELECT "
		if print_table ==True: first_line = ""
		# Ver tipo de conteudo desejado
		if content == "*":
			Query += content
			Query += " FROM factory." + table
			if print_table ==True:
				for col in colnames:
					first_line += col + "\t"
		else:
			for cont in content:
				if cont in colnames:
					Query += cont + ","
					if print_table ==True: 
						first_line += cont + "\t"
			Query = Query[:-1] + " FROM factory." + table
		
		if where == None:
			if order_by in colnames:
				Query += " ORDER BY " + order_by
			data = self.select_query(Query)

		else:
			condition = []
			Query += " WHERE "
			for key,value in where.items():
				if key[-1].isdigit():
					key = key[:-1] 
				Query += key + "=%s " + operand + " "
				condition.append(str(value))
			if operand !="OR":
				Query = Query[:-5]
			else:
				Query = Query[:-4]

			if order_by in colnames:
				Query += " ORDER BY " + order_by

			data = self.select_query(Query, condition)
			
		if print_table ==True:
			print(first_line)
			for row in data:
				line = ""
				for column in row:
					line += str(column) + "\t\t"
				print(line)
		return data


	# Não testada
	def insert_machine_stats(self, data):
		"""
		data is a list of dictionaries in order of the machines A1, A2, ...
		"""
		machines = ["A1", "A2", "A3", "B1", "B2", "B3", "C1", "C2", "C3"]
		info = ("Total time", "P1", "P2", "P3", "P4", "P5", "P6", "P7", "P8", "P9", "Total")
		
		for row, machine_id in zip(data, machines):
			Query = "UPDATE factory.machines SET total_time = %s, P1 = %s, P2 = %s, P3 = %s, P4 = %s, P5 = %s, P6 = %s, P7 = %s, P8 = %s, P9 = %s, total = %s"
			values = []
			for col in info:
				if col not in list(row.keys()):
					values.append(str(0))
				else:
					values.append(str(row[col]))
			Query += " WHERE machine_type = %s AND transformation_cell = %s"
			values.append(machine_id[0])
			values.append(machine_id[1])
			self.insert_update_query(Query, values)






	def count_pieces(self):
		"""
		Retorna o numero de peças no armazem por cada tipo de peças num vetor ordenado
		"""
		# counted = [0] * 9
		# for index, _ in enumerate(counted, start = 1):
		# 	Query = "SELECT COUNT(piece_type) FROM factory.pieces WHERE piece_type = %s AND piece_state = %s"
		# 	self._cursor.execute(Query, (index,"stored",))
		# 	data = self._cursor.fetchall()
		# 	counted[index - 1] = data[0][0]


		Query = "SELECT (amount) FROM factory.stored_pieces ORDER BY piece_type"
		counted = self.select_query(Query)
		counted = [i[0] for i in counted]
		return counted


	def add_unloaded_pieces(self, piece_type, destination):
		"""
		Adds one piece to the unloaded db in the desired destination
		"""
		Query = "UPDATE factory.unloading_zones SET P" + str(piece_type) + " = P" + str(piece_type) + " + 1 WHERE area_id = %s"
		self.insert_update_query(Query, str(destination))

	def add_stored_pieces(self, piece_type, amount = 1):
		"""
		Adds one (or more) piece from the db
			db.add_stored_pieces(1)
		For cutom amount:
			db.add_stored_pieces(1, 12)
		"""

		Query = "UPDATE factory.stored_pieces SET amount = amount + " + str(amount) + " WHERE piece_type = %s"
		self.insert_update_query(Query,str(piece_type))


	def update_on_factory(self, table, id, quantity):
		"""
		Adds a piece that was placed on the factory in the db
		"""
		Query = "UPDATE factory." + table + " SET on_factory = " + str(quantity) + ", pending = (batch_size - produced - " + str(quantity) + ")  WHERE order_id = " + str(id) 
		self.insert_update_query(Query)



	def update_processed_transform(self, quant, id):
		Query = "UPDATE factory.transform_orders SET produced = " + str(quant) + ", pending = (batch_size - on_factory - " + str(quant) + ")  WHERE order_id = " + str(id)
		self.insert_update_query(Query)

	def subtract_stored_pieces(self, piece_type, amount = 1):
		"""
		Subtracts one (or more) piece from the db
			db.subtract_stored_pieces(1)
		For cutom amount:
			db.subtract_stored_pieces(1, 12)
		Note: If the subtraction would make the amount on the db negative, the amount is set to 0
		"""
		data = self.select("stored_pieces", content = ["amount"], where = {"piece_type" : piece_type})
		if (data[0][0] - amount <= 0):
			print("####### Numero de peças não pode ser negativo (", data[0][0] - amount,") #######")
			if (data[0][0] != 0):
				print("#######       Numero de peças na DB colocado a 0      #######")
				self.update_stored_pieces(piece_type, 0)
			return
		else:
			Query = "UPDATE factory.stored_pieces SET amount = amount - "+ str(amount) + " WHERE piece_type = %s"
			self.insert_update_query(Query,str(piece_type))


	def subtract_on_factory(self, table, id):
		"""
		Adds a piece that was placed on the factory in the db
		"""
		Query = "UPDATE factory." + table + " SET on_factory = on_factory - 1 WHERE order_id = " + str(id)

		self.insert_update_query(Query)


	def update_stored_pieces(self, piece_type, amount):
		"""
		Sets piece amount into the db
			db.update_stored_pieces(1, 12)
		"""
		Query = "UPDATE factory.stored_pieces SET amount = %s WHERE piece_type = %s"
		values_condition = [str(amount), str(piece_type)]

		self.insert_update_query(Query,values_condition)




if __name__ == "__main__":
	db = DB_handler()

	# import sys
	# sys.path.insert(0, "..")
	# sys.path.insert(0, "Receive_client_orders")
	# from Order import Order,TransformOrder, UnloadOrder
	# db.insert("transform_orders", order_id = 1, maxdelay = 300, before_type = 1, after_type = 2, batch_size = 20)
	# db.insert("transform_orders", order_id = 2, maxdelay = 300, before_type = 1, after_type = 2, batch_size = 10)

	# Order.give_db(db)

	# ex_order = TransformOrder(order_type="Transform", order_number= 1032,max_delay = 200, before_type= 1, after_type = 3, quantity= 10)
	# ex_oee = UnloadOrder(order_type="Unload", order_number= 12, piece_type = 1, destination = 3, quantity= 10)

	# db.update("transform_orders", where = {"order_id" : 1}, curr_state = "active" ,batch_size = 8)
	# dic = {"curr_state" : "active", "curr_state1": "pending"}
	# data = db.select("transform_orders", where = dic, operand= "OR" ,print_table= True, order_by= "order_id")
	# db.update_stored_pieces(3, 23)
	# db.add_stored_pieces(1)
	# db.subtract_stored_pieces(3, 50)
	# data = db.count_pieces()

	# data = []
	# for _ in range(9):
	# 	data.append({"Total time": 1, "P1" : 2, "P2" : 3, "P3" : 4, "P4" : 5, "P5" : 6, "P6" : 7, "P7" : 8, "P8" : 9, "P9" : 10, "Total" : 11})
	# db.insert_machine_stats(data)

	# db.subtract_on_factory("transform_orders", 1032)
	
	hello = db.select("unloading_zones")
	print(hello)