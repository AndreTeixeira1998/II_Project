import time
import pickle
from Optimizer.transfgraph import TransfGraph, Transform, Machine
from Optimizer.search import dijkstra

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
        self.graph = TransfGraph()
        self.machines = {}

    def update_state(self, node, val):
        self.factory_state[node] = val

    def print_state(self):
        print('==================== Current Factory State ===============================')
        [print(f"{key}: {value}") for key, value in self.factory_state.items()]
        print('==========================================================================\r\n')

    def add_piece_type(self, type):
        return self.graph.add_vertex(type)

    def add_transform(self, frm, to, transform : Transform):
        return self.graph.add_edge(frm, to, transform)

    def add_machine(self, name):
        if name not in self.machines.keys():
            self.machines[name] = Machine(name)
        else:
            raise NameError(f"Machine {name} already exists")

    def compute_transform(self, frm : str, to : str, search=dijkstra, debug=False):
        #TODO Add check for non valid transforms
        duration, path, trans_path = search(self.graph, frm, to)
        if debug:
            print(f"\r\nComputing transform path: {frm} -> {to}")
            print("Shortest path {}, ETA = {} s".format([piece.id for piece in path], duration))
            print("Sequence of Operations: {}".format([str(transform) for transform in trans_path]))


if __name__ == '__main__':

    #Load optimizer configs from a pickle
    with open("config/babyFactory.pickle","rb") as config_pickle:
        optimizer = pickle.load(config_pickle)


    start = time.time()

    optimizer.compute_transform("P1", "P5", debug=True)
    optimizer.compute_transform("P1", "P3", debug=True)
    optimizer.compute_transform("P4", "P8", debug=True)
    optimizer.compute_transform("P2", "P9", debug=True)
    optimizer.compute_transform("P3", "P5", debug=True)
    optimizer.compute_transform("P3", "P9", debug=True)

    end = time.time()
    elapsed_time = end-start


    print(f'\r\nOptimization completed in {elapsed_time*1000} ms')