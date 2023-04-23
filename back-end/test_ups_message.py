import socket
from amazon_create_msg import *
from ups_interact import *
from world_interact import *

# def addOrderToDB():

# def test_UTAArrived():

# def test_UTAOutDelivery():

# def test_UTADelivered():

def generate_UTAConnect(worldid):
    UTAConnect = upb2.UTAConnect()
    UTAConnect.worldid = worldid
    return UTAConnect   

def ups_send_rec_connect():
    # create a TCP socket
    ups_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ups_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    WORLD_ID = 4
    # connect the socket to a specific address and port
    ups_address = ('localhost', 32345)
    print('Server is listening on {}:{}'.format(*ups_address))
    ups_socket.bind(ups_address)
    ups_socket.listen(100)
    amazon_socket, addr = ups_socket.accept()
    request = generate_UTAConnect(WORLD_ID)
    sendMessage(request, amazon_socket)
    print("Request sent to amazon: ", request)
    # receive data from server
    response = getMessage(amazon_socket)
    connected_response = upb2.AUConnected()
    connected_response.ParseFromString(response)
    if (connected_response.HasField('worldid')):
        # connect to that world
        print("The amazon has connected with world: ", connected_response.worldid)
    else: 
        raise ValueError("Amazon does not connenct to the right world")
    # close the connection
    return amazon_socket
    
    #ups_socket.close()

if __name__ == '__main__':
    amazon_socket = ups_send_rec_connect()
    
    print()