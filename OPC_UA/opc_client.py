import asyncio
import sys
import collections
from queue import Queue

sys.path.insert(0, "..")
import logging
import pickle
import numpy as np
from array import array
from asyncua import Client, Node, ua
from OPC_UA.subhandles import OptimizerSubHandler
from Optimizer.baby_optimizer import BabyOptimizer
from Optimizer.baby_optimizer import Piece


from Receive_client_orders.Order import TransformOrder

SUB_PERIOD = 20 #Publishing interval in miliseconds
LOG_FILENAME = 'opc_client.log'

logging.basicConfig(level=logging.DEBUG, filename=LOG_FILENAME)
_logger = logging.getLogger('asyncua')


#Some Global Vars
path_length=51
transf_length=6	

machine_dic = {'Ma_1': 1, 'Mb_1': 2, 'Mc_1': 3,
			   'Ma_2': 1, 'Mb_2': 2, 'Mc_2': 3,
			   'Ma_3': 1, 'Mb_3': 2, 'Mc_3': 3}

tool_dic = {'T1': 1, 'T2': 2, 'T3': 3}

class OnePiece():
	'''
	Classe Piece deveria ser importada mas sou lazy as **** 

	'''
	def __init__(self, id, optimizer, order):
		self.id = id
		self.optimizer=optimizer
		self.waiting_time = 0
		self.order=order


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


	async def send_path(self, piece, var_write):#piece, var_path, var_id, var_maq, var_tool, var_new_piece, var_tipo_atual):
		machine_translated = [machine_dic[machine] for machine in piece.machines]
		tools_translated = [tool_dic[tool] for tool in piece.tools]
		print(piece.tools)
		await self.write_array_int16(var_write["path"], piece.path, path_length)  # set node value using implicit data type
		await self.write_int16(var_write["id"], piece.id)  # set node value using implicit data type
		await self.write_int16(var_write["tipo_atual"], piece.type)
		await self.write_array_int16(var_write["maq"], machine_translated, transf_length)
		await self.write_array_int16(var_write["tool"], tools_translated, transf_length)
		await self.write_bool(var_write["new_piece"], True)
		return


async def write(client, vars, optimizer, q_udp_in, cond):
	print("######################debug: write() started")

	orders_client = []
	
	#vars Escrita
	
	var_id= await vars.get_child("4:id")
	var_path = await vars.get_child("4:path")
	var_maq = client.get_node("ns=4;s=|var|CODESYS Control Win V3 x64.Application.GVL.piece_array[0].transf.maq")
	var_tool = client.get_node("ns=4;s=|var|CODESYS Control Win V3 x64.Application.GVL.piece_array[0].transf.tool")
	var_new_piece = client.get_node("ns=4;s=|var|CODESYS Control Win V3 x64.Application.GVL.new_piece")
	var_tipo_atual = client.get_node("ns=4;s=|var|CODESYS Control Win V3 x64.Application.GVL.piece_array[0].tipo_atual")
	
	var_write={"id" : var_id, 
				"path" : var_path, 
				"maq" : var_maq, 
				"tool" : var_tool, 
				"new_piece" : var_new_piece, 
				"tipo_atual" : var_tipo_atual}
	

	#id=1
	sender = OnePiece(None, None, None)
	
	

	
	
	while True:
		

		while optimizer.dispatch_queue:
			#lock
			#async with cond:
			if True:
				async with cond:
					piece = optimizer.dispatch_queue.popleft()
					###########################################
					# codigo amazing para mandar as peças##
					print('codigo amazing para mandar as peças \m/')
					await sender.send_path(piece, var_write)
					###########################################
					print(f"Dispatching piece no {piece.id}")
				
					await cond.wait()
				#await asyncio.sleep(5)
				
		await asyncio.sleep(0.2)
		
		
		
async def sentinela(client, cond):
	#vars Leitura
	var_despacha_1_para_3= client.get_node("ns=4;s=|var|CODESYS Control Win V3 x64.Application.tapetes.at1._entregar_posterior_o.x")
	print( "VALLLL", await var_despacha_1_para_3.get_value())
	while True:
		if (await var_despacha_1_para_3.get_value()):
			print('noted!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
			await cond.set()
			break
		


async def read(client, vars, handler):
	print("######################debug: read() started")

	sub = await client.create_subscription(SUB_PERIOD, handler)
	await sub.subscribe_data_change(vars)



async def main(q_udp_in):
	url = 'opc.tcp://localhost:4840/'

	####################################### Isto n deve tar aqui é so para testar sem precisar de enviar ordens #################################
	optimizer = BabyOptimizer()

	fake_order = []

	fake_order.append(TransformOrder(order_type="Transform", order_number=1,
									 max_delay=2000, before_type=2, after_type=6, quantity=9))
	fake_order.append(TransformOrder(order_type="Transform", order_number=2,
									 max_delay=2000, before_type=4, after_type=5, quantity=9))
	fake_order.append(TransformOrder(order_type="Transform", order_number=3,
									 max_delay=2000, before_type=7, after_type=9, quantity=9))

	for order in fake_order:
		print(
			f"Order number {order.order_number}. {order.quantity} transforms from P{order.before_type} to P{order.after_type}")
		optimizer.order_handler(order)
		print(f'Total number of pieces: {optimizer.state.num_pieces}\r\n')

	print(f'Optimizing {optimizer.state.num_pieces} pieces')
	optimizer.state = optimizer.optimize_all_pieces()
	print(f'{optimizer.state}')
	optimizer.print_machine_schedule()
	#############################################################################################################################################

	async with Client(url=url) as client:

		vars_to_write = client.get_node("ns=4;s=|var|CODESYS Control Win V3 x64.Application.GVL.piece_array[0]")

		#Subscrições para monitorizar as maquinas
		ma, mb, mc = client.get_node("ns=4;s=|var|CODESYS Control Win V3 x64.Application.tapetes.c1t3")\
						, client.get_node("ns=4;s=|var|CODESYS Control Win V3 x64.Application.tapetes.c1t4")\
							, client.get_node("ns=4;s=|var|CODESYS Control Win V3 x64.Application.tapetes.c1t5")
		m_steps = await ma.get_children() + await mb.get_children() + await mc.get_children()
		m_vars = []
		for step in m_steps:
			nodes = await step.get_children()
			for node in nodes:
				m_vars.append(node)

		cond = asyncio.Event()

		handler = OptimizerSubHandler(optimizer, _logger)
		await asyncio.gather(read(client, m_vars, handler), write(client, vars_to_write, optimizer, q_udp_in, cond), sentinela(client, cond))
		

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