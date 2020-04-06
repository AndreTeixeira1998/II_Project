import time
import pickle
from transfgraph import TransfGraph, Transform, Machine
from search import dijkstra
from pathing.pathgraph import Conveyor, PathGraph
from pathing.dijkstra import dijkstra_conveyors


class BabyOptimizer:
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
		self.machines = {}
		self.path_graph = PathGraph()

	def update_state(self, node, val):
		self.factory_state[node] = val

	def print_state(self):
		print('==================== Current Factory State ===============================')
		[print(f"{key}: {value}") for key, value in self.factory_state.items()]
		print('==========================================================================\r\n')

	def add_piece_type(self, type):
		return self.transf_graph.add_vertex(type)

	def add_transform(self, frm, to, transform : Transform):
		return self.transf_graph.add_edge(frm, to, transform)

	def add_machine(self, name):
		if name not in self.machines.keys():
			self.machines[name] = Machine(name)
		else:
			raise NameError(f"Machine {name} already exists")
			
	def add_conveyor(self, id_):
		return self.path_graph.add_vertex(id_)
			
	def add_conveyor_path(self, frm, to, cost):
		return self.path_graph.add_edge(frm, to, cost)

	def compute_transform(self, frm : str, to : str, search=dijkstra, debug=False):
		#TODO Add check for non valid transforms
		duration, path, trans_path = search(self.transf_graph, frm, to)
		if debug:
			print(f"\r\nComputing transform path: {frm} -> {to}")
			print("Shortest path {}, ETA = {} s".format([piece.id for piece in path], duration))
			print("Sequence of Operations: {}".format([str(transform) for transform in trans_path]))
		return duration, path, trans_path

	def encode(self, trans_path, debug=False):
		start=1
		final=[2, 49, 50]
		path=[start]
		dict= {"Ma": [4,16,28], "Mb": [5,17,30], "Mc":[6,18,30], "end_your_life": final}
		
		for trans in trans_path:
			encoded= dict[str(trans.machine)][0]
			
			if debug:
				print (encoded)
			path.append(encoded)
		
		path.append(dict["end_your_life"][0])
		print(path)
		return path
		


	def compute_path(self, trans_path, search=dijkstra_conveyors, debug=False):
		
		path_encoded= self.encode(trans_path)
		final_path=[]
		final_duration=0
		path_iter= iter(path_encoded)
		next(path_iter)
		for i in range(len(path_encoded)-1):
			
			frm = path_encoded[i]
			to = next(path_iter)

			duration, path = search(self.path_graph, frm, to)
			final_path.extend(path[1:])
			final_duration=final_duration+duration
			
			if debug:
				print(f"\r\nConveyor pathing: {frm} -> {to}")
				print("Shortest path {}, ETA = {} s".format([conveyor.id for conveyor in path], duration))
		
	
		if debug:
			print("\n\nShortest FINAL path {}, ETA = {} s".format([piece.id for piece in final_path], final_duration))
	
			
	def compute_conveyor(self, frm : str, to : str, search=dijkstra_conveyors, debug=False):
	
		duration, path = search(self.path_graph, frm, to)
		if debug:
			print(f"\r\nComputing conveyor path: {frm} -> {to}")
			print("Shortest path {}, ETA = {} s".format([conveyor.id for conveyor in path], duration))
		
		return duration, path



if __name__ == '__main__':

	#Load optimizer configs from a pickle
	with open("./config/babyFactory.pickle","rb") as config_pickle:
		optimizer = pickle.load(config_pickle)


	start = time.time()

	duration, piece, trans_path = optimizer.compute_transform("P2", "P5", debug=True)
	
	#optimizer.encode(trans_path)
	
	#for trans in trans_path:
	#	print(trans.machine)
	
	optimizer.compute_path(trans_path, debug=True)
	

	#optimizer.compute_conveyor(4, 16, debug=True)  #testing
	

	end = time.time()
	elapsed_time = end-start


	print(f'\r\nOptimization completed in {elapsed_time*1000} ms')