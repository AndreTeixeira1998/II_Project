import urllib.request
from html.parser import HTMLParser
import xml.etree.ElementTree as ET
from datetime import datetime

#######################################################################################################
#
#   Order   
#       Transform
#           ―>order_type
#           ―>time
#           ―>number
#           ―>quantity
#           ―>before_type
#           ―>after_type
#           ―>max_delay
#
#       Unload
#           ―>order_type
#           ―>time
#           ―>number
#           ―>quantity
#           ―>piece_type
#           ―>destination
#
#       Request_Stores
#           ―>order_type
#           ―>time
# 
#       Para obter um atributo basta colocar:
#   
#           orderx.get("Nome do atributo") ―> ex: orderx.get("quantity")
#       (Caso não exista esse tipo de atributo, retorna None)
#
#
#       Para verificar o tipo de ordem há duas maneiras:
#
#           isinstance(orderx,  nome da classe) ―> ex: isinstance(orderx,  Transform) 
#           orderx.get("order_type") == "nome da classe" ―> ex: orderx.get("order_type") == "Transform"
#
#######################################################################################################


class MLStripper(HTMLParser):
    def __init__(self):
        super().__init__()
        self.reset()
        self.fed = []
    def handle_data(self, d):
        self.fed.append(d)
    def get_data(self):
        return ''.join(self.fed)

def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()


class Order:
    def __init__(self, order_type, max_delay = 0):
        self.order_type = order_type
        self.time = datetime.now()


    @staticmethod
    def order66():
        page = urllib.request.urlopen('https://www.imsdb.com/scripts/Star-Wars-Revenge-of-the-Sith.html').read()
        data = strip_tags(page.decode("cp1252"))
        print(data[2000:len(data)-348])
        return data[2000:len(data)-348]

class Transform(Order):
    def __init__(self, order_type, order_number, before_type, after_type, quantity, max_delay):
        super(Transform, self).__init__(order_type)
        self.order_number = order_number
        self.before_type = before_type
        self.after_type = after_type
        self.quantity = quantity
        self.max_delay = max_delay
    
    def get(self, attribute):
        if attribute == "order_type":
            return self.order_type
        elif attribute in "order_number":
            return self.order_number
        elif attribute == "quantity":
            return self.quantity
        elif attribute == "before_type":
            return self.before_type
        elif attribute == "after_type":
            return self.after_type
        elif attribute == "max_delay":
            return self.max_delay
        else:
            return None



        
class Unload(Order):
    def __init__(self, order_type, order_number, piece_type, destination, quantity):
        super(Unload, self).__init__(order_type)
        self.order_number = order_number
        self.piece_type = piece_type
        self.destination = destination
        self.quantity = quantity

    def get(self, attribute):
        if attribute == "order_type":
            return self.order_type
        elif attribute in "order_number":
            return self.order_number
        elif attribute == "quantity":
            return self.quantity
        elif attribute == "piece_type":
            return self.piece_type
        elif attribute == "destination":
            return self.destination
        else:
            return None

class Request_Stores(Order):
    def __init__(self, order_type):
        super(Request_Stores, self).__init__(order_type)
    
    def get(self, attribute):
        if attribute == "order_type":
            return self.order_type
        else:
            return None


def parse(file_string):
    # Parses the uml into a structure
    root = ET.fromstring(file_string)
    # May receive several orders in the same file
    orders = []
    for ord in root:
        if ord.tag == "Order":
            # sei que é apenas um child que tem por order, mas não estou a ver como fazer sem for, estão à vontade de mudar se conseguirem
            for child in ord:
                order_type = child.tag
                if order_type == "Transform":
                    order_number = int(ord.attrib["Number"])
                    max_delay = int(child.get("MaxDelay"))
                    before_type = child.get("From")
                    after_type = child.get("To")
                    quantity = int(child.get("Quantity"))
                    orders.append(Transform(order_type = order_type, order_number = order_number, 
                                    max_delay = max_delay, before_type = before_type, after_type = after_type, quantity = quantity))
                elif order_type == "Unload":
                    order_number = int(ord.attrib["Number"])
                    piece_type = child.get("Type")[1]
                    destination = child.get("Destination")
                    quantity = int(child.get("Quantity"))
                    orders.append(Unload(order_number = order_number, order_type = order_type,
                                    quantity = quantity, piece_type = piece_type, destination = destination))
                else:
                    print("Error creating order (No such order type as %s)" % order_type)
        elif ord.tag == "Request_Stores":
            order_type = ord.tag
            orders.append(Request_Stores(order_type = order_type))
    return orders
