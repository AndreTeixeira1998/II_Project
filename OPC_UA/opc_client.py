import asyncio
import sys
sys.path.insert(0, "..")
import logging
import pickle

from asyncua import Client, Node, ua
from subhandles import OptimizerSubHandler
from Optimizer.baby_optimizer import BabyOptimizer


SUB_PERIOD = 20 #Publishing interval in miliseconds
LOG_FILENAME = 'opc_client.log'

logging.basicConfig(level=logging.DEBUG, filename=LOG_FILENAME)
_logger = logging.getLogger('asyncua')


class Piece():
	'''
	Há de fazer grandes coisas esta classe

	'''
	def __init__(self, id, var, optimizer):
		self.id = id
		self.var = var
		self.optimizer=optimizer
		self.waiting_time = 0

	def __str__(self):
		return self.id
		
	async def write_int16(self, var, value):
		datavalue = ua.DataValue(ua.Variant(value, ua.VariantType.Int16))
		await var.write_value(datavalue)

	async def write_bool(self, var, value):
		datavalue = ua.DataValue(ua.Variant(value, ua.VariantType.Boolean))
		await var.write_value(datavalue)

	def compute_conveyor(self, before, after):
		duration, piece, trans_path = self.optimizer.compute_transform(before, after)
		path_to_write = self.optimizer.compute_path(trans_path)
		return path_to_write



async def write_int16(var, value):
	#	datavalue = ua.DataValue(ua._val_to_variant(value, Int16))
	datavalue = ua.DataValue(ua.Variant(value, ua.VariantType.Int16))
	await var.write_value(datavalue)

async def write_bool(var, value):
	datavalue = ua.DataValue(ua.Variant(value, ua.VariantType.Boolean))
	await var.write_value(datavalue)

async def write_array_int16(array, value):
	dataarray = ua.DataValue(ua.Variant(array, ua.VariantType.Int16))
	await array.write_value(dataarray)
	

async def write(client, var, optimizer):
	print("######################debug: write() started")
	
	p = Piece(1, var, optimizer)
	duration, piece, trans_path = optimizer.compute_transform("P2", "P5")
	
	path_to_write = optimizer.compute_path(trans_path)
	
	 ### testar com o primeiro da lista para implementar indices
	
	while True:

			await asyncio.sleep(5)
			
			#try:
			print("###############################    Changing Value!   ###########################")
			await write_int16(var, path_to_write) # set node value using implicit data type
			#except:
			#	print("!!!!!!!!!!!!!!!!!!!!!!!  ERROR  Changing Value!   !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")

	


async def read(client, vars, optimizer):
	print("######################debug: read() started")
	
	handler = OptimizerSubHandler(optimizer, _logger)

	sub = await client.create_subscription(SUB_PERIOD, handler)
	await sub.subscribe_data_change(vars)



async def main():
	url = 'opc.tcp://localhost:4840/'
	#Load optimizer configs from a pickle
	with open("../Optimizer/config/babyFactory.pickle", "rb") as config_pickle:
		optimizer = pickle.load(config_pickle)
	
	async with Client(url=url) as client:
		#root = client.get_root_node()
		#program = await root.get_child(['0:Objects', '0:Server', '4:CODESYS Control Win V3 x64', '3:Resources', '4:Application', '3:Programs', '4:PLC_PRG'])
		#vars = await program.get_children()
		var = client.get_node("ns=4;s=|var|CODESYS Control Win V3 x64.Application.GVL.piece_array[0].path") ###variavel teste

		await asyncio.gather(read(client, var, optimizer), write(client, var, optimizer))
		

		#Runs for 1 min
		#TODO: Change this into a permanent connection
		await asyncio.sleep(100)

if __name__ == '__main__':
	loop = asyncio.get_event_loop()
	loop.set_debug(True)
	loop.run_until_complete(main())
	loop.close()