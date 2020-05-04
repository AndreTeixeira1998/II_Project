import asyncio
from threading import Thread
from queue import Queue
import sys

from OPC_UA.opc_client import *
from Receive_client_orders.Order import *
from Receive_client_orders.Order_receiver import *
from DB.db_handler import *
sys.path.insert(0, "Statistics") # Só assim é que me começou a funcionar, juro por deus que não percebo os  retardanços do windows com as paths
from GUI import GUI

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
	
	win = GUI(db)

	q_udp = Queue()
	t_order_rec = Thread(target = order_receive, args = (q_udp, db, ))
	t_path_finder = Thread(target = run, args = (q_udp, ))

	t_order_rec.start()
	t_path_finder.start()
	
	win.open_GUI()