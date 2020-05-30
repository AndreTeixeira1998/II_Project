from Receive_client_orders.Order import Order, TransformOrder, UnloadOrder, Request_StoresOrder, parse
from socket import socket, timeout, AF_INET, SOCK_DGRAM
from threading import Thread
from queue import Queue
	

host = "172.29.0.50"
port = 54321
buf = 2048
addr = (host,port)


def answer_request(request):
	s = socket(AF_INET, # Internet
                SOCK_DGRAM) # UDP
	
	message = request.create_xml()
	# bytesToSend = str.encode(message)  #	Não deve ser preciso, já deve estar em binário
	s.sendto(message,(request.get("address"),request.get("port")))
	print(request.get("address") , " : " , request.get("port"), " Message: ", message)

	

def order_receive(out_q, notify_new_order = False):
	s = socket(AF_INET,SOCK_DGRAM)
	s.bind((host,port))

	while True:
		data,addr_port = s.recvfrom(buf)
		received_orders = parse(data, addr_port[0], addr_port[1])
		for index,rec in enumerate(received_orders):
			if rec.get("order_type") == "Request_Stores":
				#if notify_new_order == True:
				#	print("Send to", rec.get("address"), rec.get("port"))
				answer_request(rec)
				del received_orders[index]

		out_q.put(received_orders)
		if notify_new_order == True:
			for ord in received_orders:
				pass
				#print("Data received: ", ord.get("order_type"))

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
    
	db = DB_handler()
	Order.db = db

	t_order_rec = Thread(target = order_receive, args = (q,  ))
	t_Communication_thread_example = Thread(target = _Communication_thread_example, args = (q, ))
	t_order_rec.start()
	t_Communication_thread_example.start()
    
if __name__ == "__main__":
	import time
	from Order import Order, TransformOrder, UnloadOrder, Request_StoresOrder, parse
	
	import sys
	sys.path.insert(0, "..")
	sys.path.insert(0, "DB")
	from db_handler import DB_handler
	_run_example()
