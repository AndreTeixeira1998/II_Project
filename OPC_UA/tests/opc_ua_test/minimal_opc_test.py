import asyncio
import sys
sys.path.insert(0, "..")
import logging
from asyncua import Client, Node, ua
import time

logging.basicConfig(level=logging.INFO)
_logger = logging.getLogger('asyncua')



async def read(url):
	print("######################debug: read() started")

	
	async with Client(url=url) as client:
		root = client.get_root_node()
		program = await root.get_child(['0:Objects', '0:Server', '4:CODESYS Control Win V3 x64', '3:Resources', '4:Application', '3:Programs', '4:PLC_PRG'])
		vars = await program.get_children()
	
		var_test = client.get_node("ns=4;s=|var|CODESYS Control Win V3 x64.Application.PLC_PRG.int_var")
		print('{}: \t {}' .format("teste", await var_test.get_value()))
		##print(var)
		##var.get_data_value() # get value of node as a DataValue object
		#var.get_value() # get value of node as a python builtin

		while True:
			for var in vars:
				var_output_test= await var.read_value()
				print('{}: \t {}' .format((await var.get_display_name())._text, await var.read_value()))
				print("test", var_output_test)
			await asyncio.sleep(1)
			print("-----------------------------------------------------")
			#input_var= input()
			#print( input_var)
				
	
		_logger.info('Objects node is: %r', root)
		print(program)
		_logger.info('Children of root are: %r', await root.get_children())
	
		print(await root.get_children())
	


async def write(url):
	print("######################debug: write() started")
	
	async with Client(url=url) as client:

	
		var_test = client.get_node("ns=4;s=|var|CODESYS Control Win V3 x64.Application.PLC_PRG.int_var")
		print('+++++++++++++++++++++++++++++++++++++++++ {}: \t {} +++++++++++++++++++++++++++++++++++++++++++++' .format("teste", await var_test.get_value()))
		##print(var)

		while True:

			await asyncio.sleep(5)
		
			print("###############################    Changing Value!   ###########################")
			
			try:
				#input_var= input()
				#print(input_var)
				datavalue = ua.DataValue(ua.Variant(3, ua.VariantType.Int16))
				await var_test.write_value(datavalue) # set node value using implicit data type
			except:
				print("!!!!!!!!!!!!!!!!!!!!!!!  ERROR  Changing Value!   !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
				

async def main():
	url = 'opc.tcp://localhost:4840/'
	
	try:
		await asyncio.gather(read(url), write(url))
	
	except Exception:
		_logger.exception('error')
	
#	finally:
#		client.disconnect()
#		print("disconected")	
	


if __name__ == '__main__':
	loop = asyncio.get_event_loop()
	loop.set_debug(True)
	loop.run_until_complete(main())
	loop.close()
