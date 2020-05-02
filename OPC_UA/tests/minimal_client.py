import asyncio
import sys
sys.path.insert(0, "..")
import logging
from asyncua import Client, Node, ua

logging.basicConfig(level=logging.INFO)
_logger = logging.getLogger('asyncua')

async def main():
    url = 'opc.tcp://localhost:4840/'
    async with Client(url=url) as client:
        root = client.get_root_node()
        program = await root.get_child(['0:Objects', '0:Server', '4:CODESYS Control Win V3 x64', '3:Resources', '4:Application', '3:Programs', '4:PLC_PRG'])
        vars = await program.get_children()

        while True:
            for var in vars:
                print('{}: \t {}' .format((await var.get_display_name())._text,  await var.read_value()))

        _logger.info('Objects node is: %r', root)
        print(program)
        _logger.info('Children of root are: %r', await root.get_children())

        print(await root.get_children())

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.set_debug(True)
    loop.run_until_complete(main())
    loop.close()