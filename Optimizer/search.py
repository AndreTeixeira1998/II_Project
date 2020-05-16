import Optimizer.transfgraph
from heapq import heapify, heappop, heappush
from operator import itemgetter


def dijkstra(graph, start, dest):
	if graph.num_vertices == 0:
		raise ValueError('The graph is empty')
	if start not in graph.vert_dict:
		raise NameError('From node does not exist!')
	if dest not in graph.vert_dict:
		raise NameError('Destination node does not exist!')

	visited_distance = {start: 0}
	queue = [(visited_distance[start], start, [graph.get_vertex(start)], [])]
	heapify(queue)

	while queue:
		dist, node_id, path, trans_path = heappop(queue)
		if node_id == dest:
			return (dist, path, trans_path)
		node = graph.get_vertex(node_id)
		for neighbour in node.get_connections():
			neighbour_id, neighbour_dist = (neighbour.id, node.get_weight(neighbour))
			neighbour_trans, neighbour_wait = (node.get_transform(neighbour), node.get_waiting_time(neighbour))
			if neighbour_id not in visited_distance or (dist + neighbour_dist + max(0, neighbour_wait - dist)) < \
					visited_distance[neighbour_id]:
				visited_distance[neighbour_id] = dist + neighbour_dist + max(0, neighbour_wait - dist)
				heappush(queue, (
				visited_distance[neighbour_id], neighbour_id, path + [neighbour], trans_path + [neighbour_trans]))


def bfs(graph, start, dest):
	if graph.num_vertices == 0:
		raise ValueError('The graph is empty')
	if start not in graph.vert_dict:
		raise NameError('From node does not exist!')
	if dest not in graph.vert_dict:
		raise NameError('Destination node does not exist!')

	visited_distance = {start: 0}
	queue = [(visited_distance[start], start, [graph.get_vertex(start)], [])]
	heapify(queue)

	sequences = []

	while queue:
		dist, node_id, path, trans_path = heappop(queue)
		node = graph.get_vertex(node_id)
		for neighbour in node.get_connections():
			neighbour_id, neighbour_dist = (neighbour.id, node.get_weight(neighbour))
			neighbour_trans, neighbour_wait = (node.get_transform(neighbour), node.get_waiting_time(neighbour))

			if neighbour_id == dest:
				_path = path + [neighbour]
				_dist = dist + neighbour_dist + max(0, neighbour_wait - dist)
				_transforms = trans_path + [neighbour_trans]
				sequences.append((_dist, _path, _transforms))
			if neighbour_id not in visited_distance or (dist + neighbour_dist + max(0, neighbour_wait - dist)) < \
					visited_distance[neighbour_id]:
				visited_distance[neighbour_id] = dist + neighbour_dist + max(0, neighbour_wait - dist)
				heappush(queue, (
				visited_distance[neighbour_id], neighbour_id, path + [neighbour], trans_path + [neighbour_trans]))

	return sequences

def return_all_sequences(graph, start, dest):
	if graph.num_vertices == 0:
		raise ValueError('The graph is empty')
	if start not in graph.vert_dict:
		raise NameError('From node does not exist!')
	if dest not in graph.vert_dict:
		raise NameError('Destination node does not exist!')

	visited_distance = {start: 0}
	queue = [(visited_distance[start], start, [graph.get_vertex(start)], [])]
	heapify(queue)

	sequences = []

	while queue:
		dist, node_id, path, trans_path = heappop(queue)
		node = graph.get_vertex(node_id)
		for neighbour in node.get_connections():
			neighbour_id, neighbour_dist = (neighbour.id, node.get_weight(neighbour))
			neighbour_trans, neighbour_wait = (node.get_transform(neighbour), node.get_waiting_time(neighbour))

			if neighbour_id == dest:
				_path = path + [neighbour]
				_dist = dist + neighbour_dist
				_transforms = trans_path + [neighbour_trans]
				sequences.append(_transforms)

			if neighbour_id not in visited_distance or (dist + neighbour_dist) < visited_distance[neighbour_id]:
				visited_distance[neighbour_id] = dist + neighbour_dist
				heappush(queue, (
					visited_distance[neighbour_id], neighbour_id, path + [neighbour], trans_path + [neighbour_trans]))

	return sequences