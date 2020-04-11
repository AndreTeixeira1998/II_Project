import asyncio
import sys
from queue import Queue

sys.path.insert(0, "..")
import logging
import pickle
import numpy as np
from asyncua import Client, Node, ua
from OPC_UA.subhandles import OptimizerSubHandler
from Optimizer.baby_optimizer import BabyOptimizer

SUB_PERIOD = 20 #Publishing interval in miliseconds
LOG_FILENAME = 'opc_client.log'

logging.basicConfig(level=logging.DEBUG, filename=LOG_FILENAME)
_logger = logging.getLogger('asyncua')


class Piece():
	'''
	Classe Piece deveria ser importada mas sou lazy as **** 

	'''
	def __init__(self, id, optimizer):
		self.id = id
		self.optimizer=optimizer
		self.waiting_time = 0

	def __str__(self):
		return self.id
		
	async def write_int16(self, var, value):
		datavalue = ua.DataValue(ua.Variant(value, ua.VariantType.Int16))
		await var.write_value(datavalue)

	async def write_array_int16(self, var, array, Array_LENGTH):
		array.extend(np.zeros(Array_LENGTH-len(array), dtype=int))
		datavalue = ua.DataValue(ua.Variant(array, ua.VariantType.Int16))
		await var.write_value(datavalue)

	async def write_bool(self, var, value):
		datavalue = ua.DataValue(ua.Variant(value, ua.VariantType.Boolean))
		await var.write_value(datavalue)

	def update_path(self, before, after):
		duration, piece, trans_path = self.optimizer.compute_transform(before, after)
		path_to_write = self.optimizer.compute_path(trans_path)
		return duration, piece, trans_path, path_to_write



########################################## Isto não deveria estar aqui ################################################
def order_handler(order):
	if order.get("order_type") == "Request_Stores":
		return None
	else: 
		pieces = []
		count = 0
		while count != order.get("quantity"):
			p = [order.get("before_type"), order.get("after_type")]
			pieces.append(p)
			count += 1
	return pieces
#######################################################################################################################

async def write(client, vars, optimizer, q_udp_in):
	print("######################debug: write() started")
	
	orders_client = []
	
	var_id= await vars.get_child("4:id")
	var_path = await vars.get_child("4:path")
	var_maq = client.get_node("ns=4;s=|var|CODESYS Control Win V3 x64.Application.GVL.piece_array[0].transf.maq")
	var_tool = 1
	var_new_piece = client.get_node("ns=4;s=|var|CODESYS Control Win V3 x64.Application.GVL.new_piece")
	
	path_length=51
	transf_length=6
	
	id=1
	
	while True:
	
		########################################## Isto não deveria estar aqui ################################################

		while not q_udp_in.empty():
			order = q_udp_in.get()
			for o in order:
				orders_client.append(o)
		#######################################################################################################################

		for order in orders_client:
			### No final vai ter que se fazer pop à order, esqueci-me, upsie daisy
			pieces = order_handler(order)
			p = Piece(id, optimizer)
			id+=1
			for piece in pieces:


				_, _, _, path_to_write =p.update_path(piece[0], piece[1])
		
				await asyncio.sleep(5)
				try:
					print("###############################    Changing Value!   ###############################")
					await p.write_array_int16(var_path, path_to_write, path_length) # set node value using implicit data type
					await p.write_int16(var_id, p.id) # set node value using implicit data type
		
				except:
					print("!!!!!!!!!!!!!!!!!!!!!!!  ERROR  Changing Value!   !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")

	


async def read(client, vars, optimizer):
	print("######################debug: read() started")
	
	handler = OptimizerSubHandler(optimizer, _logger)

	sub = await client.create_subscription(SUB_PERIOD, handler)
	await sub.subscribe_data_change(vars)



async def main(q_udp_in):
	url = 'opc.tcp://localhost:4840/'
	
	#Load optimizer configs from a pickle
	with open("./Optimizer/config/babyFactory.pickle", "rb") as config_pickle: 
		optimizer = pickle.load(config_pickle)
	
	async with Client(url=url) as client:

		vars_to_write = client.get_node("ns=4;s=|var|CODESYS Control Win V3 x64.Application.GVL.piece_array[0]") 
		vars_to_read = await vars_to_write.get_children()

		
		await asyncio.gather(read(client, vars_to_read, optimizer), write(client, vars_to_write, optimizer, q_udp_in))
		

		#Runs for 1 min
		#TODO: Change this into a permanent connection
		await asyncio.sleep(100)

if __name__ == '__main__':
	#para testar nao esquecer de alterar path do config de . para ..
	q_udp_in=1
	loop = asyncio.get_event_loop()
	loop.set_debug(True)
	loop.run_until_complete(main(q_udp_in))
	loop.close()