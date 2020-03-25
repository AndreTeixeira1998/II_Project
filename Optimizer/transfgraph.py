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



if __name__ == '__main__':
    machine_graph = TransfGraph()

    machine_graph.add_vertex('P1')
    machine_graph.add_vertex('P2')
    machine_graph.add_vertex('P3')
    machine_graph.add_vertex('P4')
    machine_graph.add_vertex('P5')
    machine_graph.add_vertex('P9')
    machine_graph.add_vertex('P6')
    machine_graph.add_vertex('P7')
    machine_graph.add_vertex('P8')

    machine_graph.add_edge('P1', 'P2', Transform('Ma', 'T1', 15))
    machine_graph.add_edge('P1', 'P3', Transform('Mb', 'T2', 20))
    machine_graph.add_edge('P2', 'P3', Transform('Ma', 'T1', 15))
    machine_graph.add_edge('P2', 'P6', Transform('Ma', 'T2', 15))
    machine_graph.add_edge('P3', 'P4', Transform('Mb', 'T1', 15))
    machine_graph.add_edge('P4', 'P5', Transform('Mc', 'T1', 30))
    machine_graph.add_edge('P4', 'P8', Transform('Mc', 'T2', 10))
    machine_graph.add_edge('P7', 'P3', Transform('Mb', 'T2', 20))
    machine_graph.add_edge('P6', 'P9', Transform('Ma', 'T3', 15))
    machine_graph.add_edge('P8', 'P9', Transform('Mc', 'T3', 30))
    machine_graph.add_edge('P7', 'P9', Transform('Mb', 'T3', 20))
    machine_graph.update_edge_weight('P7', 'P9', 50)
    #machine_graph.add_edge('P8', 'P7', Transform('Ma', 'T2', 30))

    machine_graph.print_edges()
    machine_graph.print_graph()