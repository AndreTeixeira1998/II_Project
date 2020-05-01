import pickle
import sys
sys.path.insert(0, "..")
from Optimizer.transfgraph import TransfGraph, Transform, Machine

NUMBER_OF_CELLS = 3

#Object instantiation
def optimizer_init(optimizer):
	#Specifying all types of pieces available

	for cell in range(1, NUMBER_OF_CELLS+1):
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
		#Transformacao extra
		#optimizer.add_transform('P8', 'P7', Transform(optimizer.state-machines[f'Ma_{cell}'], 'T2', 30))


	for i in range(50):
		optimizer.add_conveyor(i+1)

	optimizer.add_conveyor_path( 1,  3, 1)

	optimizer.add_conveyor_path( 3,  1, 1)
	optimizer.add_conveyor_path( 3,  8, 1)

	optimizer.add_conveyor_path( 8,  3, 1)
	optimizer.add_conveyor_path( 8,  9, 1)
	optimizer.add_conveyor_path( 8, 15, 1)

	optimizer.add_conveyor_path( 9,  8, 1)
	optimizer.add_conveyor_path( 9, 10, 1)

	optimizer.add_conveyor_path(10,  9, 1)
	optimizer.add_conveyor_path(10, 11, 1)
	optimizer.add_conveyor_path(10,  4, 1)
	optimizer.add_conveyor_path(10, 16, 9999999999999999)

	optimizer.add_conveyor_path( 4, 10, 1)

	optimizer.add_conveyor_path(11, 10, 1)
	optimizer.add_conveyor_path(11, 12, 1)
	optimizer.add_conveyor_path(11, 17, 999999999999999)
	optimizer.add_conveyor_path(11,  5, 1)

	optimizer.add_conveyor_path( 5, 11, 1)

	optimizer.add_conveyor_path(12, 11, 1)
	optimizer.add_conveyor_path(12, 13, 1)
	optimizer.add_conveyor_path(12,  6, 1)
	optimizer.add_conveyor_path(12, 18, 999999999999999)

	optimizer.add_conveyor_path(13, 12, 1)
	optimizer.add_conveyor_path(13, 14, 1)

	optimizer.add_conveyor_path( 6, 12, 1)

	optimizer.add_conveyor_path(14, 13, 1)
	optimizer.add_conveyor_path(14,  7, 1)
	optimizer.add_conveyor_path(14, 19, 1)

	optimizer.add_conveyor_path( 7, 14, 1)
	optimizer.add_conveyor_path( 7,  2, 1)

	optimizer.add_conveyor_path( 2,  7, 1)

	optimizer.add_conveyor_path(15, 20, 1)
	optimizer.add_conveyor_path(15,  8, 1)

	optimizer.add_conveyor_path(16, 22, 1)
	optimizer.add_conveyor_path(16, 10, 1)

	optimizer.add_conveyor_path(17, 11, 1)
	optimizer.add_conveyor_path(17, 23, 1)

	optimizer.add_conveyor_path(18, 12, 1)
	optimizer.add_conveyor_path(18, 24, 1)

	optimizer.add_conveyor_path(19, 14, 1)
	optimizer.add_conveyor_path(19, 26, 1)

	optimizer.add_conveyor_path(20, 15, 1)
	optimizer.add_conveyor_path(20, 27, 1)
	optimizer.add_conveyor_path(20, 21, 1)

	optimizer.add_conveyor_path(21, 20, 1)
	optimizer.add_conveyor_path(21, 22, 1)

	optimizer.add_conveyor_path(22, 21, 1)
	optimizer.add_conveyor_path(22, 23, 1)
	optimizer.add_conveyor_path(22, 16, 1)
	optimizer.add_conveyor_path(22, 28, 9999999999999999)

	optimizer.add_conveyor_path(23, 17, 1)
	optimizer.add_conveyor_path(23, 29, 9999999999999999)

	optimizer.add_conveyor_path(24, 18, 1)
	optimizer.add_conveyor_path(24, 30, 9999999999999999)

	optimizer.add_conveyor_path(25, 24, 1)
	optimizer.add_conveyor_path(25, 26, 1)

	optimizer.add_conveyor_path(26, 19, 1)
	optimizer.add_conveyor_path(26, 31, 1)

	optimizer.add_conveyor_path(27, 20, 1)
	optimizer.add_conveyor_path(27, 32, 1)

	optimizer.add_conveyor_path(28, 22, 999999999999999)
	optimizer.add_conveyor_path(28, 34, 1)

	optimizer.add_conveyor_path(29, 23, 99999999999999)
	optimizer.add_conveyor_path(29, 35, 1)

	optimizer.add_conveyor_path(30, 24, 999999999999999)
	optimizer.add_conveyor_path(30, 36, 1)

	optimizer.add_conveyor_path(31, 26, 1)
	optimizer.add_conveyor_path(31, 38, 1)

	optimizer.add_conveyor_path(32, 27, 1)
	optimizer.add_conveyor_path(32, 39, 1)
	optimizer.add_conveyor_path(32, 33, 1)

	optimizer.add_conveyor_path(33, 32, 1)
	optimizer.add_conveyor_path(33, 34, 1)

	optimizer.add_conveyor_path(34, 33, 1)
	optimizer.add_conveyor_path(34, 28, 1)
	optimizer.add_conveyor_path(34, 35, 1)

	optimizer.add_conveyor_path(35, 29, 1)
	optimizer.add_conveyor_path(35, 34, 1)
	optimizer.add_conveyor_path(35, 36, 1)

	optimizer.add_conveyor_path(36, 35, 1)
	optimizer.add_conveyor_path(36, 37, 1)
	optimizer.add_conveyor_path(36, 30, 1)

	optimizer.add_conveyor_path(37, 36, 1)
	optimizer.add_conveyor_path(37, 38, 1)
	optimizer.add_conveyor_path(38, 37, 1)
	optimizer.add_conveyor_path(38, 31, 1)
	optimizer.add_conveyor_path(38, 46, 1)

	optimizer.add_conveyor_path(39, 40, 1)
	optimizer.add_conveyor_path(39, 32, 1)
	optimizer.add_conveyor_path(39, 41, 1)

	optimizer.add_conveyor_path(40, 39, 1)

	optimizer.add_conveyor_path(41, 39, 1)
	optimizer.add_conveyor_path(41, 42, 1)

	optimizer.add_conveyor_path(42, 41, 1)
	optimizer.add_conveyor_path(42, 43, 1)
	optimizer.add_conveyor_path(42, 48, 1)

	optimizer.add_conveyor_path(43, 42, 1)
	optimizer.add_conveyor_path(43, 44, 1)
	optimizer.add_conveyor_path(43, 49, 1)

	optimizer.add_conveyor_path(44, 43, 1)
	optimizer.add_conveyor_path(44, 45, 1)
	optimizer.add_conveyor_path(44, 50, 1)

	optimizer.add_conveyor_path(45, 44, 1)
	optimizer.add_conveyor_path(45, 46, 1)

	optimizer.add_conveyor_path(46, 38, 1)
	optimizer.add_conveyor_path(46, 47, 1)

	optimizer.add_conveyor_path(47, 46, 1)

