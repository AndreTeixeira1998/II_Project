import time
import asyncio
import collections
import copy
from Optimizer.transfgraph import TransfGraph, Transform, Machine, Operation
from Optimizer.search import dijkstra
from Optimizer.pathing.pathgraph import Conveyor, PathGraph
from Optimizer.pathing.dijkstra import dijkstra_conveyors
from OPC_UA.subhandles import OptimizerSubHandler
from Receive_client_orders.Order import TransformOrder, UnloadOrder
from Optimizer.config import setup
from lock import *
TOOL_SWAP_DURATION = 20
OPTIMIZATION_TIMEOUT = 60


class Tracker:
	def __init__(self, state, order_tracking={}, pcomplete={}, ptransit={}):
		self.order_tracking = {}
		self.pieces_complete = pcomplete
		self.pieces_on_transit = ptransit
		self.state = state

	def add_order(self, order):
		if order not in self.order_tracking.keys():
			self.order_tracking[order] = 0
			order.begin_order()

	def mark_complete(self, piece_id):
		print(f'Mark_completed {piece_id}')
		curr_order = self.state.pieces[piece_id].order
		curr_order.on_factory -= 1
		curr_order.processed += 1
		self.pieces_complete[piece_id] = self.pieces_on_transit[piece_id]
		self.pieces_on_transit.pop(piece_id)
		self.order_tracking[curr_order] += 1
		quantity = self.order_tracking[curr_order]
		if quantity == curr_order.get("quantity"):
			curr_order.order_complete()
		else:
		#	print('Updating processed')
			curr_order.update_processed(quantity)
		#	print('Updated')
		self.check_cell3_clearance()
		self.check_mb3_clearance()

	def mark_unloaded(self, piece_id):
		#print(f'Mark_completed {piece_id}')
		curr_order = self.state.pieces[piece_id].order
		self.pieces_complete[piece_id] = self.pieces_on_transit[piece_id]
		self.pieces_on_transit.pop(piece_id)
		curr_order.on_factory -= 1
		curr_order.unloaded += 1
		self.order_tracking[curr_order] += 1
		quantity = self.order_tracking[curr_order]
		if quantity == curr_order.get("quantity"):
			curr_order.order_complete()
		else:
			#print('Updating processed')
			curr_order.update_processed(quantity)
			if curr_order.order_type=='Transform':
				curr_order.update_on_factory()
			#print('Updated')

	def mark_dispatched(self, piece_id):
		#print(f'Mark_dispatched {piece_id} -> order {self.state.pieces[piece_id].order.order_number}')
		curr_order = self.state.pieces[piece_id].order
		curr_order.on_factory += 1
		self.pieces_on_transit[piece_id] = self.state.pieces[piece_id]
		self.state.pieces[piece_id].order.order_activated()
		if curr_order.order_type=='Transform':
			curr_order.update_on_factory()

	def print_tracking_info(self):
		pass
		print(f'Pieces on transit: {[pieceid for pieceid in self.pieces_on_transit.keys()]}')
		print(f'Pieces complete: {[pieceid for pieceid in self.pieces_complete.keys()]}')

	def print_order_status(self):
		for order in self.order_tracking.keys():
			pass
			print(f"Order {order.order_number}: {self.order_tracking[order]}/{order.quantity}")

	def check_cell3_clearance(self):
		if self.pieces_on_transit.keys():
			for piece_id in self.pieces_on_transit.keys():
				piece = self.state.pieces[piece_id]
				if piece.order.order_type == 'Transform':
					for m in piece.machines:
						if m == 'Ma_3' or m == 'Mb_3':
							#print('CELL 3 is busy')
							cell3_is_clear.clear()
							return False
			#print('CELL 3 is clear')
			cell3_is_clear.set()
			return True
		else:
			#print('No pieces on factory floor')
			cell3_is_clear.set()
			return True

	def check_mb3_clearance(self):
		if self.pieces_on_transit.keys():
			for piece_id in self.pieces_on_transit.keys():
				piece = self.state.pieces[piece_id]
				if piece.order.order_type == 'Transform':
					for m in piece.machines:
						if m == 'Mb_3':
							#print('Machine B3 is busy')
							mb3_is_clear.clear()
							return False
			#print('machine B3 is clear')
			mb3_is_clear.set()
			return True
		else:
			#print('No pieces on factory floor')
			mb3_is_clear.set()
			return True

# TODO adaptar isto

class Pusher():
	def __init__(self):
		self.dispatch_queue_1 = collections.deque([])
		self.dispatch_queue_2 = collections.deque([])
		self.dispatch_queue_3 = collections.deque([])
		self.count_1 = 0
		self.count_2 = 0
		self.count_3 = 0

	def push(self, order):
		if order.destination == 1:
			return self.dispatch_queue_1.append(order)
		if order.destination == 2:
			return self.dispatch_queue_2.append(order)
		if order.destination == 3:
			return self.dispatch_queue_3.append(order)


class Piece():
	'''
	Há de fazer grandes coisas esta classe
	'''

	def __init__(self, id, type, path, machines, tools, order=None, var=None):
		self.id = id
		self.type = type
		self.waiting_time = 0
		self.path = path
		self.machines = machines
		self.tools = tools
		self.order = order

	def __str__(self):
		return str(self.id)


class State:
	'''
	Piece and machine status at a given time
	'''

	def __init__(self, machines={}, pieces={}):
		self.machines = machines
		self.pieces = pieces
		self.num_pieces = 1  # hotfix para o tracker
		self.pieces_optimized = 1  # hotfix para o tracker

	def __str__(self):
		return f'{self.pieces_optimized}/{self.num_pieces}: {[(m.id, m.curr_tool, m.waiting_time) for m in self.machines.values()]}'

	def __eq__(self, other):
		return self.__str__() == other.__str__()

	def __lt__(self, other):
		return self.get_value() < self.get_value()

	def get_value(self):
		return max(m.waiting_time for m in self.machines.values())


class Optimizer:
	'''
		Simple optimizer for a single cell.
		Does not take into account time waiting for a machine to be free
		-> assumes all machines are available
		Only checks which sequence of transforms is faster
		Borderline useless for now
		'''

	def __init__(self):
		self.factory_state = {}  # variaveis monitorizadas por opc-ua
		self.transf_graph = {}
		self.path_graph = None
		self.direct_graph = PathGraph()
		self.reverse_graph = PathGraph()
		self.recipes = {}
		self.direct_recipes = {}
		self.reverse_recipes = {}
		self.stock = {}
		self.state = State()
		self.tracker = Tracker(self.state)
		self.pusher = Pusher()
		self.dispatch_queue = collections.deque([])
		self.active_orders = []
		self.is_reversed = False
		self.orders2do = []
		setup.optimizer_init(self)

	def update_state(self, node, val):
		self.factory_state[node] = val

	def print_state(self):
		print('==================== Current Factory State ===============================')
		[print(f"{key}: {value}") for key, value in self.factory_state.items()]
		print('==========================================================================\r\n')

	def add_transform_cell(self, cell_id: int):
		self.transf_graph[cell_id] = TransfGraph();

	def add_piece_type(self, type, cell_id: int):
		self.transf_graph[cell_id].add_vertex(type)

	def add_transform(self, frm, to, transform: Transform, cell_id: int):
		return self.transf_graph[cell_id].add_edge(frm, to, transform)

	def add_machine(self, name):
		if name not in self.state.machines.keys():
			self.state.machines[name] = Machine(name)
		else:
			raise NameError(f"Machine {name} already exists")

	def print_machine_schedule(self):
		for machine in self.state.machines.values():
			print(f"{machine.id}: {[str(op) for op in machine.op_list]}")

	def print_pusher_queues(self):
		print(f'P1: {[piece.id for piece in self.pusher.dispatch_queue_1]}')
		print(f'P2: {[piece.id for piece in self.pusher.dispatch_queue_2]}')
		print(f'P3: {[piece.id for piece in self.pusher.dispatch_queue_3]}')

	def add_conveyor(self, graph, id_):
		return graph.add_vertex(id_)

	def add_conveyor_path(self, graph, frm, to, cost):
		return graph.add_edge(frm, to, cost)

	def encode(self, trans_path, debug=False):
		start = 1
		final = [2, 49, 50]
		path = [start]
		dict = {"Ma_1": 4, "Mb_1": 5, "Mc_1": 6,
				"Ma_2": 16, "Mb_2": 17, "Mc_2": 18,
				"Ma_3": 28, "Mb_3": 29, "Mc_3": 30, "end_your_life": final}
		for trans in trans_path:
			encoded = dict[str(trans.machine)]
			if debug:
				print(encoded)
			path.append(encoded)
		path.append(dict["end_your_life"][0])
		# print(path)
		return path

	def compute_path(self, graph, trans_path, search=dijkstra_conveyors, debug=False):
		path_encoded = self.encode(trans_path)
		final_path = []
		final_duration = 0
		path_iter = iter(path_encoded)
		next(path_iter)
		for i in range(len(path_encoded) - 1):
			frm = path_encoded[i]
			to = next(path_iter)

			duration, path = search(graph, frm, to)
			final_path.extend(path[1:])
			final_duration = final_duration + duration

			if debug:
				pass
		# print(f"\r\nConveyor pathing: {frm} -> {to}")
		# print("Shortest path {}, ETA = {} s".format([conveyor.id for conveyor in path], duration))

		if debug:
			print("Shortest FINAL path {}, ETA = {} s".format([conveyor.id for conveyor in final_path], final_duration))
		return [conveyor.id for conveyor in final_path]

	def compute_conveyor(self, graph, frm: str, to: str, search=dijkstra_conveyors, debug=False):
		duration, path = search(graph, frm, to)
		if debug:
			print(f"\r\nComputing conveyor path: {frm} -> {to}")
			print("Shortest path {}, ETA = {} s".format([conveyor.id for conveyor in path], duration))

			return duration, path


	def order_handler(self, order):
		self.tracker.add_order(order)
		low_lim = self.state.pieces_optimized
		if isinstance(order, TransformOrder):
			high_lim = self.state.pieces_optimized + order.quantity - (order.processed + order.on_factory)
			if order.before_type == 4 and order.after_type == 7 and not self.is_reversed:
				if (order.processed + order.on_factory) < order.quantity:
					self.reset()
					self.reverse()

			for piece_number in range(low_lim, high_lim):
				self.state.pieces[piece_number] = \
					(Piece(piece_number, order.before_type, path=None, machines=None, tools=None, order=order))
				self.state.num_pieces += 1
		elif isinstance(order, UnloadOrder):
			high_lim = self.state.pieces_optimized + order.quantity - (order.unloaded + order.on_factory)
			dest_path = {1: [3, 8, 15, 20, 27, 32, 39, 41, 42, 48], 2: [3, 8, 15, 20, 27, 32, 39, 41, 42, 43, 49],
						 3: [3, 8, 15, 20, 27, 32, 39, 41, 42, 43, 44, 50]}
			for piece_number in range(low_lim, high_lim):
				self.state.pieces[piece_number] = \
					(Piece(piece_number, order.piece_type, path=dest_path[order.destination], machines=None, tools=None,
						   order=order))

				if order.destination ==1:
					self.pusher.dispatch_queue_1.append(self.state.pieces[piece_number])
				elif order.destination == 2:
					self.pusher.dispatch_queue_2.append(self.state.pieces[piece_number])
				elif order.destination == 3:
					self.pusher.dispatch_queue_3.append(self.state.pieces[piece_number])


class HorOptimizer(Optimizer):
	'''
	Simple optimizer for multiple isolated cells .
	Greedy approach - only cares about the faster way
		for next piece.
	Priority: First come fist served (Reserves machine if needed)
	Time Complexity: O(n)
	'''

	def compute_transform(self, piece_id, frm: int, to: int, search=dijkstra, debug=False, state=None):
		# TODO Add check for non valid transforms
		if state is None:
			state = self.state
		recipes = self.recipes[f'{frm}->{to}']
		curr_best = 99999
		best_seq = []
		curr_best_idx = 0
		for idx, recipe in enumerate(recipes):
			total_wait_time = 0
			for step, trans in enumerate(recipe):
				curr_m = trans.machine.id
				curr_t = trans.tool
				if step == 0:
					if curr_t != state.machines[curr_m].curr_tool:
						total_wait_time += TOOL_SWAP_DURATION + state.machines[trans.machine.id].waiting_time
						total_wait_time += trans.duration
					else:
						total_wait_time += trans.duration + state.machines[trans.machine.id].waiting_time
				else:
					if curr_m != prev_m:
						if curr_t != state.machines[curr_m].curr_tool:
							total_wait_time += max(0, TOOL_SWAP_DURATION + state.machines[
								curr_m].waiting_time - total_wait_time)
							total_wait_time += trans.duration
						else:
							total_wait_time += max(0, state.machines[curr_m].waiting_time - total_wait_time)
							total_wait_time += trans.duration
					else:
						if curr_t != prev_t:
							total_wait_time += TOOL_SWAP_DURATION
							total_wait_time += trans.duration
						else:
							total_wait_time += trans.duration

				prev_m = curr_m
				prev_t = curr_t
			# print(trans, total_wait_time)

			if total_wait_time <= curr_best:
				curr_best = total_wait_time
				curr_best_idx = idx
				best_seq = recipes[curr_best_idx]

		total_wait_time = 0
		for step, trans in enumerate(best_seq, 1):
			curr_m = trans.machine.id
			curr_t = trans.tool
			if step == 1:
				if curr_t != state.machines[curr_m].curr_tool:
					state.machines[curr_m].waiting_time += TOOL_SWAP_DURATION
					state.machines[curr_m].waiting_time += trans.duration
					total_wait_time = state.machines[curr_m].waiting_time
				else:
					state.machines[curr_m].waiting_time += trans.duration
					total_wait_time = state.machines[curr_m].waiting_time
			else:
				if curr_m != prev_m:
					# Backprop
					state.machines[curr_m].waiting_time = max(total_wait_time, state.machines[curr_m].waiting_time)
					state.machines[prev_m].waiting_time = state.machines[curr_m].waiting_time
					if curr_t != prev_t:
						state.machines[curr_m].waiting_time += trans.duration + TOOL_SWAP_DURATION
						total_wait_time = state.machines[curr_m].waiting_time
					else:
						state.machines[curr_m].waiting_time += trans.duration
						total_wait_time = state.machines[curr_m].waiting_time
				else:
					if curr_t != prev_t:
						state.machines[curr_m].waiting_time += TOOL_SWAP_DURATION
						state.machines[curr_m].waiting_time += trans.duration
						total_wait_time = state.machines[curr_m].waiting_time
					else:
						state.machines[curr_m].waiting_time += trans.duration
						total_wait_time = state.machines[curr_m].waiting_time

			prev_m = curr_m
			prev_t = curr_t

			total_machine_wait = state.machines[trans.machine.id].waiting_time
			state.machines[curr_m].add_op(Operation(piece_id, trans, step, total_machine_wait))
			state.machines[curr_m].curr_tool = curr_t
		return best_seq

	def simulate(self, order):
		simulated_state = copy.deepcopy(self.state)
		for piece_id in range(order.quantity):
			self.compute_transform(piece_id, order.before_type, order.after_type, debug=False, state=simulated_state)
		cost = simulated_state.get_value()
		return simulated_state, cost

	def optimize_single_order(self, order):
		low_lim = self.state.pieces_optimized
		if order.order_type == 'Transform':
			high_lim = low_lim + order.quantity - (order.on_factory + order.processed)
			for piece_id in range(low_lim, high_lim):
				trans_path = self.compute_transform(piece_id, order.before_type, order.after_type, debug=False)
				self.state.pieces[piece_id].machines = [trans.machine.id for trans in trans_path]
				self.state.pieces[piece_id].tools = [trans.tool for trans in trans_path]
				self.state.pieces[piece_id].path = self.compute_path(self.path_graph, trans_path)
				self.state.pieces_optimized += 1

		elif order.order_type == 'Unload':
			high_lim = low_lim + order.quantity - (order.on_factory + order.unloaded)
			for piece_id in range(order.unloaded + self.state.pieces_optimized, order.quantity + self.state.pieces_optimized):
				self.state.pieces_optimized += 1

		print('Optimized:')
		#self.print_machine_schedule()
		#self.print_pusher_queues()
		return self.state

	def reset(self, cond_pusher1 = cond_pusher_1, cond_pusher2=cond_pusher_2, cond_pusher3=cond_pusher_3):
		lock.acquire()
		optimization_lock.acquire()
		self.tracker.check_cell3_clearance()
		self.tracker.check_mb3_clearance()
		self.orders2do = copy.copy(self.active_orders)
		self.active_orders.clear()

		for m in self.state.machines.values():
			new_oplist = [op for op in m.op_list if op.piece_id in self.tracker.pieces_on_transit]
			removed_ops = [op for op in m.op_list if op.piece_id not in self.tracker.pieces_on_transit]
			m.op_list = collections.deque(new_oplist)

			print(new_oplist)
			if not new_oplist:
				print(f'VAZIo')
				#m.make_available()
				m.waiting_time = 0
			else:
				m.waiting_time = m.op_list[-1].eta


			#print('New:')
			#print([str(op) for op in new_oplist])
			#print('REMOVED:')
			#print([str(op) for op in removed_ops])
			#print(f'Waiting time: {m.waiting_time}')



		self.pusher.dispatch_queue_1.clear()
		self.pusher.dispatch_queue_2.clear()
		self.pusher.dispatch_queue_3.clear()
		cond_pusher1.set()
		cond_pusher2.set()
		cond_pusher3.set()

		self.dispatch_queue.clear()
		#self.print_machine_schedule()
		self.print_pusher_queues()
		lock.release()
		optimization_lock.release()

	def reverse(self):
		self.path_graph = self.reverse_graph
		self.recipes = self.reverse_recipes
		self.is_reversed = True
		flag.set()

	def direct(self):
		self.path_graph = self.direct_graph
		self.recipes = self.direct_recipes
		self.is_reversed = False
		reverse_flag.set()


