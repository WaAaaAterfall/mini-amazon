import socket
from utils import *
from multiprocessing import Pool
#from world_interact import *
from ups_interact import *
PROCESS_NUM = 3


def connect_ups(amazon_socket):
    socket_list = list()
    while(1):
        ups_socket, addr = amazon_socket.accept()
        socket_list.append(ups_socket)
        if len(socket_list) > 0:
            current_ups_socket = socket_list.pop(0)
            # TODO: need to use multiprocessing to handle different ups, write later
            handle_ups(current_ups_socket)
            ups_socket.close()

# def connect_world():
#     world_server_address = ('0.0.0.0', 12345)
#     amazon_socket.connect(world_server_address)
#     print('Connected to', world_server_address)
#     handle_world_request()

def initializer():
    """ensure the parent proc's database connections are not touched
    in the new connection pool"""
    engine.dispose(close=False)


def amazonStart():
    # TODO: pool or multithreading?
   # pool = Pool(PROCESS_NUM, initializer=initializer)
    init_engine()
    amazon_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    amazon_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # bind the socket to ups
    #TODO: What is the port number for ups?
    amazon_address = ('0.0.0.0', 32345)
    print('Server is listening on {}:{}'.format(*amazon_address))
    amazon_socket.bind(amazon_address)
    amazon_socket.listen(100)
    #pool.apply_async(func=connect_ups, args=(amazon_socket,))
    connect_ups(amazon_socket)
    # connect to front-end
    amazon_socket.close()

if __name__ == '__main__':
    amazonStart()
