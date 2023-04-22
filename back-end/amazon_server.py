from ups_interact import *
from world_interact import *
import threading

def connect_ups_world(amazon_socket):
    while(1):
        ups_socket, addr = amazon_socket.accept()
        worldid = handle_UTAConnect(ups_socket)
        print("Create a thread to handle ups command")
        thread_handle_ups = threading.Thread(target = handle_UTACommands, args =(ups_socket,))
        thread_handle_ups.start()
        # keep connect to world until it success
        world_fd = 0
        while (True):
            fd, Connected, world_id_received = connectWorld(worldid)
            world_fd = fd
            if Connected:
                #listen on world
                print("Create a thread to handle world command")
                thread_handle_world = threading.Thread(target = handleWorldResponse, args =(world_fd))
                thread_handle_world.start()
                break
        if world_id_received != worldid:
            raise ValueError("The connect world id is not the world ups required for")
    
        send_ATUConnected(world_id_received, ups_socket)
        #listen on ups
        break
    thread_handle_world.join()
    thread_handle_ups.join()
    ups_socket.close()
    world_fd.close()      

def amazonStart():
    try:
        # TODO: pool or multithreading?
        init_engine()
        amazon_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        amazon_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # bind the socket to ups
        amazon_address = ('0.0.0.0', 32345)
        print('Server is listening on {}:{}'.format(*amazon_address))
        amazon_socket.bind(amazon_address)
        amazon_socket.listen(100)
        connect_ups_world(amazon_socket)

        # connect to front-end


        amazon_socket.close()
    except ValueError as err:
        print("Raise error: ", err.args)


if __name__ == '__main__':
    amazonStart()
