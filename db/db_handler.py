import psycopg2

class DB_handler:
	def __init__(self):
		try:
			self._connection = psycopg2.connect(user = "ii",
									password = "iisuckz",
									host = "192.168.99.100",
									port = "5432") #https://stackoverflow.com/questions/32812463/setting-schema-for-all-queries-of-a-connection-in-psycopg2-getting-race-conditi


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

		except(Exception, psycopg2.Error) as error:
			print("Error while connecting to PostgreSQL", error) 

	def __del__(self):
		self.close()

	def _get_columns(self, table):
		Query = "SELECT * FROM factory." + table + " LIMIT 0"

		self._cursor.execute(Query)
		colnames = [names[0] for names in self._cursor.description]
		return colnames

	def close(self):
		"""Termina a conecção"""
		if (self._connection):
			self._cursor.close()
			self._connection.close()
			print("Database connection closed")
	


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

		try:
			self._cursor.execute(Query,tuple(values))
			self._connection.commit()
		except(Exception, psycopg2.Error) as error:
			print("Error while connecting to PostgreSQL", error)

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
		for key, vals in kwargs.items():
			if key in colnames:
				Query += key + " = %s,"
				values.append(str(vals))
		Query = Query[:-1]

		condition = []
		Query += " WHERE "
		for key,value in where.items():
			Query += key + "=%s AND "
			condition.append(str(value))
		Query = Query[:-5]

		values_condition = values + condition

		try:
			self._cursor.execute(Query,tuple(values_condition))
			self._connection.commit()
		except(Exception, psycopg2.Error) as error:
			print("Error while connecting to PostgreSQL", error)

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
			try:
				self._cursor.execute(Query)
			except(Exception, psycopg2.Error) as error:
				print("Error while connecting to PostgreSQL", error)
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

			try:
				self._cursor.execute(Query,tuple(condition))
			except(Exception, psycopg2.Error) as error:
				print("Error while connecting to PostgreSQL", error)

		data = self._cursor.fetchall()
		if print_table ==True:
			print(first_line)
			for row in data:
				line = ""
				for column in row:
					line += str(column) + "\t\t"
				print(line)
		return data




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
		self._cursor.execute(Query)
		counted = self._cursor.fetchall()
		counted = [i[0] for i in counted]
		return counted




	def add_stored_pieces(self, piece_type, amount = 1):
		"""
		Adds one (or more) piece from the db
			db.add_stored_pieces(1)
		For cutom amount:
			db.add_stored_pieces(1, 12)
		"""

		Query = "UPDATE factory.stored_pieces SET amount = amount + " + str(amount) + " WHERE piece_type = %s"
		try:
			self._cursor.execute(Query,tuple(str(piece_type)))
			self._connection.commit()
		except(Exception, psycopg2.Error) as error:
			print("Error while connecting to PostgreSQL", error)


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
		Query = "UPDATE factory.stored_pieces SET amount = amount - "+ str(amount) + " WHERE piece_type = %s"
		
		try:
			self._cursor.execute(Query,tuple(str(piece_type)))
			self._connection.commit()
		except(Exception, psycopg2.Error) as error:
			print("Error while connecting to PostgreSQL", error)


	def update_stored_pieces(self, piece_type, amount):
		"""
		Sets piece amount into the db
			db.update_stored_pieces(1, 12)
		"""
		Query = "UPDATE factory.stored_pieces SET amount = %s WHERE piece_type = %s"
		values_condition = [str(amount), str(piece_type)]
		try:
			self._cursor.execute(Query,tuple(values_condition))
			self._connection.commit()
		except(Exception, psycopg2.Error) as error:
			print("Error while connecting to PostgreSQL", error)



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
	db.add_stored_pieces(1)
	db.subtract_stored_pieces(3, 50)
	data = db.count_pieces()
	print(data)