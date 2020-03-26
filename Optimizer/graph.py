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

    g.add_vertex('P1')
    g.add_vertex('P2')
    g.add_vertex('P3')
    g.add_vertex('P4')
    g.add_vertex('P5')
    g.add_vertex('P6')
    g.add_vertex('P7')
    g.add_vertex('P8')
    g.add_vertex('P9')

    g.add_edge('P1', 'P2', 7)
    g.add_edge('a', 'c', 9)
    g.add_edge('a', 'f', 14)
    g.add_edge('b', 'c', 10)
    g.add_edge('b', 'd', 15)
    g.add_edge('c', 'd', 11)
    g.add_edge('c', 'f', 2)
    g.add_edge('d', 'e', 6)
    g.add_edge('e', 'f', 9)

    g.print_edges()
    g.print_graph()