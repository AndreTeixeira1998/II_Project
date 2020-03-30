import pickle
import sys
sys.path.insert(0, "..")
from baby_optimizer import BabyOptimizer
from transfgraph import TransfGraph, Transform, Machine

#Object instantiation
optimizer = BabyOptimizer()

#Specifying all types of pieces available
optimizer.add_piece_type('P1')
optimizer.add_piece_type('P2')
optimizer.add_piece_type('P3')
optimizer.add_piece_type('P4')
optimizer.add_piece_type('P5')
optimizer.add_piece_type('P9')
optimizer.add_piece_type('P6')
optimizer.add_piece_type('P7')
optimizer.add_piece_type('P8')

#Specifying all machines available
optimizer.add_machine('Ma')
optimizer.add_machine('Mb')
optimizer.add_machine('Mc')

#Specifying all transforms available
optimizer.add_transform('P1', 'P2', Transform(optimizer.machines['Ma'], 'T1', 15))
optimizer.add_transform('P1', 'P3', Transform(optimizer.machines['Mb'], 'T2', 20))
optimizer.add_transform('P1', 'P4', Transform(optimizer.machines['Mc'], 'T1', 10))
optimizer.add_transform('P2', 'P3', Transform(optimizer.machines['Ma'], 'T1', 15))
optimizer.add_transform('P2', 'P6', Transform(optimizer.machines['Ma'], 'T2', 15))
optimizer.add_transform('P3', 'P4', Transform(optimizer.machines['Mb'], 'T1', 15))
optimizer.add_transform('P4', 'P5', Transform(optimizer.machines['Mc'], 'T1', 30))
optimizer.add_transform('P4', 'P8', Transform(optimizer.machines['Mc'], 'T2', 10))
optimizer.add_transform('P3', 'P7', Transform(optimizer.machines['Mb'], 'T2', 20))
optimizer.add_transform('P6', 'P9', Transform(optimizer.machines['Ma'], 'T3', 15))
optimizer.add_transform('P8', 'P9', Transform(optimizer.machines['Mc'], 'T3', 30))
optimizer.add_transform('P7', 'P9', Transform(optimizer.machines['Mb'], 'T3', 20))

with open("babyFactory.pickle","wb") as config_pickle:
	pickle.dump(optimizer, config_pickle)