from Order import order
from socket import socket, timeout, AF_INET, SOCK_DGRAM
from threading import Thread
from queue import Queue

host = "127.0.0.1"
port = 54321
buf = 1024
addr = (host,port)

def order_receive(out_q):
    s = socket(AF_INET,SOCK_DGRAM)
    s.bind((host,port))

    while True:
        data,addr = s.recvfrom(buf)
        received_orders = order.parse(data)
        out_q.put(received_orders)

def Communication_thread_example(in_q):
    while True:
        # Recebe a informação colocada na queue de comunicação entre threads. 
        # Esta queue terá que ser declarada na main, ou noutra região onde deverão ser chamadas as duas funções que terão que comunicar
        orders = in_q.get()
        for ord in orders:
            print("Data received: ", ord.order_type)

# Apenas um exemplo de comunicação entre threads
def run_example():
    q = Queue()

    t_order_rec = Thread(target = order_receive, args = (q, ))
    t_Communication_thread_example = Thread(target = Communication_thread_example, args = (q, ))
    t_order_rec.start()
    t_Communication_thread_example.start()