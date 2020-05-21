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


check_stock = True
def order_scheduling(optimizer, q_udp_in, pending_orders, q_orders):
	orders_received = []
	orders_to_schedule = []
	orders_wait_stock = []
	orders_scheduled = []

	if pending_orders:
		for idx, order in enumerate(pending_orders):
			orders_received.append(order)
		pending_orders.clear()

	while True:
		# Orders received from UDP
		while not q_udp_in.empty():
			order = q_udp_in.get()
			for o in order:
				orders_received.append(o)

		# Orders waiting for restock
		if orders_wait_stock:
			idx2remove = []
			for idx, order in enumerate(orders_wait_stock):
				if check_stock:
					orders_to_schedule.append(order)
					idx2remove.append(idx)
				else:
					continue
			for idx in idx2remove:
				orders_wait_stock.pop(idx)

		# Check if warehouse has enough pieces for each order
		if orders_received:
			for idx, order in enumerate(orders_received):
				if check_stock:
					orders_to_schedule.append(order)
					#orders_received.pop(idx)
				else:
					orders_wait_stock.append()
					#orders_received.pop(idx)
			orders_received.clear()

		# Schedule orders that can be complete
		if orders_to_schedule:
			for idx, order in enumerate(orders_to_schedule):
				if isinstance(order, TransformOrder):
					max_delay = order.max_delay
					#order._db = None
					sim_order = TransformOrder(order.order_type, order.order_number, order.before_type,
											   order.after_type, order.quantity, order.max_delay, state = "pending",
											   processed = order.processed, on_factory = order.on_factory)
					_, cost = optimizer.simulate(sim_order)
					cost = 0
					priority = max_delay - cost
				else:
					priority = -9999999

				orders_scheduled.append((priority, order))
			orders_to_schedule.clear()
			orders_scheduled.sort(key=lambda order: order[0])

			print('## schedule ##')
			for priority, order in orders_scheduled:
				print(f'{order.order_number}: {priority}')
				q_orders.put(order)
			print('## end ##')

		for _, order in orders_scheduled:
			print(f'Optimizing order {order.order_number}')
			optimizer.order_handler(order)
			optimizer.optimize_single_order(order)
			print(f'Optimization complete')
		orders_scheduled.clear()



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
	#db.delete_all_content(['unload_orders', 'transform_orders'])

	optimizer = HorOptimizer()
	win = GUI_V2(db)

	Order._db = db

	# Para usar na persistencia, verifica se há ordens na base de dados que faltam processar
	pending_orders = []
	pending_orders.extend(parse_from_db_unload(db.select("unload_orders", where= { "curr_state" : "pending", "curr_state1" : "active"}, operand='OR'),db))
	print('ordens pendentes unload:' + str(len(pending_orders)))
	pending_orders.extend(parse_from_db_transformation(db.select("transform_orders", where= { "curr_state" : "pending", "curr_state1" : "active"}, operand='OR'),db)) #, "curr_state" : "suspended"
	print('ordens pendentes transform + unload:' + str(len(pending_orders)))

	q_udp = Queue()		#	Exchanges information from order receiver to the next stage of the program
	t_order_rec = Thread(target = order_receive, args = (q_udp, True))
	t_order_rec.name = "Thread_client_receive"
	t_opc_run = Thread(target = run, args = (optimizer, ))
	t_opc_run.name = "Thread_opc_run"

	#t_compute_orders = Thread(target=compute_orders, args=(optimizer, q_udp, pending_orders))
	#t_compute_orders.name = "Thread_compute_order"

	q_orders = Queue()
	t_order_scheduling = Thread(target=order_scheduling, args=(optimizer, q_udp, pending_orders, q_orders))
	t_order_scheduling.name = "Thread_order_scheduling"

	t_update_dispatch = Thread(target=update_dispatch, args=(optimizer,))
	t_update_dispatch.name = "Thread_update_dispatch"

	#t_optimize = Thread(target=optimize_stuff, args=(optimizer,q_orders))
	#t_optimize.name = "Thread_optimize"

	t_test = Thread(target=test_thread, args=(optimizer,))
	t_test.name = "Test"

	threads = [t_order_rec, t_opc_run, t_order_scheduling, t_update_dispatch] #, t_optimize]

	t_opc_run.start()
	t_order_rec.start()
	#t_optimize.start()

	#t_compute_orders.start()
	t_update_dispatch.start()
	t_order_scheduling.start()

	# threads.append(t_test)
	# t_test.start()

	#win.open_GUI()

	## Joints all the threads
	map(lambda x:x.join(),threads)
