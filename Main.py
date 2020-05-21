import asyncio
from threading import Thread
from queue import Queue
import sys
import time

from OPC_UA.opc_client import *
from Receive_client_orders.Order import *
from Receive_client_orders.Order_receiver import *
from DB.db_handler import *
sys.path.insert(0, "Statistics") # Só assim é que me começou a funcionar, juro por deus que não percebo os  retardanços do windows com as paths
from GUI import GUI_V2
from Optimizer.baby_optimizer import HorOptimizer
from DB.db_handler import *

def parse_from_db_unload(data, db):
	parsed_order = []
	for order in data:
		parsed_order.append(UnloadOrder(order_type = "Unload", order_number = order[0], piece_type = order[6], 
										destination = order[7], quantity = order[8], db = db, unloaded = order[9], 
										state = order[5], already_in_db= True))
	return parsed_order

def parse_from_db_transformation(data, db):
	parsed_order = []
	for order in data:
		parsed_order.append(TransformOrder(order_type = "Transform", order_number = order[0], before_type = order[6], 
											after_type = order[7], quantity = order[8], max_delay = order[4], processed = order[9], 
											state = order[5], db = db, already_in_db= True))
	return parsed_order

def test_thread(optimizer):
	while True:
		#print(f'{optimizer.state.num_pieces} {optimizer.dispatch_queue}')
		time.sleep(1)

def compute_orders(optimizer, q_udp_in, pending_orders):
	print("Ordens pendentes: ", len(pending_orders))
	for o in pending_orders:
		if o.order_type == 'Transform':
			optimizer.order_handler(o)
			optimizer.optimize_all_pieces()
		elif o.order_type == 'Unload':
			optimizer.order_handler(o)
	
	while True:
#		print('Update orders')
		while not q_udp_in.empty():
			order = q_udp_in.get()
			for o in order:
				if o.order_type == 'Transform':
					optimizer.order_handler(o)
					optimizer.optimize_all_pieces()
				elif o.order_type == 'Unload':
					optimizer.order_handler(o)
			#optimizer.print_machine_schedule()

def update_dispatch(optimizer):
	while True:
#		print('Update dispatch')
		for machine in reversed(optimizer.state.machines.values()):
			#print(f'{machine}: {machine.op_list}')
			if machine.is_free and machine.op_list:
				next_op = machine.op_list[0]
				next_piece = next_op.piece_id
				if next_op.step == 1:
					if next_piece in optimizer.tracker.pieces_on_transit:
						print('WARNING: Piece has already been dispatched')
						machine.make_unavailable()
					else:
						optimizer.dispatch_queue.append(optimizer.state.pieces[next_piece])
						machine.make_unavailable()
				else:
					machine.make_unavailable()
		time.sleep(0.01)


def run(optimizer):
	loop = asyncio.new_event_loop()
	loop.run_until_complete(opc_client_run(optimizer, loop))
	loop.run_forever()
	loop.close()

if __name__ == "__main__":
	db = DB_handler()

	#fuck persistencia
	db.delete_all_content(['unload_orders', 'transform_orders'])

	optimizer = HorOptimizer()
	win = GUI_V2(db)

	# Para usar na persistencia, verifica se há ordens na base de dados que faltam processar
	pending_orders = []
	pending_orders.extend(parse_from_db_unload(db.select("unload_orders", where= { "curr_state" : "active", "curr_state" : "pending"}),db))
	pending_orders.extend(parse_from_db_transformation(db.select("transform_orders", where= { "curr_state" : "active", "curr_state" : "pending"}),db)) #, "curr_state" : "suspended"

	q_udp = Queue()		#	Exchanges information from order receiver to the next stage of the program
	t_order_rec = Thread(target = order_receive, args = (q_udp, db, True))
	t_order_rec.name = "Thread_client_receive"
	t_opc_run = Thread(target = run, args = (optimizer, ))
	t_opc_run.name = "Thread_opc_run"
	t_compute_orders = Thread(target=compute_orders, args=(optimizer, q_udp, pending_orders))
	t_compute_orders.name = "Thread_compute_order"
	t_update_dispatch = Thread(target=update_dispatch, args=(optimizer,))
	t_update_dispatch.name = "Thread_update_dispatch"
	t_test = Thread(target=test_thread, args=(optimizer,))
	t_test.name = "Test"

	threads = [t_order_rec, t_opc_run, t_compute_orders, t_update_dispatch]

	t_opc_run.start()
	t_order_rec.start()

	t_compute_orders.start()
	t_update_dispatch.start()

	# threads.append(t_test)
	# t_test.start()

	#win.open_GUI()

	## Joints all the threads
	map(lambda x:x.join(),threads)
