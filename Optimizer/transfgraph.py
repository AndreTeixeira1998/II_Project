from Optimizer.graph import Graph, Vertex

class Machine():
    '''
    Machine to be associated with one or more transform
    Waiting time represents the time neeeded to complete all
    scheduled transformations (not implemented yet)
    '''
    def __init__(self, id):
        self.id = id
        self.waiting_time = 0

    def __str__(self):
        return self.id

class Transform():
    def __init__ (self,machine : Machine, tool,  duration):
        self.tool = tool
        self.machine = machine
        self.duration = duration

    def __str__ (self):
        return f'{self.tool} on {self.machine} for {self.duration}s with waiting time {self.machine.waiting_time}s'

class TransfVertex(Vertex):
    '''
    Graph node - edge consists of a transform
    #TODO implement edge class instead
    '''
    def add_neighbor(self, neighbor, transform : Transform):
        self.adjacent[neighbor] = transform

    def get_weight(self, neighbor):
        return self.adjacent[neighbor].duration

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


    def add_edge(self, frm, to, transform : Transform):
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
