from ups_interact import *
from world_interact import *
import threading

def connect_ups_world(atu_socket, ups_address):
    while(1):
        atu_socket.connect(ups_address)
        worldid = handle_UTAConnect(atu_socket)
        print("Create a thread to handle ups command")
        thread_handle_ups = threading.Thread(target = handle_UTACommands, args =(atu_socket,))
        thread_handle_ups.start()
        # keep connect to world until it success
        # Create an empty dictionary to store warehouse information
        warehouse_dict = {}
        # Add a warehouse to the dictionary
        warehouse_dict[1] = {'x': 20, 'y': 20}
        warehouse_dict[2] = {'x': 300, 'y': 300}
        world_fd = 0
        while (True):
            fd, Connected, world_id_received = connectWorld(warehouse_dict)
            world_fd = fd
            if Connected:
                #listen on world
                break
        print("Create a thread to handle world command")
        thread_handle_world = threading.Thread(target = handleWorldResponse, args =(world_fd,))
        thread_handle_world.start()
        if world_id_received != worldid:
            raise ValueError("The connect world id is not the world ups required for")
        send_ATUConnected(world_id_received, atu_socket)
        break

    thread_send_ups = threading.Thread(target = sendToUPS, args =(atu_socket,))
    thread_send_ups.start()
    thread_send_world = threading.Thread(target = sendToWorld, args =(world_fd,))
    thread_send_world.start()
    
    thread_handle_world.join()
    thread_handle_ups.join()
    thread_send_world.join()
    thread_send_ups.join()

    atu_socket.close()
    world_fd.close()      

def amazonStart():
    #Port for world: connect to 23456
    #Port for ups: connect to 32345
    #Port for web: listen on 54321
    try:
        # TODO: pool or multithreading?
        init_engine()
        amazon_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        amazon_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # connect to front-end
        # amazon_address = ('0.0.0.0', 32345)
        # print('Server is listening on {}:{}'.format(*amazon_address))
        # amazon_socket.bind(amazon_address)
        # amazon_socket.listen(100)
        #connect_web(amazon_socket)

        # connect to ups
        atu_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        atu_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        ups_address = ('0.0.0.0', 32345)
        connect_ups_world(atu_socket, ups_address)
        print('Connected to', ups_address)

        amazon_socket.close()
    except ValueError as err:
        print("Raise error: ", err.args)


if __name__ == '__main__':
    amazonStart()
