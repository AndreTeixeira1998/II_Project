import time
import pickle
import copy
import collections
import signal
from contextlib import contextmanager
from Optimizer.transfgraph import TransfGraph, Transform, Machine, Operation
from Optimizer.search import dijkstra, bfs
from Optimizer.pathing.pathgraph import Conveyor, PathGraph
from Optimizer.pathing.dijkstra import dijkstra_conveyors
from OPC_UA.subhandles import OptimizerSubHandler
from Receive_client_orders.Order import Transform as TransformOrder
from Optimizer.config import setup

TOOL_SWAP_DURATION = 20
OPTIMIZATION_TIMEOUT = 60

class Piece():
	'''
	Há de fazer grandes coisas esta classe
	<Rui>: Mudei a classe para ser mais similar à do PLC
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
	def __init__(self, machines = {}, pieces = {}):
		self.machines = machines
		self.pieces = pieces
		self.num_pieces = 0
		self.pieces_optimized = 0

	def __str__(self):
		return f'{self.pieces_optimized}/{self.num_pieces}: {[(m.id, m.curr_tool, m.waiting_time) for m in self.machines.values()]}'

	def __eq__(self, other):
		return self.__str__() == other.__str__()

	def __lt__(self, other):
		return	self.get_value() < self.get_value()

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
		self.factory_state = {}
		self.transf_graph = TransfGraph()
		self.path_graph = PathGraph()
		self.statelistener = OptimizerSubHandler(self)
		self.state = State()
		self.transposition_table = {}
		setup.optimizer_init(self)

	def update_state(self, node, val):
		self.factory_state[node] = val

	def print_state(self):
		print('==================== Current Factory State ===============================')
		[print(f"{key}: {value}") for key, value in self.factory_state.items()]
		print('==========================================================================\r\n')

	def add_piece_type(self, type):
		return self.transf_graph.add_vertex(type)

	def add_transform(self, frm, to, transform: Transform):
		return self.transf_graph.add_edge(frm, to, transform)

	def add_machine(self, name):
		if name not in self.state.machines.keys():
			self.state.machines[name] = Machine(name)
		else:
			raise NameError(f"Machine {name} already exists")

	def print_machine_schedule(self):
		for machine in self.state.machines.values():
			print(f"{machine.id}: {[str(op) for op in machine.op_list]}")

	def add_conveyor(self, id_):
		return self.path_graph.add_vertex(id_)

	def add_conveyor_path(self, frm, to, cost):
		return self.path_graph.add_edge(frm, to, cost)

	def encode(self, trans_path, debug=False):
		start = 1
		final = [2, 49, 50]
		path = [start]
		dict = {"Ma": [4, 16, 28], "Mb": [5, 17, 30], "Mc": [6, 18, 30], "end_your_life": final}
		for trans in trans_path:
			encoded = dict[str(trans.machine)][0]
			if debug:
				print(encoded)
			path.append(encoded)
		path.append(dict["end_your_life"][0])
		# print(path)
		return path

	def compute_path(self, trans_path, search=dijkstra_conveyors, debug=False):
		path_encoded = self.encode(trans_path)
		final_path = []
		final_duration = 0
		path_iter = iter(path_encoded)
		next(path_iter)
		for i in range(len(path_encoded) - 1):
			frm = path_encoded[i]
			to = next(path_iter)

			duration, path = search(self.path_graph, frm, to)
			final_path.extend(path[1:])
			final_duration = final_duration + duration

			if debug:
				pass
		# print(f"\r\nConveyor pathing: {frm} -> {to}")
		# print("Shortest path {}, ETA = {} s".format([conveyor.id for conveyor in path], duration))

		if debug:
			print("Shortest FINAL path {}, ETA = {} s".format([conveyor.id for conveyor in final_path], final_duration))
		return [conveyor.id for conveyor in final_path]

	def compute_conveyor(self, frm: str, to: str, search=dijkstra_conveyors, debug=False):
		duration, path = search(self.path_graph, frm, to)
		if debug:
			print(f"\r\nComputing conveyor path: {frm} -> {to}")
			print("Shortest path {}, ETA = {} s".format([conveyor.id for conveyor in path], duration))

		return duration, path

	def order_handler(self, order: TransformOrder):
		for piece_number in range(self.state.num_pieces, self.state.num_pieces + order.quantity):
			self.state.pieces[piece_number] = \
				(Piece(piece_number, order.before_type, path=None, machines=None, tools=None, order=order))
			self.state.num_pieces += 1

class BabyOptimizer(Optimizer):
	'''
	Simple optimizer for a single cell.
	Greedy approach - only cares about the faster way
		for next piece.
	Priority: First come fist served (Reserves machine if needed)
	Time Complexity: O(n)
	'''

	def compute_transform(self, piece_id, frm : str, to : str, search=dijkstra, debug=False, state = None):
		#TODO Add check for non valid transforms
		if state is None:
			state = self.state
		duration, path, trans_path = search(self.transf_graph, frm, to)
		if debug:
			print(f"\r\nComputing transform path for piece {piece_id}: {frm} -> {to}")
			print("Shortest path {}, ETA = {} s".format([piece.id for piece in path], duration))
			print("Sequence of transforms: {}".format([str(transform) for transform in trans_path]))

		total_machine_wait = 0
		for step, trans in enumerate(trans_path, 1):
			# Account for Tool Swapping
			if state.machines[trans.machine.id].curr_tool == trans.tool:
				tool_swap = 0
			else:
				tool_swap = TOOL_SWAP_DURATION
			# Reserves Machine until current transform is complete
			if state.machines[trans.machine.id].waiting_time > total_machine_wait:
				state.machines[trans.machine.id].update_wait_time(trans.duration + tool_swap)
			else:
				lock_duration = total_machine_wait-state.machines[trans.machine.id].waiting_time
				state.machines[trans.machine.id].update_wait_time(lock_duration + trans.duration + tool_swap)
			# Update Machines
			total_machine_wait = state.machines[trans.machine.id].waiting_time
			state.machines[trans.machine.id].add_op(Operation(piece_id, trans, step, total_machine_wait))
			state.machines[trans.machine.id].curr_tool = trans.tool

			if debug:
				print(f"Added {trans.duration}s wait  on {trans.machine}")

		return duration, path, trans_path


	def optimize_all_pieces(self):
		for piece_id in range(self.state.pieces_optimized, self.state.num_pieces):
			#Todo: Change Piece types to int
			before_type = self.state.pieces[piece_id].order.before_type
			after_type = self.state.pieces[piece_id].order.after_type
			_, _,  trans_path = self.compute_transform(piece_id, f"P{before_type}", f"P{after_type}", debug=False)
			self.state.pieces[piece_id].machines = [trans.machine.id for trans in trans_path]
			self.state.pieces[piece_id].tools = [trans.tool for trans in trans_path]
			self.state.pieces[piece_id].path = self.compute_path(trans_path)
			self.state.pieces_optimized += 1
		return self.state

class DaddyOptimizer(Optimizer):
	'''
	Single cell
	Brute-Force Depth-First-Search based
	Takes into account subsequent pieces
	Priority: First come fist served (Reserves machine if needed)
	Time Complexity: O(b^n) (b: branching factor, n: number of pieces)
	'''
	def compute_all_transforms(self, piece_id, frm: str, to : str, state: State, search=bfs, debug=False):
		sequences = search(self.transf_graph, frm, to)
		new_states = []
		for durations, paths, trans_path in sequences:
			new_state = copy.deepcopy(state)
			total_machine_wait = 0
			for step, trans in enumerate(trans_path, 1):
				# Account for Tool Swapping
				if new_state.machines[trans.machine.id].curr_tool == trans.tool:
					tool_swap = 0
				else:
					tool_swap = TOOL_SWAP_DURATION
				# Reserves Machine until previous operation is complete
				if new_state.machines[trans.machine.id].waiting_time > total_machine_wait:
					new_state.machines[trans.machine.id].update_wait_time(trans.duration + tool_swap)
				else:
					lock_duration = total_machine_wait - new_state.machines[trans.machine.id].waiting_time
					new_state.machines[trans.machine.id].update_wait_time(lock_duration + trans.duration + tool_swap)
				# Update Machines
				total_machine_wait = new_state.machines[trans.machine.id].waiting_time
				new_state.machines[trans.machine.id].add_op(Operation(piece_id, trans, step, total_machine_wait))
				new_state.machines[trans.machine.id].curr_tool = trans.tool
			# Add piece to newly created state
			new_state.pieces[piece_id].machines = [trans.machine.id for trans in trans_path]
			new_state.pieces[piece_id].tools = [trans.tool for trans in trans_path]
			new_state.pieces[piece_id].path = self.compute_path(trans_path)
			new_state.pieces_optimized += 1
			new_states.append(new_state)
		return sorted(new_states)

	def optimize_all_pieces(self, timeout = OPTIMIZATION_TIMEOUT):
		open_states = collections.deque([self.state])
		min_depth = self.state.pieces_optimized
		max_depth = self.state.num_pieces
		curr_best = float("inf")
		best_state = None
		if timeout: start = time.time()
		# Depth-First Search
		while open_states:
			if timeout and (time.time()-start) > timeout:
				print(f"TIMEOUT of {timeout}s exceeded")
				if best_state:
					print(f"Returning best result achieved")
					return best_state
				else:
					raise ValueError("Order timeout is not enough to converge. Please increase it or reduce order size")
			state = open_states.popleft()
			if str(state) in self.transposition_table:
				continue
			else:
				value = state.get_value()
				if value > curr_best:
					continue
				if state.pieces_optimized == max_depth:
					curr_best = min(curr_best, value)
					best_state = copy.deepcopy(state)
				else:
					self.transposition_table[str(state)] = True
					curr_piece = state.pieces[state.pieces_optimized]
					before_type = curr_piece.order.before_type
					after_type = curr_piece.order.after_type
					new_states = collections.deque(self.compute_all_transforms(state.pieces_optimized, f"P{before_type}", f"P{after_type}", debug=False, state=state))
					open_states = new_states + open_states

		return best_state

if __name__ == '__main__':

	optimizer = BabyOptimizer()
	print("Using BabyOptimizer")

	#optimizer = DaddyOptimizer()
	#print("Using DaddyOptimizer\r\n")

	fake_order = []

	fake_order.append(TransformOrder(order_type="Transform", order_number=1,
								max_delay=2000, before_type=2, after_type=6, quantity=30))


	fake_order.append(TransformOrder(order_type="Transform", order_number=2,
								max_delay=2000, before_type=3, after_type=5, quantity=7))

	fake_order.append(TransformOrder(order_type="Transform", order_number=3,
								max_delay=2000, before_type=7, after_type=9, quantity=10))

	fake_order.append(TransformOrder(order_type = "Transform", order_number = 4,
							    max_delay = 2000, before_type = 4, after_type = 8, quantity = 7))

	fake_order.append(TransformOrder(order_type="Transform", order_number=5,
								max_delay=2000, before_type=1, after_type=9, quantity=20))



	for order in fake_order:
		print(f"Order number {order.order_number}. {order.quantity} transforms from P{order.before_type} to P{order.after_type}")
		optimizer.order_handler(order)
		print(f'Total number of pieces: {optimizer.state.num_pieces}\r\n')

	print(f'Optimizing {optimizer.state.num_pieces} pieces')
	start = time.time()
	optimizer.state = optimizer.optimize_all_pieces()

	end = time.time()
	print(f'Optmized {optimizer.state.pieces_optimized}/{optimizer.state.num_pieces} '
					f'pieces in {(end-start)*1000}ms')
	print(f'{optimizer.state}')
	optimizer.print_machine_schedule()



