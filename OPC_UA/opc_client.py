import asyncio
import sys
sys.path.insert(0, "..")
import logging

from asyncua import Client, Node
from subhandles import OptimizerSubHandler
from Optimizer.baby_optimizer import BabyOptimizer


SUB_PERIOD = 20 #Publishing interval in miliseconds
LOG_FILENAME = 'opc_client.log'

logging.basicConfig(level=logging.DEBUG, filename=LOG_FILENAME)
_logger = logging.getLogger('asyncua')


async def main():
    url = 'opc.tcp://localhost:4840/'
    async with Client(url=url) as client:
        root = client.get_root_node()
        program = await root.get_child(['0:Objects', '0:Server', '4:CODESYS Control Win V3 x64', '3:Resources', '4:Application', '3:Programs', '4:PLC_PRG'])
        vars = await program.get_children()


        optimizer = BabyOptimizer()
        handler = OptimizerSubHandler(optimizer, _logger)

        sub = await client.create_subscription(SUB_PERIOD, handler)
        await sub.subscribe_data_change(vars)

        #Runs for 1 min
        #TODO: Change this into a permanent connection
        await asyncio.sleep(100)

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.set_debug(True)
    loop.run_until_complete(main())
    loop.close()