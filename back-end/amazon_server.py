from ups_interact import *
from world_interact import *
from web_interact import *
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
        print('Connected to', ups_address)
        break

    thread_send_ups = threading.Thread(target = sendToUPS, args =(atu_socket,))
    thread_send_ups.start()
    thread_send_world = threading.Thread(target = sendToWorld, args =(world_fd,))
    thread_send_world.start()
    
    thread_handle_world.join()
    thread_handle_ups.join()
    thread_send_world.join()
    thread_send_ups.join()

    world_fd.close()      

def accept_web(amazon_socket, amazon_address):
    print('Server is listening on {}:{}'.format(*amazon_address))
    amazon_socket.bind(amazon_address)
    amazon_socket.listen(100)
    web_socket, addr = amazon_socket.accept()
    return web_socket


def process_order(web_fd,session):
    while(True):
        msg = web_fd.recv(1024)
        id = msg.decode()
        if not msg:
            continue
        session.begin()
        order = session.query(Order).filter_by(package_id=id).first()
        nearst_whid = findWarehouse(order.addr_x, order.addr_y,session)
        # update order to inclue warehouse id
        order.warehouse_id = nearst_whid
        if check_inventory_availability(order.warehouse_id, order.product_id, order.count) == False:
            
        session.commit()
        

def amazonStart():
    #Port for world: connect to 23456
    #Port for ups: connect to 32345
    #Port for web: listen on 54321
    try:
        # TODO: pool or multithreading?
        init_engine()
        amazon_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        amazon_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        amazon_address = ('0.0.0.0', 54321)
        # connect to front-end
        web_socket = accept_web(amazon_socket, amazon_address)
        thread_handle_web = threading.Thread(target = handle_web_query, args =(web_socket,))
        thread_handle_web.start()

        # connect to ups
        atu_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        atu_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        ups_address = ('0.0.0.0', 32345)
        connect_ups_world(atu_socket, ups_address)

        thread_handle_web.join()

        atu_socket.close()
        amazon_socket.close()
    except ValueError as err:
        print("Raise error: ", err.args)


if __name__ == '__main__':
    amazonStart()
