from Order import Order, Transform, Unload, Request_Stores, parse
from socket import socket, timeout, AF_INET, SOCK_DGRAM
from threading import Thread
from queue import Queue
	

host = "127.0.0.1"
port = 54321
buf = 1024
addr = (host,port)

def order_receive(out_q, notify_new_order = False):
	s = socket(AF_INET,SOCK_DGRAM)
	s.bind((host,port))

	while True:
		data,_ = s.recvfrom(buf)
		received_orders = parse(data)
		out_q.put(received_orders)
		if notify_new_order == True:
			for ord in received_orders:
				print("Data received: ", ord.get("order_type"))

def _Communication_thread_example(in_q):
	orders = []
	while True:
		# Recebe a informação colocada na queue de comunicação entre threads. 
		# Esta queue terá que ser declarada na main, ou noutra região onde deverão ser chamadas as duas funções que terão que comunicar

		while not in_q.empty():
			ord = in_q.get()
			for o in ord:
				orders.append(o)
		for o in orders:
			print(o.get("order_type"))
		time.sleep(15) # Simula o tempo de execução de um outro processo
        


# Apenas um exemplo de comunicação entre threads
def _run_example():
	q = Queue()
    
	t_order_rec = Thread(target = order_receive, args = (q, ))
	t_Communication_thread_example = Thread(target = _Communication_thread_example, args = (q, ))
	t_order_rec.start()
	t_Communication_thread_example.start()
    
if __name__ == "__main__":
	import time
	_run_example()
