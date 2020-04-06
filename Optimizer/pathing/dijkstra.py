import graph
from heapq import heapify, heappop, heappush

def dijkstra_conveyors(graph, start, dest):
	if graph.num_vertices == 0:
		raise ValueError('The graph is empty')
	if start not in graph.vert_dict:
		raise NameError('From node does not exist!')
	if dest not in graph.vert_dict:
		raise NameError('Destination node does not exist!')

	visited_distance = {start : 0}
	queue = [(visited_distance[start], start, [graph.get_vertex(start)])]
	heapify(queue)

	while queue:
		#print(heappop(queue))
		dist, node_id, path = heappop(queue)
		if node_id == dest:
			return  (dist, path)
		node = graph.get_vertex(node_id)
		for neighbour in node.get_connections():
			neighbour_id, neighbour_dist = (neighbour.id, node.get_weight(neighbour))
			if neighbour_id not in visited_distance or (dist + neighbour_dist) < visited_distance[neighbour_id]:
				visited_distance[neighbour_id] = dist + neighbour_dist
				heappush(queue, (visited_distance[neighbour_id], neighbour_id, path + [neighbour]))
