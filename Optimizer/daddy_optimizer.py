import time
import copy
import collections
from Optimizer.transfgraph import Operation
from Optimizer.search import bfs
from Receive_client_orders.Order import TransformOrder
from Optimizer.baby_optimizer import Piece, State, Optimizer

TOOL_SWAP_DURATION = 20
OPTIMIZATION_TIMEOUT = 60

class DaddyOptimizer(Optimizer):
	'''
	Single cell
	Brute-Force Depth-First-Search based
	Takes into account subsequent pieces
	Priority: First come fist served (Reserves machine if needed)
	Time Complexity: O(b^n) (b: branching factor, n: number of pieces)
	'''

	def compute_all_transforms(self, piece_id, frm: str, to: str, state: State, search=bfs, debug=False):
		sequences = search(self.transf_graph[1], frm, to) #Para já so é utilizavel para uma unica celula
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

	def optimize_all_pieces(self, timeout=OPTIMIZATION_TIMEOUT):
		open_states = collections.deque([self.state])
		min_depth = self.state.pieces_optimized
		max_depth = self.state.num_pieces
		curr_best = float("inf")
		best_state = None
		if timeout: start = time.time()
		# Depth-First Search
		while open_states:
			if timeout and (time.time() - start) > timeout:
				#print(f"TIMEOUT of {timeout}s exceeded")
				if best_state:
					#print(f"Returning best result achieved")
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
					new_states = collections.deque(
						self.compute_all_transforms(state.pieces_optimized, f"P{before_type}", f"P{after_type}",
													debug=False, state=state))
					open_states = new_states + open_states

		return best_state


if __name__ == '__main__':

	optimizer = DaddyOptimizer()
	#print("Using DaddyOptimizer\r\n")

	fake_order = []

	fake_order.append(TransformOrder(order_type="Transform", order_number=1,
									 max_delay=2000, before_type=2, after_type=6, quantity=10))
	fake_order.append(TransformOrder(order_type="Transform", order_number=2,
									 max_delay=2000, before_type=4, after_type=5, quantity=10))
	fake_order.append(TransformOrder(order_type="Transform", order_number=3,
									 max_delay=2000, before_type=7, after_type=9, quantity=10))
	#fake_order.append(TransformOrder(order_type="Transform", order_number=4,
	#								 max_delay=2000, before_type=4, after_type=8, quantity=7))
	#fake_order.append(TransformOrder(order_type="Transform", order_number=5,
	#								 max_delay=2000, before_type=1, after_type=9, quantity=20))
	#fake_order.append(TransformOrder(order_type="Transform", order_number=6,
	#								 max_delay=2000, before_type=4, after_type=7, quantity=20))

	for order in fake_order:
		print(
			f"Order number {order.order_number}. {order.quantity} transforms from P{order.before_type} to P{order.after_type}")
		optimizer.order_handler(order)
		print(f'Total number of pieces: {optimizer.state.num_pieces}\r\n')

	print(f'Optimizing {optimizer.state.num_pieces} pieces')
	start = time.time()
	optimizer.state = optimizer.optimize_all_pieces()

	end = time.time()
	print(f'Optmized {optimizer.state.pieces_optimized}/{optimizer.state.num_pieces} '
		  f'pieces in {(end - start) * 1000}ms')
	print(f'{optimizer.state}')
	optimizer.print_machine_schedule()
