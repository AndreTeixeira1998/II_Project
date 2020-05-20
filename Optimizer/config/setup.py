import pickle
import sys
import copy
sys.path.insert(0, "..")
from Optimizer.transfgraph import TransfGraph, Transform, Machine
from Optimizer.search import return_all_sequences

NUMBER_OF_CELLS = 3

encode = {'Ma_1': 1, 'Mb_1': 2, 'Mc_1':3,
		  'Ma_2': 4, 'Mb_2': 5, 'Mc_2':6,
		  'Ma_3': 7, 'Mb_3': 8, 'Mc_3':9}

decode = {1: 'Ma_1', 2: 'Mb_1', 3: 'Mc_1',
		  4: 'Ma_2', 5: 'Mb_2', 6: 'Mc_2',
		  7: 'Ma_3', 8: 'Mb_3', 9: 'Mc_3'}

# Object instantiation
def optimizer_init(optimizer):
	# Specifying all types of pieces available
	print('Setting up Optimizer...')

	optimizer.block_pieces.set()

	for cell in range(1, NUMBER_OF_CELLS + 1):
		optimizer.add_transform_cell(cell)

		optimizer.add_piece_type('P1', cell)
		optimizer.add_piece_type('P2', cell)
		optimizer.add_piece_type('P3', cell)
		optimizer.add_piece_type('P4', cell)
		optimizer.add_piece_type('P5', cell)
		optimizer.add_piece_type('P6', cell)
		optimizer.add_piece_type('P7', cell)
		optimizer.add_piece_type('P8', cell)
		optimizer.add_piece_type('P9', cell)

		optimizer.add_machine(f'Ma_{cell}')
		optimizer.add_machine(f'Mb_{cell}')
		optimizer.add_machine(f'Mc_{cell}')

		optimizer.add_transform('P1', 'P2', Transform(optimizer.state.machines[f'Ma_{cell}'], 'T1', 15), cell)
		optimizer.add_transform('P2', 'P3', Transform(optimizer.state.machines[f'Ma_{cell}'], 'T1', 15), cell)
		optimizer.add_transform('P2', 'P6', Transform(optimizer.state.machines[f'Ma_{cell}'], 'T2', 15), cell)
		optimizer.add_transform('P6', 'P9', Transform(optimizer.state.machines[f'Ma_{cell}'], 'T3', 15), cell)
		optimizer.add_transform('P1', 'P3', Transform(optimizer.state.machines[f'Mb_{cell}'], 'T1', 20), cell)
		optimizer.add_transform('P3', 'P4', Transform(optimizer.state.machines[f'Mb_{cell}'], 'T1', 15), cell)
		optimizer.add_transform('P3', 'P7', Transform(optimizer.state.machines[f'Mb_{cell}'], 'T2', 20), cell)
		optimizer.add_transform('P7', 'P9', Transform(optimizer.state.machines[f'Mb_{cell}'], 'T3', 20), cell)
		optimizer.add_transform('P1', 'P4', Transform(optimizer.state.machines[f'Mc_{cell}'], 'T1', 10), cell)
		optimizer.add_transform('P4', 'P5', Transform(optimizer.state.machines[f'Mc_{cell}'], 'T1', 30), cell)
		optimizer.add_transform('P4', 'P8', Transform(optimizer.state.machines[f'Mc_{cell}'], 'T2', 10), cell)
		optimizer.add_transform('P8', 'P9', Transform(optimizer.state.machines[f'Mc_{cell}'], 'T3', 10), cell)

	###
	### Mario-kun se alguma veres vir isto
 	### i am sorry
	###

	for p_before in range(1,10):
		for p_after in range(1,10):
			optimizer.recipes[f'{p_before}->{p_after}'] = []

			#Celula 1
			sequences = return_all_sequences(optimizer.transf_graph[1], f'P{p_before}', f'P{p_after}')
			if sequences:
				for seq in sequences:
					if len(seq) == 2:
						new_seq = copy.deepcopy(seq)
						for idx, trans in enumerate(new_seq):
							if idx == 0:
								old_m = trans.machine.id
								old_t = trans.tool
							else:
								new_m = trans.machine.id
								new_t = trans.tool
								if old_t != new_t and old_m == new_m:
									#print(f'{p_before}->{p_after}' + 'paralelizavel')
									m_id = decode[encode[trans.machine.id] + 3]
									trans.machine = optimizer.state.machines[m_id]
									sequences.append(new_seq)
					optimizer.recipes[f'{p_before}->{p_after}'].append(seq)


			# Celula 2
			sequences = return_all_sequences(optimizer.transf_graph[2], f'P{p_before}', f'P{p_after}')
			if sequences:
				for seq in sequences:
					if len(seq) == 2:
						new_seq = copy.deepcopy(seq)
						for idx, trans in enumerate(new_seq):
							if idx == 0:
								old_m = trans.machine.id
								old_t = trans.tool
							else:
								new_m = trans.machine.id
								new_t = trans.tool
								if old_t != new_t and old_m == new_m:
									#print(f'{p_before}->{p_after}' + 'paralelizavel')
									m_id = decode[encode[trans.machine.id] + 3]
									trans.machine = optimizer.state.machines[m_id]
									sequences.append(new_seq)
					optimizer.recipes[f'{p_before}->{p_after}'].append(seq)

			# Celula 3
			sequences = return_all_sequences(optimizer.transf_graph[3], f'P{p_before}', f'P{p_after}')
			if sequences:
				for seq in sequences:
					optimizer.recipes[f'{p_before}->{p_after}'].append(seq)

	print('Automatic recipes loaded.')

	optimizer.recipes['1->9'].append([Transform(optimizer.state.machines[f'Ma_1'], 'T1', 15),
							  			Transform(optimizer.state.machines[f'Ma_2'], 'T2', 15),
							 				Transform(optimizer.state.machines[f'Ma_3'], 'T3', 15)])

	optimizer.recipes['1->9'].append([Transform(optimizer.state.machines[f'Mb_1'], 'T1', 20),
							  			Transform(optimizer.state.machines[f'Mb_2'], 'T2', 20),
							 				Transform(optimizer.state.machines[f'Mb_3'], 'T3', 15)])

	optimizer.recipes['1->9'].append([Transform(optimizer.state.machines[f'Mc_1'], 'T1', 10),
							  			Transform(optimizer.state.machines[f'Mc_2'], 'T2', 10),
							 				Transform(optimizer.state.machines[f'Mc_3'], 'T3', 10)])

	print('Custom recipes loaded')
	#for transf, seq in zip(optimizer.recipes.keys(), optimizer.recipes.values()):
	#	print(f'{transf}: {len(seq)} {seq}')

	# Transformacao extra
	# optimizer.add_transform('P8', 'P7', Transform(optimizer.state-machines[f'Ma_{cell}'], 'T2', 30))


	for i in range(50):
		optimizer.add_conveyor(optimizer.path_graph, i + 1)
		optimizer.add_conveyor(optimizer.reverse_graph, i + 1)

	BLOCKED = 9999999
	PASS = 1
	MACHINE_INPUT = 2
	MACHINE_OUTPUT = 1

	#Normal
	optimizer.add_conveyor_path(optimizer.path_graph,  1, 3, PASS)

	optimizer.add_conveyor_path(optimizer.path_graph, 3, 1, BLOCKED)
	optimizer.add_conveyor_path(optimizer.path_graph, 3, 8, PASS)

	optimizer.add_conveyor_path(optimizer.path_graph, 8, 3, BLOCKED)
	optimizer.add_conveyor_path(optimizer.path_graph, 8, 9, PASS)
	optimizer.add_conveyor_path(optimizer.path_graph, 8, 15, PASS)

	optimizer.add_conveyor_path(optimizer.path_graph, 9, 8, BLOCKED)
	optimizer.add_conveyor_path(optimizer.path_graph, 9, 10, PASS)

	optimizer.add_conveyor_path(optimizer.path_graph, 10, 9, BLOCKED)
	optimizer.add_conveyor_path(optimizer.path_graph, 10, 11, PASS)
	optimizer.add_conveyor_path(optimizer.path_graph, 10, 4, MACHINE_INPUT)
	optimizer.add_conveyor_path(optimizer.path_graph, 10, 16, MACHINE_INPUT)

	optimizer.add_conveyor_path(optimizer.path_graph, 4, 10, MACHINE_OUTPUT)

	optimizer.add_conveyor_path(optimizer.path_graph, 11, 10, BLOCKED)
	optimizer.add_conveyor_path(optimizer.path_graph, 11, 12, PASS)
	optimizer.add_conveyor_path(optimizer.path_graph, 11, 17, MACHINE_INPUT)
	optimizer.add_conveyor_path(optimizer.path_graph, 11, 5, MACHINE_INPUT)

	optimizer.add_conveyor_path(optimizer.path_graph, 5, 11, MACHINE_OUTPUT)

	optimizer.add_conveyor_path(optimizer.path_graph, 12, 11, BLOCKED)
	optimizer.add_conveyor_path(optimizer.path_graph, 12, 13, PASS)
	optimizer.add_conveyor_path(optimizer.path_graph, 12, 6, MACHINE_INPUT)
	optimizer.add_conveyor_path(optimizer.path_graph, 12, 18, MACHINE_INPUT)

	optimizer.add_conveyor_path(optimizer.path_graph, 13, 12, BLOCKED)
	optimizer.add_conveyor_path(optimizer.path_graph, 13, 14, PASS)

	optimizer.add_conveyor_path(optimizer.path_graph, 6, 12, PASS)

	optimizer.add_conveyor_path(optimizer.path_graph, 14, 13, BLOCKED)
	optimizer.add_conveyor_path(optimizer.path_graph, 14, 7, PASS)
	optimizer.add_conveyor_path(optimizer.path_graph, 14, 19, BLOCKED)

	optimizer.add_conveyor_path(optimizer.path_graph, 7, 14, BLOCKED)
	optimizer.add_conveyor_path(optimizer.path_graph, 7, 2, PASS)

	optimizer.add_conveyor_path(optimizer.path_graph, 2, 7, BLOCKED)

	optimizer.add_conveyor_path(optimizer.path_graph, 15, 20, PASS)
	optimizer.add_conveyor_path(optimizer.path_graph, 15, 8, BLOCKED)

	optimizer.add_conveyor_path(optimizer.path_graph, 16, 22, MACHINE_OUTPUT)
	optimizer.add_conveyor_path(optimizer.path_graph, 16, 10, BLOCKED)

	optimizer.add_conveyor_path(optimizer.path_graph, 17, 11, BLOCKED)
	optimizer.add_conveyor_path(optimizer.path_graph, 17, 23, MACHINE_OUTPUT)

	optimizer.add_conveyor_path(optimizer.path_graph, 18, 12, BLOCKED)
	optimizer.add_conveyor_path(optimizer.path_graph, 18, 24, MACHINE_OUTPUT)

	optimizer.add_conveyor_path(optimizer.path_graph, 19, 14, PASS)
	optimizer.add_conveyor_path(optimizer.path_graph, 19, 26, BLOCKED)

	optimizer.add_conveyor_path(optimizer.path_graph, 20, 15, BLOCKED)
	optimizer.add_conveyor_path(optimizer.path_graph, 20, 27, PASS)
	optimizer.add_conveyor_path(optimizer.path_graph, 20, 21, PASS)

	optimizer.add_conveyor_path(optimizer.path_graph, 21, 20, BLOCKED)
	optimizer.add_conveyor_path(optimizer.path_graph, 21, 22, PASS)

	optimizer.add_conveyor_path(optimizer.path_graph, 22, 21, BLOCKED)
	optimizer.add_conveyor_path(optimizer.path_graph, 22, 23, PASS)
	optimizer.add_conveyor_path(optimizer.path_graph, 22, 16, BLOCKED)
	optimizer.add_conveyor_path(optimizer.path_graph, 22, 28, MACHINE_INPUT)

	optimizer.add_conveyor_path(optimizer.path_graph, 23, 17, BLOCKED)
	optimizer.add_conveyor_path(optimizer.path_graph, 23, 29, MACHINE_INPUT)
	optimizer.add_conveyor_path(optimizer.path_graph, 23, 22, BLOCKED)
	optimizer.add_conveyor_path(optimizer.path_graph, 23, 24, PASS)

	optimizer.add_conveyor_path(optimizer.path_graph, 24, 18, BLOCKED)
	optimizer.add_conveyor_path(optimizer.path_graph, 24, 30, PASS)
	optimizer.add_conveyor_path(optimizer.path_graph, 24, 23, BLOCKED)
	optimizer.add_conveyor_path(optimizer.path_graph, 24, 25, PASS)

	optimizer.add_conveyor_path(optimizer.path_graph, 25, 24, BLOCKED)
	optimizer.add_conveyor_path(optimizer.path_graph, 25, 26, PASS)

	optimizer.add_conveyor_path(optimizer.path_graph, 26, 19, PASS)
	optimizer.add_conveyor_path(optimizer.path_graph, 26, 31, BLOCKED)
	optimizer.add_conveyor_path(optimizer.path_graph, 26, 25, BLOCKED)

	optimizer.add_conveyor_path(optimizer.path_graph, 27, 20, BLOCKED)
	optimizer.add_conveyor_path(optimizer.path_graph, 27, 32, PASS)

	optimizer.add_conveyor_path(optimizer.path_graph, 28, 22, BLOCKED)
	optimizer.add_conveyor_path(optimizer.path_graph, 28, 34, MACHINE_OUTPUT)

	optimizer.add_conveyor_path(optimizer.path_graph, 29, 23, BLOCKED)
	optimizer.add_conveyor_path(optimizer.path_graph, 29, 35, MACHINE_OUTPUT)

	optimizer.add_conveyor_path(optimizer.path_graph, 30, 24, BLOCKED)
	optimizer.add_conveyor_path(optimizer.path_graph, 30, 36, MACHINE_OUTPUT)

	optimizer.add_conveyor_path(optimizer.path_graph, 31, 26, PASS)
	optimizer.add_conveyor_path(optimizer.path_graph, 31, 38, BLOCKED)

	optimizer.add_conveyor_path(optimizer.path_graph, 32, 27, BLOCKED)
	optimizer.add_conveyor_path(optimizer.path_graph, 32, 39, PASS)
	optimizer.add_conveyor_path(optimizer.path_graph, 32, 33, PASS)

	optimizer.add_conveyor_path(optimizer.path_graph, 33, 32, BLOCKED)
	optimizer.add_conveyor_path(optimizer.path_graph, 33, 34, PASS)

	optimizer.add_conveyor_path(optimizer.path_graph, 34, 33, BLOCKED)
	optimizer.add_conveyor_path(optimizer.path_graph, 34, 28, BLOCKED)
	optimizer.add_conveyor_path(optimizer.path_graph, 34, 35, PASS)

	optimizer.add_conveyor_path(optimizer.path_graph, 35, 29, BLOCKED)
	optimizer.add_conveyor_path(optimizer.path_graph, 35, 34, BLOCKED)
	optimizer.add_conveyor_path(optimizer.path_graph, 35, 36, PASS)

	optimizer.add_conveyor_path(optimizer.path_graph, 36, 35, BLOCKED)
	optimizer.add_conveyor_path(optimizer.path_graph, 36, 37, PASS)
	optimizer.add_conveyor_path(optimizer.path_graph, 36, 30, BLOCKED)

	optimizer.add_conveyor_path(optimizer.path_graph, 37, 36, BLOCKED)
	optimizer.add_conveyor_path(optimizer.path_graph, 37, 38, PASS)

	optimizer.add_conveyor_path(optimizer.path_graph, 38, 37, BLOCKED)
	optimizer.add_conveyor_path(optimizer.path_graph, 38, 31, PASS)
	optimizer.add_conveyor_path(optimizer.path_graph, 38, 46, BLOCKED)

	optimizer.add_conveyor_path(optimizer.path_graph, 39, 40, BLOCKED)
	optimizer.add_conveyor_path(optimizer.path_graph, 39, 32, BLOCKED)
	optimizer.add_conveyor_path(optimizer.path_graph, 39, 41, PASS)

	optimizer.add_conveyor_path(optimizer.path_graph, 40, 39, PASS)

	optimizer.add_conveyor_path(optimizer.path_graph, 41, 39, BLOCKED)
	optimizer.add_conveyor_path(optimizer.path_graph, 41, 42, PASS)

	optimizer.add_conveyor_path(optimizer.path_graph, 42, 41, BLOCKED)
	optimizer.add_conveyor_path(optimizer.path_graph, 42, 43, PASS)
	optimizer.add_conveyor_path(optimizer.path_graph, 42, 48, PASS)

	optimizer.add_conveyor_path(optimizer.path_graph, 43, 42, BLOCKED)
	optimizer.add_conveyor_path(optimizer.path_graph, 43, 44, PASS)
	optimizer.add_conveyor_path(optimizer.path_graph, 43, 49, PASS)

	optimizer.add_conveyor_path(optimizer.path_graph, 44, 43, BLOCKED)
	optimizer.add_conveyor_path(optimizer.path_graph, 44, 45, PASS)
	optimizer.add_conveyor_path(optimizer.path_graph, 44, 50, PASS)

	optimizer.add_conveyor_path(optimizer.path_graph, 45, 44, BLOCKED)
	optimizer.add_conveyor_path(optimizer.path_graph, 45, 46, PASS)

	optimizer.add_conveyor_path(optimizer.path_graph, 46, 38, PASS)
	optimizer.add_conveyor_path(optimizer.path_graph, 46, 47, BLOCKED)

	optimizer.add_conveyor_path(optimizer.path_graph, 47, 46, PASS)

	#Reverse
	optimizer.add_conveyor_path(optimizer.reverse_graph,  1, 3, PASS)

	optimizer.add_conveyor_path(optimizer.reverse_graph,  3, 1, BLOCKED)
	optimizer.add_conveyor_path(optimizer.reverse_graph,  3, 8, PASS)

	optimizer.add_conveyor_path(optimizer.reverse_graph,  8, 3, BLOCKED)
	optimizer.add_conveyor_path(optimizer.reverse_graph,  8, 9, PASS)
	optimizer.add_conveyor_path(optimizer.reverse_graph,  8, 15, PASS)

	optimizer.add_conveyor_path(optimizer.reverse_graph,  9, 8, BLOCKED)
	optimizer.add_conveyor_path(optimizer.reverse_graph,  9, 10, PASS)

	optimizer.add_conveyor_path(optimizer.reverse_graph,  10, 9, BLOCKED)
	optimizer.add_conveyor_path(optimizer.reverse_graph,  10, 11, PASS)
	optimizer.add_conveyor_path(optimizer.reverse_graph,  10, 4, MACHINE_INPUT)
	optimizer.add_conveyor_path(optimizer.reverse_graph,  10, 16, MACHINE_INPUT)

	optimizer.add_conveyor_path(optimizer.reverse_graph,  4, 10, MACHINE_OUTPUT)

	optimizer.add_conveyor_path(optimizer.reverse_graph,  11, 10, BLOCKED)
	optimizer.add_conveyor_path(optimizer.reverse_graph,  11, 12, PASS)
	optimizer.add_conveyor_path(optimizer.reverse_graph,  11, 17, MACHINE_INPUT)
	optimizer.add_conveyor_path(optimizer.reverse_graph,  11, 5, MACHINE_INPUT)

	optimizer.add_conveyor_path(optimizer.reverse_graph,  5, 11, MACHINE_OUTPUT)

	optimizer.add_conveyor_path(optimizer.reverse_graph,  12, 11, BLOCKED)
	optimizer.add_conveyor_path(optimizer.reverse_graph,  12, 13, PASS)
	optimizer.add_conveyor_path(optimizer.reverse_graph,  12, 6, MACHINE_INPUT)
	optimizer.add_conveyor_path(optimizer.reverse_graph,  12, 18, MACHINE_INPUT)

	optimizer.add_conveyor_path(optimizer.reverse_graph,  13, 12, BLOCKED)
	optimizer.add_conveyor_path(optimizer.reverse_graph,  13, 14, PASS)

	optimizer.add_conveyor_path(optimizer.reverse_graph,  6, 12, PASS)

	optimizer.add_conveyor_path(optimizer.reverse_graph,  14, 13, BLOCKED)
	optimizer.add_conveyor_path(optimizer.reverse_graph,  14, 7, PASS)
	optimizer.add_conveyor_path(optimizer.reverse_graph,  14, 19, BLOCKED)

	optimizer.add_conveyor_path(optimizer.reverse_graph,  7, 14, BLOCKED)
	optimizer.add_conveyor_path(optimizer.reverse_graph,  7, 2, PASS)

	optimizer.add_conveyor_path(optimizer.reverse_graph,  2, 7, BLOCKED)

	optimizer.add_conveyor_path(optimizer.reverse_graph,  15, 20, PASS)
	optimizer.add_conveyor_path(optimizer.reverse_graph,  15, 8, BLOCKED)

	optimizer.add_conveyor_path(optimizer.reverse_graph,  16, 22, MACHINE_OUTPUT)
	optimizer.add_conveyor_path(optimizer.reverse_graph,  16, 10, BLOCKED)

	optimizer.add_conveyor_path(optimizer.reverse_graph,  17, 11, BLOCKED)
	optimizer.add_conveyor_path(optimizer.reverse_graph,  17, 23, MACHINE_OUTPUT)

	optimizer.add_conveyor_path(optimizer.reverse_graph,  18, 12, BLOCKED)
	optimizer.add_conveyor_path(optimizer.reverse_graph,  18, 24, MACHINE_OUTPUT)

	optimizer.add_conveyor_path(optimizer.reverse_graph,  19, 14, PASS)
	optimizer.add_conveyor_path(optimizer.reverse_graph,  19, 26, BLOCKED)

	optimizer.add_conveyor_path(optimizer.reverse_graph,  20, 15, BLOCKED)
	optimizer.add_conveyor_path(optimizer.reverse_graph,  20, 27, PASS)
	optimizer.add_conveyor_path(optimizer.reverse_graph,  20, 21, PASS)

	optimizer.add_conveyor_path(optimizer.reverse_graph,  21, 20, BLOCKED)
	optimizer.add_conveyor_path(optimizer.reverse_graph,  21, 22, PASS)

	optimizer.add_conveyor_path(optimizer.reverse_graph,  22, 21, BLOCKED)
	optimizer.add_conveyor_path(optimizer.reverse_graph,  22, 23, PASS)
	optimizer.add_conveyor_path(optimizer.reverse_graph,  22, 16, BLOCKED)
	optimizer.add_conveyor_path(optimizer.reverse_graph,  22, 28, MACHINE_INPUT)

	optimizer.add_conveyor_path(optimizer.reverse_graph,  23, 17, BLOCKED)
	optimizer.add_conveyor_path(optimizer.reverse_graph,  23, 29, MACHINE_INPUT)
	optimizer.add_conveyor_path(optimizer.reverse_graph,  23, 22, BLOCKED)
	optimizer.add_conveyor_path(optimizer.reverse_graph,  23, 24, PASS)

	optimizer.add_conveyor_path(optimizer.reverse_graph,  24, 18, BLOCKED)
	optimizer.add_conveyor_path(optimizer.reverse_graph,  24, 30, PASS)
	optimizer.add_conveyor_path(optimizer.reverse_graph,  24, 23, BLOCKED)
	optimizer.add_conveyor_path(optimizer.reverse_graph,  24, 25, PASS)

	optimizer.add_conveyor_path(optimizer.reverse_graph,  25, 24, BLOCKED)
	optimizer.add_conveyor_path(optimizer.reverse_graph,  25, 26, PASS)

	optimizer.add_conveyor_path(optimizer.reverse_graph,  26, 19, PASS)
	optimizer.add_conveyor_path(optimizer.reverse_graph,  26, 31, BLOCKED)
	optimizer.add_conveyor_path(optimizer.reverse_graph,  26, 25, BLOCKED)

	optimizer.add_conveyor_path(optimizer.reverse_graph,  27, 20, BLOCKED)
	optimizer.add_conveyor_path(optimizer.reverse_graph,  27, 32, PASS)

	optimizer.add_conveyor_path(optimizer.reverse_graph,  28, 22, BLOCKED)
	optimizer.add_conveyor_path(optimizer.reverse_graph,  28, 34, MACHINE_OUTPUT)

	optimizer.add_conveyor_path(optimizer.reverse_graph,  29, 23, BLOCKED)
	optimizer.add_conveyor_path(optimizer.reverse_graph,  29, 35, MACHINE_OUTPUT)

	optimizer.add_conveyor_path(optimizer.reverse_graph,  30, 24, BLOCKED)
	optimizer.add_conveyor_path(optimizer.reverse_graph,  30, 36, MACHINE_OUTPUT)

	optimizer.add_conveyor_path(optimizer.reverse_graph,  31, 26, PASS)
	optimizer.add_conveyor_path(optimizer.reverse_graph,  31, 38, BLOCKED)

	optimizer.add_conveyor_path(optimizer.reverse_graph,  32, 27, BLOCKED)
	optimizer.add_conveyor_path(optimizer.reverse_graph,  32, 39, PASS)
	optimizer.add_conveyor_path(optimizer.reverse_graph,  32, 33, PASS)

	optimizer.add_conveyor_path(optimizer.reverse_graph,  33, 32, BLOCKED)
	optimizer.add_conveyor_path(optimizer.reverse_graph,  33, 34, PASS)

	optimizer.add_conveyor_path(optimizer.reverse_graph,  34, 33, BLOCKED)
	optimizer.add_conveyor_path(optimizer.reverse_graph,  34, 28, BLOCKED)
	optimizer.add_conveyor_path(optimizer.reverse_graph,  34, 35, PASS)

	optimizer.add_conveyor_path(optimizer.reverse_graph,  35, 29, BLOCKED)
	optimizer.add_conveyor_path(optimizer.reverse_graph,  35, 34, BLOCKED)
	optimizer.add_conveyor_path(optimizer.reverse_graph,  35, 36, PASS)

	optimizer.add_conveyor_path(optimizer.reverse_graph,  36, 35, BLOCKED)
	optimizer.add_conveyor_path(optimizer.reverse_graph,  36, 37, PASS)
	optimizer.add_conveyor_path(optimizer.reverse_graph,  36, 30, BLOCKED)

	optimizer.add_conveyor_path(optimizer.reverse_graph,  37, 36, BLOCKED)
	optimizer.add_conveyor_path(optimizer.reverse_graph,  37, 38, PASS)

	optimizer.add_conveyor_path(optimizer.reverse_graph,  38, 37, BLOCKED)
	optimizer.add_conveyor_path(optimizer.reverse_graph,  38, 31, PASS)
	optimizer.add_conveyor_path(optimizer.reverse_graph,  38, 46, BLOCKED)

	optimizer.add_conveyor_path(optimizer.reverse_graph,  39, 40, BLOCKED)
	optimizer.add_conveyor_path(optimizer.reverse_graph,  39, 32, BLOCKED)
	optimizer.add_conveyor_path(optimizer.reverse_graph,  39, 41, PASS)

	optimizer.add_conveyor_path(optimizer.reverse_graph,  40, 39, PASS)

	optimizer.add_conveyor_path(optimizer.reverse_graph,  41, 39, BLOCKED)
	optimizer.add_conveyor_path(optimizer.reverse_graph,  41, 42, PASS)

	optimizer.add_conveyor_path(optimizer.reverse_graph,  42, 41, BLOCKED)
	optimizer.add_conveyor_path(optimizer.reverse_graph,  42, 43, PASS)
	optimizer.add_conveyor_path(optimizer.reverse_graph,  42, 48, PASS)

	optimizer.add_conveyor_path(optimizer.reverse_graph,  43, 42, BLOCKED)
	optimizer.add_conveyor_path(optimizer.reverse_graph,  43, 44, PASS)
	optimizer.add_conveyor_path(optimizer.reverse_graph,  43, 49, PASS)

	optimizer.add_conveyor_path(optimizer.reverse_graph,  44, 43, BLOCKED)
	optimizer.add_conveyor_path(optimizer.reverse_graph,  44, 45, PASS)
	optimizer.add_conveyor_path(optimizer.reverse_graph,  44, 50, PASS)

	optimizer.add_conveyor_path(optimizer.reverse_graph,  45, 44, BLOCKED)
	optimizer.add_conveyor_path(optimizer.reverse_graph,  45, 46, PASS)

	optimizer.add_conveyor_path(optimizer.reverse_graph,  46, 38, PASS)
	optimizer.add_conveyor_path(optimizer.reverse_graph,  46, 47, BLOCKED)

	optimizer.add_conveyor_path(optimizer.reverse_graph,  47, 46, PASS)

	print('Optimizer setup complete')

