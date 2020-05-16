import asyncio
from threading import Thread
from queue import Queue
import time

from OPC_UA.opc_client import *
from Receive_client_orders.Order import *
from Receive_client_orders.Order_receiver import *
from Optimizer.baby_optimizer import HorOptimizer
from db.db_handler import *

def test_thread(optimizer):
	while True:
		#print(f'{optimizer.state.num_pieces} {optimizer.dispatch_queue}')
		time.sleep(1)

def compute_orders(optimizer, q_udp_in):
	while True:
		while not q_udp_in.empty():
			order = q_udp_in.get()
			for o in order:
				if o.order_type == 'Transform':
					i = 0
					print(f"{i}")
					i = i+1
					optimizer.order_handler(o)
					optimizer.optimize_all_pieces()
				elif o.order_type == 'Unload':
					optimizer.order_handler(o)
			#optimizer.print_machine_schedule()

def update_dispatch(optimizer):
	while True:
		for machine in optimizer.state.machines.values():
			#print(f'{machine}: {machine.op_list}')
			if machine.is_free and machine.op_list:
				next_op = machine.op_list[0]
				if next_op.step == 1:
					optimizer.dispatch_queue.append(optimizer.state.pieces[next_op.piece_id])
					machine.make_unavailable()
				else:
					machine.make_unavailable()
		time.sleep(0.1)


def run(optimizer):
	
	# loop = asyncio.get_event_loop()
	#	Para multi thrading...acho
	#	https://stackoverflow.com/questions/46727787/runtimeerror-there-is-no-current-event-loop-in-thread-in-async-apscheduler
	loop = asyncio.new_event_loop() 
	asyncio.set_event_loop(loop)
	loop.set_debug(True)
	loop.run_until_complete(opc_client_run(optimizer))
	loop.close()

#	https://docs.python.org/3.8/library/signal.html
#	https://docs.python.org/3/library/asyncio-queue.html
if __name__ == "__main__":
	db = DB_handler()
	optimizer = HorOptimizer()

	q_udp = Queue()		#	Exchanges information from order receiver to the next stage of the program
	t_order_rec = Thread(target = order_receive, args = (q_udp, db, True))
	t_order_rec.name = "Thread_client_receive"
	t_opc_run = Thread(target = run, args = (optimizer, ))
	t_opc_run.name = "Thread_opc_run"
	t_compute_orders = Thread(target=compute_orders, args=(optimizer, q_udp,))
	t_compute_orders.name = "Thread_compute_order"
	t_update_dispatch = Thread(target=update_dispatch, args=(optimizer,))
	t_update_dispatch.name = "Thread_update_dispatch"
	t_test = Thread(target=test_thread, args=(optimizer,))
	t_test.name = "Test"

	threads = [t_order_rec, t_opc_run, t_compute_orders, t_update_dispatch, t_test]

	t_opc_run.start()
	t_order_rec.start()
	t_compute_orders.start()
	t_update_dispatch.start()
	t_test.start()


	## Joints all the threads
	map(lambda x:x.join(),threads)
