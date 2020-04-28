from Optimizer.graph import Graph, Vertex

class Conveyor(Vertex):
    '''
    Graph node - edge consists of a transform
	'''

    def __init__(self, node):
		
		#encoding = dict(zip(char, vec_))
		
        self.id = node
        self.adjacent = {}

    def __str__(self):
        return str(self.id) + ' adjacent: ' + str([x.id for x in self.adjacent])

    def add_neighbor(self, neighbor, weight=0):
        self.adjacent[neighbor] = weight

    def get_connections(self):
        return self.adjacent.keys()

    def get_id(self):
		
		#decoding = dict(zip(vec_, char))
		
		#decoded= decoding[self.id]
		
        return self.id #decoded

    def get_weight(self, neighbor):
        return self.adjacent[neighbor]


class PathGraph(Graph):
    '''
    Graph class to be used with Conveyor()
    specific for pathfinding
    uses transport duration as edge weight
    '''
    def add_vertex(self, node):
        self.num_vertices = self.num_vertices + 1
        new_vertex = Conveyor(node)
        self.vert_dict[node] = new_vertex
        return new_vertex
 
    def add_edge(self, frm, to, cost = 0):
        if frm not in self.vert_dict:
            self.add_vertex(frm)
        if to not in self.vert_dict:
            self.add_vertex(to)

        self.vert_dict[frm].add_neighbor(self.vert_dict[to], cost)

    def update_edge_weight(self, frm, to, new_duration):
        if frm not in self.vert_dict:
            raise NameError('From node does not exist!')
        if to not in self.vert_dict:
            raise NameError('Destination node does not exist!')
        if self.get_vertex(to) not in self.vert_dict[frm].adjacent:
            raise NameError('The requested nodes are not connected!')

        self.vert_dict[frm].update_weight(self.get_vertex(to), new_duration)
