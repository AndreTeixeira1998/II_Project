from Optimizer.graph import Graph, Vertex
import collections

class Operation:
	def __init__(self, piece_id, transform, step: int, eta):
		self.piece_id = piece_id
		self.step = step
		self.transform = transform
		self.eta = eta

	def __str__(self):
		return f"P:{self.piece_id} S:{self.step} M:{self.transform.machine.id} T:{self.transform.tool} ETA:{self.eta}"

	def update_next_tool(self):
		self.transform.machine.next_tool = self.transform.machine.op_list[0].transform.tool


class Machine:
	'''
	Machine to be associated with one or more transform
	Waiting time represents the time neeeded to complete all
	scheduled transformations (not implemented yet)
	'''

	def __init__(self, id, tool='T1', is_free=False):
		self.id = id
		self.op_list = collections.deque([])
		self.curr_tool = tool
		self.next_tool = None
		self.waiting_time = 0
		self.is_free = is_free

	def __str__(self):
		return self.id

	def update_wait_time(self, increase):
		self.waiting_time += increase

	def make_available(self):
		self.is_free = True

	def make_unavailable(self):
		self.is_free = False

	def add_op(self, op):
		self.op_list.append(op)

	def remove_op(self):
		removed_op = self.op_list.popleft()
		if self.op_list:
			for op in self.op_list:
				#print(f'ANTES: {op}')
				op.eta -= removed_op.eta
				#print(f'Depois: {op}')
			self.waiting_time -= removed_op.eta
		else:
			self.waiting_time = 0


class Transform:
	def __init__(self, machine: Machine, tool, duration):
		self.tool = tool
		self.machine = machine
		self.duration = duration

	def __str__(self):
		return f'{self.tool} on {self.machine} for {self.duration}s'


class TransfVertex(Vertex):
	'''
	Graph node - edge consists of a transform
	#TODO implement edge class instead
	'''

	def add_neighbor(self, neighbor, transform: Transform):
		self.adjacent[neighbor] = transform

	def get_weight(self, neighbor):
		return self.adjacent[neighbor].duration

	def get_waiting_time(self, neighbor):
		return self.adjacent[neighbor].machine.waiting_time

	def update_weight(self, neighbor, new_duration):
		self.adjacent[neighbor].duration = new_duration

	def get_transform(self, neighbor):
		return self.adjacent[neighbor]


class TransfGraph(Graph):
	'''
	Graph class to be used with TransfVertex()
	specific for transformation pathfinding
	uses trasnformation duration as edge weight
	'''

	def add_vertex(self, node):
		self.num_vertices = self.num_vertices + 1
		new_vertex = TransfVertex(node)
		self.vert_dict[node] = new_vertex
		return new_vertex

	def add_edge(self, frm, to, transform: Transform):
		if frm not in self.vert_dict:
			self.add_vertex(frm)
		if to not in self.vert_dict:
			self.add_vertex(to)

		self.vert_dict[frm].add_neighbor(self.vert_dict[to], transform)

	def update_edge_weight(self, frm, to, new_duration):
		if frm not in self.vert_dict:
			raise NameError('From node does not exist!')
		if to not in self.vert_dict:
			raise NameError('Destination node does not exist!')
		if self.get_vertex(to) not in self.vert_dict[frm].adjacent:
			raise NameError('The requested nodes are not connected!')

		self.vert_dict[frm].update_weight(self.get_vertex(to), new_duration)
