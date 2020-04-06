import asyncio
import sys
sys.path.insert(0, "..")
import logging

from asyncua import Client, Node, ua
from subhandles import OptimizerSubHandler
from Optimizer.baby_optimizer import BabyOptimizer


SUB_PERIOD = 20 #Publishing interval in miliseconds
LOG_FILENAME = 'opc_client.log'

logging.basicConfig(level=logging.DEBUG, filename=LOG_FILENAME)
_logger = logging.getLogger('asyncua')



async def write_int16(var, value):
	datavalue = ua.DataValue(ua.Variant(value, ua.VariantType.Int16))
	await var.write_value(datavalue)
	

async def write(client, vars, optimizer):
	print("######################debug: write() started")
	
	#var = client.get_node("ns=4;s=|var|CODESYS Control Win V3 x64.Application.PLC_PRG.int_var") ###variavel teste
	
	var = vars[1] ### testar com o primeiro da lista para implementar indices
	
	while True:

			await asyncio.sleep(5)
			
			try:
				print("###############################    Changing Value!   ###########################")
				await write_int16(var, 3) # set node value using implicit data type
			except:
				print("!!!!!!!!!!!!!!!!!!!!!!!  ERROR  Changing Value!   !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")

	


async def read(client, vars, optimizer):
	print("######################debug: read() started")
	
	handler = OptimizerSubHandler(optimizer, _logger)

	sub = await client.create_subscription(SUB_PERIOD, handler)
	await sub.subscribe_data_change(vars)



async def main():
	url = 'opc.tcp://localhost:4840/'
	optimizer = BabyOptimizer()
	async with Client(url=url) as client:
		root = client.get_root_node()
		program = await root.get_child(['0:Objects', '0:Server', '4:CODESYS Control Win V3 x64', '3:Resources', '4:Application', '3:Programs', '4:PLC_PRG'])
		vars = await program.get_children()
		 
		await asyncio.gather(read(client, vars, optimizer), write(client, vars, optimizer))
		

		#Runs for 1 min
		#TODO: Change this into a permanent connection
		await asyncio.sleep(100)

if __name__ == '__main__':
	loop = asyncio.get_event_loop()
	loop.set_debug(True)
	loop.run_until_complete(main())
	loop.close()