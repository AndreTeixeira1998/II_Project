import asyncio
from threading import Thread
from queue import Queue

from OPC_UA.opc_client import *
from Receive_client_orders.Order import *
from Receive_client_orders.Order_receiver import *
from db.db_handler import *

def order_into_pieces(order:Order):
	if order.get("order_type") == "Transform":		
		pass
	if order.get("order_type") == "Unload":
		pass
	raise NotImplementedError
	# return pieces


def order_handler():

	raise NotImplementedError

def int_threading():
	raise NotImplementedError

def run(q_udp_in):
	
	loop = asyncio.get_event_loop()
	loop.set_debug(True)
	loop.run_until_complete(main(q_udp_in))
	loop.close()

#	https://docs.python.org/3.8/library/signal.html
#	https://docs.python.org/3/library/asyncio-queue.html
if __name__ == "__main__":
	
	q_udp = Queue()
	t_order_rec = Thread(target = order_receive, args = (q_udp, ))
	t_path_finder = Thread(target = run, args = (q_udp, ))

	t_order_rec.start()
	t_path_finder.start()