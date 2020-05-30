##############################################################################
###  The folowing code is based on:                                      #####
###  https://www.bogotobogo.com/python/python_graph_data_structures.php  #####
##############################################################################

class Vertex:
    '''
    Generic node for directed graph
    '''
    def __init__(self, node):
        self.id = node
        self.adjacent = {}

    def __str__(self):
        return str(self.id) + ' adjacent: ' + str([x.id for x in self.adjacent])

    def add_neighbor(self, neighbor, weight=0):
        self.adjacent[neighbor] = weight

    def get_connections(self):
        return self.adjacent.keys()

    def get_id(self):
        return self.id

    def get_weight(self, neighbor):
        return self.adjacent[neighbor]

class Graph:
    '''
    Generic Directed graph class
    '''
    def __init__(self):
        self.vert_dict = {}
        self.num_vertices = 0

    def __iter__(self):
        return iter(self.vert_dict.values())

    def add_vertex(self, node):
        self.num_vertices = self.num_vertices + 1
        new_vertex = Vertex(node)
        self.vert_dict[node] = new_vertex
        return new_vertex

    def get_vertex(self, n):
        if n in self.vert_dict:
            return self.vert_dict[n]
        else:
            return None

    def add_edge(self, frm, to, cost = 0):
        if frm not in self.vert_dict:
            self.add_vertex(frm)
        if to not in self.vert_dict:
            self.add_vertex(to)

        self.vert_dict[frm].add_neighbor(self.vert_dict[to], cost)

    def get_vertices(self):
        return self.vert_dict.keys()

    def print_graph(self):
        return [print (f'{v}') for v in self]

    def print_edges(self):
        for v in self:
            for w in v.get_connections():
                print(f'{v.get_id()} -> {w.get_id()} (weight: {v.get_weight(w)})')


if __name__ == '__main__':

	g = Graph()
	
	for i in range(50):
		g.add_vertex(i+1)

	g.add_edge( 1,  3, 1)
	
	g.add_edge( 3,  1, 1)
	g.add_edge( 3,  8, 1)
	
	g.add_edge( 8,  3, 1)
	g.add_edge( 8,  9, 1)
	g.add_edge( 8, 15, 1)
	
	g.add_edge( 9,  8, 1)
	g.add_edge( 9, 10, 1)
	
	g.add_edge(10,  9, 1)
	g.add_edge(10, 11, 1)
	g.add_edge(10,  4, 1)
	g.add_edge(10, 16, 1)
	
	g.add_edge( 4, 10, 1)
	
	g.add_edge(11, 10, 1)
	g.add_edge(11, 12, 1)
	g.add_edge(11, 17, 1)
	g.add_edge(11,  5, 1)
	
	g.add_edge( 5, 11, 1)
	
	g.add_edge(12, 11, 1)
	g.add_edge(12, 13, 1)
	g.add_edge(12,  6, 1)
	g.add_edge(12, 18, 1)
	
	g.add_edge(13, 12, 1)
	g.add_edge(13, 14, 1)
	
	g.add_edge( 6, 12, 1)
	
	g.add_edge(14, 13, 1)
	g.add_edge(14,  7, 1)
	g.add_edge(14, 19, 1)
	
	g.add_edge( 7, 14, 1)
	g.add_edge( 7,  2, 1)
	
	g.add_edge( 2,  7, 1)
	
	g.add_edge(15, 20, 1)
	g.add_edge(15,  8, 1)
	
	g.add_edge(16, 22, 1)
	g.add_edge(16, 10, 1)
	
	g.add_edge(17, 11, 1)
	g.add_edge(17, 23, 1)
	
	g.add_edge(18, 12, 1)
	g.add_edge(18, 24, 1)
	
	g.add_edge(19, 14, 1)
	g.add_edge(19, 26, 1)
	
	g.add_edge(20, 15, 1)
	g.add_edge(20, 27, 1)
	g.add_edge(20, 21, 1)
	
	g.add_edge(21, 20, 1)
	g.add_edge(21, 22, 1)
	
	g.add_edge(22, 21, 1)
	g.add_edge(22, 23, 1)
	g.add_edge(22, 16, 1)
	g.add_edge(22, 28, 1)
	
	g.add_edge(23, 17, 1)
	g.add_edge(23, 29, 1)
	
	g.add_edge(24, 18, 1)
	g.add_edge(24, 30, 1)
	
	g.add_edge(25, 24, 1)
	g.add_edge(25, 26, 1)
	
	g.add_edge(26, 19, 1)
	g.add_edge(26, 31, 1)
	
	g.add_edge(27, 20, 1)
	g.add_edge(27, 32, 1)
	
	g.add_edge(28, 22, 1)
	g.add_edge(28, 34, 1)
	
	g.add_edge(29, 23, 1)
	g.add_edge(29, 35, 1)
	
	g.add_edge(30, 24, 1)
	g.add_edge(30, 36, 1)
	
	g.add_edge(31, 26, 1)
	g.add_edge(31, 38, 1)
	
	g.add_edge(32, 27, 1)
	g.add_edge(32, 39, 1)
	g.add_edge(32, 33, 1)
	
	g.add_edge(33, 32, 1)
	g.add_edge(33, 34, 1)
	
	g.add_edge(34, 33, 1)
	g.add_edge(34, 28, 1)
	g.add_edge(34, 35, 1)
	
	g.add_edge(35, 29, 1)
	g.add_edge(35, 34, 1)
	g.add_edge(35, 36, 1)
	
	g.add_edge(36, 35, 1)
	g.add_edge(36, 37, 1)
	g.add_edge(36, 30, 1)
	
	g.add_edge(37, 36, 1)
	g.add_edge(37, 38, 1)

	g.add_edge(38, 37, 1)
	g.add_edge(38, 31, 1)
	g.add_edge(38, 46, 1)
	
	g.add_edge(39, 40, 1)
	g.add_edge(39, 32, 1)
	g.add_edge(39, 41, 1)
	
	g.add_edge(40, 39, 1)
	
	g.add_edge(41, 39, 1)
	g.add_edge(41, 42, 1)
	
	g.add_edge(42, 41, 1)
	g.add_edge(42, 43, 1)
	g.add_edge(42, 48, 1)
	
	g.add_edge(43, 42, 1)
	g.add_edge(43, 44, 1)
	g.add_edge(43, 49, 1)
	
	g.add_edge(44, 43, 1)
	g.add_edge(44, 45, 1)
	g.add_edge(44, 50, 1)
	
	g.add_edge(45, 44, 1)
	g.add_edge(45, 46, 1)
	
	g.add_edge(46, 38, 1)
	g.add_edge(46, 47, 1)
	
	g.add_edge(47, 46, 1)
	
	
#    g.add_edge('a', 'c', 9)
#    g.add_edge('a', 'f', 14)
#    g.add_edge('b', 'c', 10)
#    g.add_edge('b', 'd', 15)
#    g.add_edge('c', 'd', 11)
#    g.add_edge('c', 'f', 2)
#    g.add_edge('d', 'e', 6)
#    g.add_edge('e', 'f', 9)

	#g.print_edges()
	#g.print_graph()