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



def int_threading():
	raise NotImplementedError

def run(q_udp_in):
	
	# loop = asyncio.get_event_loop()
	#	Para multi thrading...acho
	#	https://stackoverflow.com/questions/46727787/runtimeerror-there-is-no-current-event-loop-in-thread-in-async-apscheduler
	loop = asyncio.new_event_loop() 
	asyncio.set_event_loop(loop)
	loop.set_debug(True)
	loop.run_until_complete(main(q_udp_in))
	loop.close()

#	https://docs.python.org/3.8/library/signal.html
#	https://docs.python.org/3/library/asyncio-queue.html
if __name__ == "__main__":
	db = DB_handler()

	q_udp = Queue()		#	Exchanges information from order receiver to the next stage of the program
	t_order_rec = Thread(target = order_receive, args = (q_udp, db, ))
	t_order_rec.name = "Thread_client_receive"
	t_path_finder = Thread(target = run, args = (q_udp, ))
	t_path_finder.name = "Thread_path_finder"

	threads = [t_order_rec, t_path_finder]

	t_order_rec.start()
	t_path_finder.start()

	## Joints all the threads
	map(lambda x:x.join(),threads)