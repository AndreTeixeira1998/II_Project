import urllib.request
from html.parser import HTMLParser
import xml.etree.ElementTree as ET


#   Esta estrutura foi baseada diretamente na estrutura e dados dos ficheiros XML
#######################################################################################################
#
#   Order   ―>order_type
#       If order_type == Transform
#           ―>number
#           ―>transform     ―>quantity
#                           ―>before_type
#                           ―>after_type
#                           ―>max_delay
#
#       If order_type == Unload
#           ―>number
#           ―>unload    ―>quantity
#                       ―>piece_type
#                       ―>destination
#
#       If order_type == Request_Stores
#           (No additional attributes)
#
#######################################################################################################

# Tipos de ordem guardadas como integer
O_types = {
    "Transform" : 0,
    "Unload" : 1,
    "Request_Stores" : 2
}


class transform:
    def __init__(self, before_type, after_type, quantity, max_delay):
        self.before_type = before_type
        self.after_type = after_type
        self.quantity = quantity
        self.max_delay = max_delay


class unload:
    def __init__(self, piece_type, destination, quantity):
        self.piece_type = piece_type
        self.destination = destination
        self.quantity = quantity



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


class order:
    def __init__(self, order_number, order_type, max_delay = 0, **kwargs):
        self.order_type = order_type
        

        #   Deve ser possivel organizar os tipos de ordem num dicionario associado aos parametros de cada.
        #   Fica mais fácil de percorrer e mais elegante para ver
        if order_type == "Transform" and "transform" in kwargs:
            self.number = order_number
            self.transform = kwargs["transform"]

        elif order_type == "Unload" and "unload" in kwargs:
            self.number = order_number
            self.unload = kwargs["unload"]

        else:
            pass

        
    @staticmethod
    def parse(file_string):
        # Parses the uml into a structure
        root = ET.fromstring(file_string)

        # May receive several orders in the same file
        orders = []
        for ord in root:
            if ord.tag == "Order":
                # sei que é apenas um child que tem por order, mas não estou a ver como fazer sem for, estão à vontade de mudar se conseguirem
                for child in ord:
                    order_type = O_types[child.tag]
                    if order_type == O_types["Transform"]:
                        order_number = int(ord.attrib["Number"])
                        max_delay = int(child.get("MaxDelay"))
                        before_type = int(child.get("From")[1])
                        after_type = int(child.get("To")[1])
                        quantity = int(child.get("Quantity"))

                        trans = transform(max_delay = max_delay, before_type = before_type, after_type = after_type, quantity = quantity)
                        orders.append(order(order_number = order_number, order_type = order_type, transform = trans))

                    elif order_type == O_types["Unload"]:
                        order_number = int(ord.attrib["Number"])
                        piece_type = int(child.get("Type")[1])
                        destination = int(child.get("Destination")[1])
                        quantity = int(child.get("Quantity"))

                        unl = unload(quantity = quantity, piece_type = piece_type, destination = destination) 
                        orders.append(order(order_number = order_number, order_type = order_type, unload = unl))

                    elif order_type == O_types["Request_Stores"]:
                        orders.append(order(order_number = order_number, order_type = order_type))

                    else:
                        print("Error creating order (No such order type as %s)" % order_type)
            elif ord.tag == "Request_Stores":
                order_type = O_types[ord.tag]
                orders.append(order(order_number = 0, order_type = order_type))
        return orders

    @staticmethod
    def order66():
        page = urllib.request.urlopen('https://www.imsdb.com/scripts/Star-Wars-Revenge-of-the-Sith.html').read()
        data = strip_tags(page.decode("cp1252"))
        print(data[2000:len(data)-348]) 
        return data[2000:len(data)-348] 

