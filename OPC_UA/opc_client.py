import asyncio
import sys
import collections
from queue import Queue

sys.path.insert(0, "..")
import logging
import copy
import pickle
import numpy as np
from array import array
from asyncua import Client, Node, ua
from OPC_UA.subhandles import OptimizerSubHandler
from Optimizer.baby_optimizer import BabyOptimizer
from Optimizer.baby_optimizer import Piece
from Optimizer.baby_optimizer import Pusher
from lock import lock, optimization_lock

from Receive_client_orders.Order import TransformOrder, UnloadOrder

SUB_PERIOD = 20  # Publishing interval in miliseconds
LOG_FILENAME = 'opc_client.log'

logging.basicConfig(level=logging.DEBUG, filename=LOG_FILENAME)
logging.FileHandler(LOG_FILENAME, 'w+')
_logger = logging.getLogger('asyncua')

# Some Global Vars
path_length = 51
transf_length = 6

machine_dic = {'Ma_1': 4, 'Mb_1': 5, 'Mc_1': 6,
			   'Ma_2': 16, 'Mb_2': 17, 'Mc_2': 18,
			   'Ma_3': 28, 'Mb_3': 29, 'Mc_3': 30, 0: 0}

tool_dic = {'T1': 1, 'T2': 2, 'T3': 3}


class OnePiece():
	'''
	Classe Piece deveria ser importada mas sou lazy as **** 

	'''

	def __str__(self):
		return self.id

	async def write_int16(self, var, value):
		datavalue = ua.DataValue(ua.Variant(value, ua.VariantType.Int16))
		await var.write_value(datavalue)

	async def write_array_int16(self, var, array, Array_LENGTH):
		array.extend(np.zeros(Array_LENGTH - len(array), dtype=int))
		datavalue = ua.DataValue(ua.Variant(array, ua.VariantType.Int16))
		await var.write_value(datavalue)

	async def write_bool(self, var, value):
		datavalue = ua.DataValue(ua.Variant(value, ua.VariantType.Boolean))
		await var.write_value(datavalue)

	async def send_path(self, piece,
						var_write):  # piece, var_path, var_id, var_maq, var_tool, var_new_piece, var_tipo_atual):
		await self.write_array_int16(var_write["path"], piece.path,
									 path_length)  # set node value using implicit data type
		await self.write_int16(var_write["id"], piece.id)  # set node value using implicit data type
		await self.write_int16(var_write["tipo_atual"], piece.type)
		if piece.order.order_type == 'Transform':
			machine_translated = [machine_dic[machine] for machine in piece.machines]
			tools_translated = [tool_dic[tool] for tool in piece.tools]
			await self.write_array_int16(var_write["maq"], machine_translated, transf_length)
			await self.write_array_int16(var_write["tool"], tools_translated, transf_length)
		await self.write_bool(var_write["new_piece"], True)
		return


async def write(var_write, optimizer, cond, cond_pusher1, cond_pusher2, cond_pusher3):
	# print("######################debug: write() started")
	sender = OnePiece()
	PIECES_TO_SEND = 3

	if optimizer.pusher.dispatch_queue_1 and cond_pusher1.is_set():
		for p in range(PIECES_TO_SEND):
			if optimizer.pusher.dispatch_queue_1 and optimizer.pusher.count_1 < 3:
				optimizer.pusher.count_1 += 1
				piece = optimizer.pusher.dispatch_queue_1.popleft()
				optimizer.dispatch_queue.appendleft(piece)
		if optimizer.pusher.count_1 >= 3:
			cond_pusher1.clear()

	elif optimizer.pusher.dispatch_queue_2 and cond_pusher2.is_set():
		for p in range(PIECES_TO_SEND):
			if optimizer.pusher.dispatch_queue_2 and optimizer.pusher.count_2 < 3:
				optimizer.pusher.count_2 += 1
				piece = optimizer.pusher.dispatch_queue_2.popleft()
				optimizer.dispatch_queue.appendleft(piece)
		if optimizer.pusher.count_2 >= 3:
			cond_pusher2.clear()

	elif optimizer.pusher.dispatch_queue_3 and cond_pusher3.is_set():
		for p in range(PIECES_TO_SEND):
			if optimizer.pusher.dispatch_queue_3 and optimizer.pusher.count_3 < 3:
				optimizer.pusher.count_3 += 1
				piece = optimizer.pusher.dispatch_queue_3.popleft()
				optimizer.dispatch_queue.appendleft(piece)
		if optimizer.pusher.count_3 >= 3:
			cond_pusher3.clear()

	elif optimizer.dispatch_queue:
		piece = optimizer.dispatch_queue[0]
		first_type = optimizer.dispatch_queue[0].type
		if cond.is_set():
			if optimizer.stock[first_type] <= 0:
				lock.acquire()
				optimization_lock.acquire()
				print('OH SHIT OH FUCK N TENHO PEÇAS PARA ISSO')
				optimizer.orders2do = copy.copy(optimizer.active_orders)
				optimizer.active_orders.clear()
				print(optimizer.orders2do)
				if piece.order.order_type == 'Transform':
					for m in optimizer.state.machines.values():
						new_oplist = [op for op in m.op_list if op.piece_id  in optimizer.tracker.pieces_on_transit]
						removed_ops = [op for op in m.op_list if op.piece_id not in optimizer.tracker.pieces_on_transit]
						if not new_oplist: m.make_available()
						for op in removed_ops:
							m.waiting_time -= op.transform.duration
						m.op_list = collections.deque(new_oplist)
				optimizer.dispatch_queue.clear()
				lock.release()
				optimization_lock.release()
			else:
				print('TA FIXE MANO')
				piece = optimizer.dispatch_queue.popleft()
				#print("id: ", piece.id, " path: ", piece.path)
				# await block_pieces.wait()
				if (piece.id not in optimizer.tracker.pieces_on_transit) \
					and (piece.id not in optimizer.tracker.pieces_complete):
					await sender.send_path(piece, var_write)
					print(f"Dispatching piece no {piece.id}: ")
					optimizer.tracker.mark_dispatched(piece.id)
					optimizer.print_machine_schedule()
					cond.clear()
				await asyncio.sleep(1)


async def swap_tools(tool_nodes, optimizer):
	# print('#debug swap tools')
	sender = OnePiece()
	for machine in optimizer.state.machines.values():
		if machine.next_tool:
			# print(f'{machine.id}: {tool_nodes[machine.id]} {tool_dic[machine.next_tool]} {type(tool_dic[machine.next_tool])}')
			await sender.write_int16(tool_nodes[machine.id], tool_dic[machine.next_tool])
		elif machine.op_list:
			machine.next_tool = machine.op_list[0].transform.tool
		else:
			continue


async def read(client, vars, handler):
	print("######################debug: read() started")
	sub = await client.create_subscription(SUB_PERIOD, handler)
	await sub.subscribe_data_change(vars)


async def charge_P1(client, cond_p1, charge_var):
	# print('#debug Charge P1')
	sender = OnePiece()
	dest_path = [39, 41, 42, 43, 44, 45, 46, 38, 31, 26, 19, 14, 7, 2]
	var_load_path = client.get_node("ns=4;s=|var|CODESYS Control Win V3 x64.Application.GVL.piece_array[40].path")
	var_load_tipo_atual = client.get_node(
		"ns=4;s=|var|CODESYS Control Win V3 x64.Application.GVL.piece_array[40].tipo_atual")
	# var_load_id

	# if (await charge_var.get_value()):
	if cond_p1:
		# await cond_p1.wait()
		# print("OOOOOOOOOOOOOOOOOOOOOOOOOOOO", await charge_var.get_value())
		# await self.write_int16(var_write["id"], piece.id)  # set node value using implicit data type
		await sender.write_int16(var_load_tipo_atual, 1)
		await sender.write_array_int16(var_load_path, dest_path,
									   path_length)  # set node value using implicit data type

		cond_p1.clear()


async def charge_P2(client, cond_p2, charge_var):
	# print('#debug Charge P2')
	sender = OnePiece()
	dest_path = [46, 38, 31, 26, 19, 14, 7, 2]
	var_load_path = client.get_node("ns=4;s=|var|CODESYS Control Win V3 x64.Application.GVL.piece_array[47].path")
	var_load_tipo_atual = client.get_node(
		"ns=4;s=|var|CODESYS Control Win V3 x64.Application.GVL.piece_array[47].tipo_atual")

	# if (await charge_var.get_value()):
	# await cond_p2.wait()
	if cond_p2:
		# print("OOOOOOOOOOOOOOOOOOOOOOOOOOOO", await charge_var.get_value())
		await sender.write_int16(var_load_tipo_atual, 2)
		await sender.write_array_int16(var_load_path, dest_path,
									   path_length)  # set node value using implicit data type
		await asyncio.sleep(2)
		cond_p2.clear()


async def unload(optimizer, cond_pusher_1):
	# print('#debug UNLOAD')
	while True:
		if optimizer.pusher.dispatch_queue_1:
			await cond_pusher_1.wait()

			optimizer.pusher.count_1=0
			order_ = optimizer.pusher.dispatch_queue_1.popleft()

			print("quantidade em falta: ", order_.quantity)
			optimizer.order_handler(order_)
			cond_pusher_1.clear()
		await asyncio.sleep(1)

async def get_stocks(optimizer, stock_nodes):
	for type in range(1,10):
		optimizer.stock[type] = await stock_nodes[type].get_value()
	#print(optimizer.stock)
	return optimizer.stock

async def opc_client_run(optimizer, loop):
	url = 'opc.tcp://localhost:4840/'
	print('Connecting to PLC')
	async with Client(url=url) as client:
		print('Reading Node information')

		vars_to_write = client.get_node("ns=4;s=|var|CODESYS Control Win V3 x64.Application.GVL.piece_array[0]")
		var_id = await vars_to_write.get_child("4:id")
		var_path = await vars_to_write.get_child("4:path")
		var_maq = client.get_node("ns=4;s=|var|CODESYS Control Win V3 x64.Application.GVL.piece_array[0].transf.maq")
		var_tool = client.get_node("ns=4;s=|var|CODESYS Control Win V3 x64.Application.GVL.piece_array[0].transf.tool")
		var_new_piece = client.get_node("ns=4;s=|var|CODESYS Control Win V3 x64.Application.GVL.new_piece")
		var_tipo_atual = client.get_node(
			"ns=4;s=|var|CODESYS Control Win V3 x64.Application.GVL.piece_array[0].tipo_atual")

		var_write = {"id": var_id,
					 "path": var_path,
					 "maq": var_maq,
					 "tool": var_tool,
					 "new_piece": var_new_piece,
					 "tipo_atual": var_tipo_atual}

		# Subscrições para monitorizar as maquinas
		ma_1, mb_1, mc_1 = client.get_node("ns=4;s=|var|CODESYS Control Win V3 x64.Application.tapetes.c1t3") \
			, client.get_node("ns=4;s=|var|CODESYS Control Win V3 x64.Application.tapetes.c1t4") \
			, client.get_node("ns=4;s=|var|CODESYS Control Win V3 x64.Application.tapetes.c1t5")
		ma_2, mb_2, mc_2 = client.get_node("ns=4;s=|var|CODESYS Control Win V3 x64.Application.tapetes.c3t3") \
			, client.get_node("ns=4;s=|var|CODESYS Control Win V3 x64.Application.tapetes.c3t4") \
			, client.get_node("ns=4;s=|var|CODESYS Control Win V3 x64.Application.tapetes.c3t5")

		ma_3, mb_3, mc_3 = client.get_node("ns=4;s=|var|CODESYS Control Win V3 x64.Application.tapetes.c5t3") \
			, client.get_node("ns=4;s=|var|CODESYS Control Win V3 x64.Application.tapetes.c5t4") \
			, client.get_node("ns=4;s=|var|CODESYS Control Win V3 x64.Application.tapetes.c5t5")

		m_steps = await ma_1.get_children() + await mb_1.get_children() + await mc_1.get_children()
		m_steps += await ma_2.get_children() + await mb_2.get_children() + await mc_2.get_children()
		m_steps += await ma_3.get_children() + await mb_3.get_children() + await mc_3.get_children()

		m_vars = []
		for step in m_steps:
			nodes = await step.get_children()
			for node in nodes:
				m_vars.append(node)

		tool_nodes = {
			'Ma_1': client.get_node("ns=4;s=|var|CODESYS Control Win V3 x64.Application.GVL.next_tool_c1t3"),
			'Ma_2': client.get_node("ns=4;s=|var|CODESYS Control Win V3 x64.Application.GVL.next_tool_c3t3"),
			'Ma_3': client.get_node("ns=4;s=|var|CODESYS Control Win V3 x64.Application.GVL.next_tool_c5t3"),
			'Mb_1': client.get_node("ns=4;s=|var|CODESYS Control Win V3 x64.Application.GVL.next_tool_c1t4"),
			'Mb_2': client.get_node("ns=4;s=|var|CODESYS Control Win V3 x64.Application.GVL.next_tool_c3t4"),
			'Mb_3': client.get_node("ns=4;s=|var|CODESYS Control Win V3 x64.Application.GVL.next_tool_c5t4"),
			'Mc_1': client.get_node("ns=4;s=|var|CODESYS Control Win V3 x64.Application.GVL.next_tool_c1t5"),
			'Mc_2': client.get_node("ns=4;s=|var|CODESYS Control Win V3 x64.Application.GVL.next_tool_c3t5"),
			'Mc_3': client.get_node("ns=4;s=|var|CODESYS Control Win V3 x64.Application.GVL.next_tool_c5t5")
		}

		stock_nodes = {}
		for ptype in range(1, 10):
			print(str(ptype))
			stock_nodes[ptype] = client.get_node("ns=4;s=|var|CODESYS Control Win V3 x64.Application.GVL.p" + str(ptype))

		var_despacha_1_para_3 = client.get_node("ns=4;s=|var|CODESYS Control Win V3 x64.Application.tapetes.at1.Init.x")
		m_vars.append(var_despacha_1_para_3)

		vars_P1_charge = client.get_node("ns=4;s=|var|CODESYS Control Win V3 x64.Application.GVL.c7t7a_i.sensor")
		vars_P2_charge = client.get_node("ns=4;s=|var|CODESYS Control Win V3 x64.Application.GVL.c7t7b_i.sensor")
		m_vars.append(vars_P1_charge)
		m_vars.append(vars_P2_charge)

		pusher1 = client.get_node("ns=4;s=|var|CODESYS Control Win V3 x64.Application.GVL.vazio_ramp1")
		m_vars.append(pusher1)
		pusher2 = client.get_node("ns=4;s=|var|CODESYS Control Win V3 x64.Application.GVL.vazio_ramp2")
		m_vars.append(pusher2)
		pusher3 = client.get_node("ns=4;s=|var|CODESYS Control Win V3 x64.Application.GVL.vazio_ramp3")
		m_vars.append(pusher3)

		warehouse_in = client.get_node('ns=4;s=|var|CODESYS Control Win V3 x64.Application.GVL.piece_array[2].id')
		m_vars.append(warehouse_in)

		cond = asyncio.Event()
		cond_p1 = asyncio.Event()
		cond_p2 = asyncio.Event()

		cond_pusher_1 = asyncio.Event()
		cond_pusher_2 = asyncio.Event()
		cond_pusher_3 = asyncio.Event()
		cond_pusher_1.set()
		cond_pusher_2.set()
		cond_pusher_3.set()

		handler = OptimizerSubHandler(optimizer, cond, cond_p1, cond_p2, cond_pusher_1, cond_pusher_2, cond_pusher_3, _logger)

		print("MES-PLC OpcUA Connection established")

		await read(client, m_vars, handler)

		# loop = asyncio.get_event_loop()

		while True:
			await asyncio.gather(
				write(var_write, optimizer, cond, cond_pusher_1, cond_pusher_2, cond_pusher_3),
				charge_P1(client, cond_p1, vars_P1_charge),
				charge_P2(client, cond_p2, vars_P2_charge),
				swap_tools(tool_nodes, optimizer),
				#unload(optimizer, cond_pusher_1)
			)
			await get_stocks(optimizer, stock_nodes)


if __name__ == '__main__':
	optimizer = BabyOptimizer()
	loop = asyncio.get_event_loop()
	loop.set_debug(True)
	loop.run_until_complete(opc_client_run(optimizer))
	loop.close()
