import asyncio
import sys
import collections
from queue import Queue

sys.path.insert(0, "..")
import logging
import pickle
import numpy as np
from array import array
from asyncua import Client, Node, ua
from OPC_UA.subhandles import OptimizerSubHandler
from Optimizer.baby_optimizer import BabyOptimizer
from Optimizer.baby_optimizer import Piece
from Optimizer.baby_optimizer import Pusher

from Receive_client_orders.Order import TransformOrder, UnloadOrder

from threading import Thread

SUB_PERIOD = 20  # Publishing interval in miliseconds
LOG_FILENAME = 'opc_client.log'

logging.basicConfig(level=logging.DEBUG, filename=LOG_FILENAME)
_logger = logging.getLogger('asyncua')

# Some Global Vars
path_length = 51
transf_length = 6

machine_dic = {'Ma_1': 1, 'Mb_1': 2, 'Mc_1': 3,
               'Ma_2': 1, 'Mb_2': 2, 'Mc_2': 3,
               'Ma_3': 1, 'Mb_3': 2, 'Mc_3': 3, 0:0}

tool_dic = {'T1': 1, 'T2': 2, 'T3': 3, 0:0}


class OnePiece():
    '''
    Classe Piece deveria ser importada mas sou lazy as **** 

    '''

    def __str__(self):
        return self.id

    async def write_int16(self, var, value):
        datavalue = ua.DataValue(ua.Variant(value, ua.VariantType.Int16))
        await var.write_value(datavalue)

    async def write_array_int16(self, var, array, Array_LENGTH):
        array.extend(np.zeros(Array_LENGTH - len(array), dtype=int))
        datavalue = ua.DataValue(ua.Variant(array, ua.VariantType.Int16))
        await var.write_value(datavalue)

    async def write_bool(self, var, value):
        datavalue = ua.DataValue(ua.Variant(value, ua.VariantType.Boolean))
        await var.write_value(datavalue)

    async def send_path(self, piece, var_write):  # piece, var_path, var_id, var_maq, var_tool, var_new_piece, var_tipo_atual):
        print("Send piece")
        machine_translated = [machine_dic[machine] for machine in piece.machines]
        tools_translated = [tool_dic[tool] for tool in piece.tools]
        print(machine_translated)
        print(tools_translated)
        await self.write_array_int16(var_write["path"], piece.path,
                                     path_length)  # set node value using implicit data type
        await self.write_int16(var_write["id"], piece.id)  # set node value using implicit data type
        await self.write_int16(var_write["tipo_atual"], piece.type)
        await self.write_array_int16(var_write["maq"], machine_translated, transf_length)
        await self.write_array_int16(var_write["tool"], tools_translated, transf_length)
        await self.write_bool(var_write["new_piece"], True)
        return


async def write(client, vars, optimizer, cond):
    print("######################debug: write() started")
    var_id = await vars.get_child("4:id")
    var_path = await vars.get_child("4:path")
    var_maq = client.get_node("ns=4;s=|var|CODESYS Control Win V3 x64.Application.GVL.piece_array[0].transf.maq")
    var_tool = client.get_node("ns=4;s=|var|CODESYS Control Win V3 x64.Application.GVL.piece_array[0].transf.tool")
    var_new_piece = client.get_node("ns=4;s=|var|CODESYS Control Win V3 x64.Application.GVL.new_piece")
    var_tipo_atual = client.get_node("ns=4;s=|var|CODESYS Control Win V3 x64.Application.GVL.piece_array[0].tipo_atual")

    var_write = {"id": var_id,
                 "path": var_path,
                 "maq": var_maq,
                 "tool": var_tool,
                 "new_piece": var_new_piece,
                 "tipo_atual": var_tipo_atual}

    # id=1
    sender = OnePiece()

    while True:
        if optimizer.dispatch_queue:
            print("DEBUG ====>", optimizer.dispatch_queue)
            await cond.wait()
            piece = optimizer.dispatch_queue.popleft()
            
            await sender.send_path(piece, var_write)
            print(f"Dispatching piece no {piece.id}: ")
            print(list(optimizer.dispatch_queue))
            cond.clear()
        await asyncio.sleep(1)

async def read(client, vars, handler):
    print("######################debug: read() started")
    sub = await client.create_subscription(SUB_PERIOD, handler)
    await sub.subscribe_data_change(vars)


async def charge_P1(client, cond2, charge_var):
    print("######################debug: load P1 started")
    
    sender = OnePiece()
    dest_path = [39, 41, 42, 43, 44, 45, 46, 38, 31, 26, 19, 14, 7, 2]
    var_load_path = client.get_node("ns=4;s=|var|CODESYS Control Win V3 x64.Application.GVL.piece_array[40].path")
    #var_load_tipo_atual = client.get_node("ns=4;s=|var|CODESYS Control Win V3 x64.Application.GVL.piece_array[40].tipo_atual")
    #var_load_id

    while True:
        if(await charge_var.get_value()):
            await cond2.wait()
            #print("OOOOOOOOOOOOOOOOOOOOOOOOOOOO", await charge_var.get_value())
            #await self.write_int16(var_write["id"], piece.id)  # set node value using implicit data type
            #await self.write_int16(var_write["tipo_atual"], piece.type)
            await sender.write_array_int16(var_load_path, dest_path,
                                     path_length)  # set node value using implicit data type
            cond2.clear()
            
async def charge_P2(client, cond3, charge_var):
    print("######################debug: load P2 started")
    
    sender = OnePiece()
    dest_path = [46, 38, 31, 26, 19, 14, 7, 2]
    var_load_path = client.get_node("ns=4;s=|var|CODESYS Control Win V3 x64.Application.GVL.piece_array[47].path")
    #var_load_tipo_atual
    #var_load_id
    
    while True:
    
        if (await charge_var.get_value()):
            await cond3.wait()
            #print("OOOOOOOOOOOOOOOOOOOOOOOOOOOO", await charge_var.get_value())
            await sender.write_array_int16(var_load_path, dest_path,
                                     path_length)  # set node value using implicit data type
            cond3.clear()
            
'''
def pusher1(vars_):
    print("OOOOOOOOOOOOOOOOOOOOOOOOOOOO1",  vars_["vars_1_discharge"].get_value())
    print("OOOOOOOOOOOOOOOOOOOOOOOOOOOO2",  vars_["vars_2_discharge"].get_value())
    print("OOOOOOOOOOOOOOOOOOOOOOOOOOOO3",  vars_["vars_3_discharge"].get_value())
'''

async def unload(client, optimizer, vars_, cond_pusher_1):
    print("######################debug: unload() started")
    
    while True:
        #if vars_["vars_1_discharge"] and vars_["vars_2_discharge"] and vars_["vars_3_discharge"]:
        #if (await vars_["vars_3_discharge"].get_value()):
            
            
        if optimizer.pusher.dispatch_queue_1:    
            #print("#########################DEBUUUUUUUUUGGGGGGGGGGG#########")
            await cond_pusher_1.wait()
            
            order_=optimizer.pusher.dispatch_queue_1.pop()
            print("quantidade em falta: ", order_.quantity)
            optimizer.order_handler(order_, continue_unload_command=True)
            #optimizer.optimize_all_pieces()
            optimizer.dispatch_queue.append(TransformOrder(order_type="Transform", order_number=3, max_delay=2000, before_type=4, after_type=5, quantity=3))
            cond_pusher_1.clear()
            
        
        


async def main():
    url = 'opc.tcp://localhost:4840/'

    ####################################### Isto n deve tar aqui é so para testar sem precisar de enviar ordens #################################
    optimizer = BabyOptimizer()

    fake_order = []

    #fake_order.append(TransformOrder(order_type="Transform", order_number=1,
    #                                 max_delay=2000, before_type=1, after_type=8, quantity=2))
    
    #fake_order.append(UnloadOrder(order_type="Unload", order_number=2,
    #                                piece_type=2, destination=2, quantity=5))

    #fake_order.append(UnloadOrder(order_type="Unload", order_number=2,
    #                                piece_type=4, destination=2, quantity=5))
    fake_order.append(UnloadOrder(order_type="Unload", order_number=2,
                                    piece_type=2, destination=1, quantity=5))

    #fake_order.append(UnloadOrder(order_type="Unload", order_number=2,
    #                                piece_type=4, destination=1, quantity=5))
    #fake_order.append(TransformOrder(order_type="Transform", order_number=3,
    #								 max_delay=2000, before_type=4, after_type=5, quantity=3))
    #fake_order.append(TransformOrder(order_type="Transform", order_number=3,
    #								 max_delay=2000, before_type=7, after_type=9, quantity=9))

    for order in fake_order:
        #print(
        #    f"Order number {order.order_number}. {order.quantity} transforms from P{order.before_type} to P{order.after_type}")
        optimizer.order_handler(order)
        print(f'Total number of pieces: {optimizer.state.num_pieces}\r\n')

    print(f'Optimizing {optimizer.state.num_pieces} pieces')
    optimizer.state = optimizer.optimize_all_pieces()
    print(f'{optimizer.state}')
    optimizer.print_machine_schedule()
    #############################################################################################################################################

    #

    async with Client(url=url) as client:

        vars_to_write = client.get_node("ns=4;s=|var|CODESYS Control Win V3 x64.Application.GVL.piece_array[0]")

        # Subscrições para monitorizar as maquinas
        ma_1, mb_1, mc_1 = client.get_node("ns=4;s=|var|CODESYS Control Win V3 x64.Application.tapetes.c1t3") \
            , client.get_node("ns=4;s=|var|CODESYS Control Win V3 x64.Application.tapetes.c1t4") \
            , client.get_node("ns=4;s=|var|CODESYS Control Win V3 x64.Application.tapetes.c1t5")
        ma_2, mb_2, mc_2 = client.get_node("ns=4;s=|var|CODESYS Control Win V3 x64.Application.tapetes.c3t3") \
            , client.get_node("ns=4;s=|var|CODESYS Control Win V3 x64.Application.tapetes.c3t4") \
            , client.get_node("ns=4;s=|var|CODESYS Control Win V3 x64.Application.tapetes.c3t5")

        ma_3, mb_3, mc_3 = client.get_node("ns=4;s=|var|CODESYS Control Win V3 x64.Application.tapetes.c5t3") \
            , client.get_node("ns=4;s=|var|CODESYS Control Win V3 x64.Application.tapetes.c5t4") \
            , client.get_node("ns=4;s=|var|CODESYS Control Win V3 x64.Application.tapetes.c5t5") \

        m_steps = await ma_1.get_children() + await mb_1.get_children() + await mc_1.get_children()
        m_steps += await ma_2.get_children() + await mb_2.get_children() + await mc_2.get_children()
        m_steps += await ma_3.get_children() + await mb_3.get_children() + await mc_3.get_children()

        m_vars = []
        for step in m_steps:
            nodes = await step.get_children()
            for node in nodes:
                m_vars.append(node)

        var_despacha_1_para_3 = client.get_node("ns=4;s=|var|CODESYS Control Win V3 x64.Application.tapetes.at1.Init.x")
        m_vars.append(var_despacha_1_para_3)
        
        vars_P1_charge = client.get_node("ns=4;s=|var|CODESYS Control Win V3 x64.Application.GVL.c7t1b_i.sensor")
        vars_P2_charge = client.get_node("ns=4;s=|var|CODESYS Control Win V3 x64.Application.GVL.c7t7b_i.sensor")
        m_vars.append(vars_P1_charge)
        m_vars.append(vars_P2_charge)
        
        vars_1_discharge = client.get_node("ns=4;s=|var|CODESYS Control Win V3 x64.Application.GVL.c7t3_i.sensor_extra")
        vars_2_discharge = client.get_node("ns=4;s=|var|CODESYS Control Win V3 x64.Application.IoConfig_Globals_Mapping.pm12_sensor")
        vars_3_discharge = client.get_node("ns=4;s=|var|CODESYS Control Win V3 x64.Application.IoConfig_Globals_Mapping.pm13_sensor")
        vars_pusher1 ={"vars_1_discharge":vars_1_discharge, "vars_2_discharge":vars_2_discharge, "vars_3_discharge":vars_3_discharge}
        m_vars.append(vars_3_discharge)
        
        #m_vars.append()

        cond = asyncio.Event()
        cond2=asyncio.Event()
        cond3=asyncio.Event()
        
        cond_pusher_1=asyncio.Event()
        #fazer dic
        
        handler = OptimizerSubHandler(optimizer, cond, cond2, cond3, cond_pusher_1, vars_pusher1, _logger)

        await asyncio.gather(read(client, m_vars, handler),
                              write(client, vars_to_write, optimizer, cond),
                              charge_P1(client,cond2, vars_P1_charge),
                              charge_P2(client,cond3, vars_P2_charge),
                              unload(client, optimizer, vars_pusher1, cond_pusher_1)
                             )

        await asyncio.sleep(10)

        # Runs for 1 min
        # TODO: Change this into a permanent connection
        await asyncio.sleep(100)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.set_debug(True)
    loop.run_until_complete(main())
    loop.close()
