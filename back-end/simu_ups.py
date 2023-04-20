import socket
from db_table import *
from utils import *

import ups_amazon_pb2 as pb2

def generate_UTAConnect(worldid):
    UTAConnect = pb2.UTAConnect()
    UTAConnect.worldid = worldid
    return UTAConnect   

def ups_send_connect():
    # create a TCP socket
    ups_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ups_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # connect the socket to a specific address and port
    amazon_address = ('localhost', 32345)
    ups_socket.connect(amazon_address)
    print('Connected to', amazon_address)
    request = generate_UTAConnect(1)
    sendMessage(request, ups_socket)
    print("Request sent: ", request)
    # receive data from server
    response = getMessage(ups_socket)
    connected_response = pb2.AUConnected()
    connected_response.ParseFromString(response)
    if (connected_response.HasField('worldid')):
        # connect to that world
        print("The amazon has connected with world: ", connected_response.worldid)
    else: 
        raise ValueError("Amazon does not connenct to the right world")
    # close the connection
    ups_socket.close()

if __name__ == '__main__':
    ups_send_connect()
    print()