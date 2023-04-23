from ups_interact import *
from world_interact import *
from web_interact import *


def define_warehouse_product():
    warehouse_dict = {}
    warehouse_dict[1] = {'x': 20, 'y': 20}
    warehouse_dict[2] = {'x': 300, 'y': 300}
    product_dict = {}
    product_dict[1] = "This is a huge assignment you wrote in ece551"
    product_dict[2] = "This is also a huge assignment from DUKE ECE"

    return warehouse_dict, product_dict


def config_db(warehouse_dict, product_dict, world_id_received):
    session = Session()
    session.begin()
    for warehouse_id, warehouse_info in warehouse_dict.items():
        new_warehose = Warehouse(id = warehouse_id, world_id = world_id_received, x = warehouse_info['x'], y = warehouse_info['y'])
        session.add(new_warehose)
        session.commit()
    for product_id, product_desc in product_dict.items():
        new_product = Product(id = product_id, description = product_desc)
        session.add(new_product)
        session.commit()
    session.close()


def connect_ups_world(atu_socket, ups_address):
    while(1):
        atu_socket.connect(ups_address)
        worldid = handle_UTAConnect(atu_socket)
        print("Create a thread to handle ups command")
        thread_handle_ups = threading.Thread(target = handle_UTACommands, args =(atu_socket,))
        thread_handle_ups.start()

        #define warehouse and product in the world
        warehouse_dict, product_dict = define_warehouse_product()
        world_fd = 0
        while (True):
            fd, Connected, world_id_received = connectWorld(warehouse_dict)
            config_db(warehouse_dict, product_dict, world_id_received)
            world_fd = fd
            if Connected:
                #listen on world
                break
        print("Create a thread to handle world command")
        thread_handle_world = threading.Thread(target = handleWorldResponse, args =(world_fd,))
        thread_handle_world.start()
        #not to debug, uncomment those lines
        # if world_id_received != worldid:
        #     print(world_id_received)
        #     raise ValueError("The connect world id is not the world ups required for")
        send_ATUConnected(world_id_received, atu_socket)
        print('Connected to', ups_address)
        break

    print("Connection to ups and world should finish, creat thread to handle function")
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


def process_order(web_fd):
    session = Session()
    while(True):
        msg = web_fd.recv(1024)
        package_id = msg.decode()
        if not msg:
            continue
        session.begin()
        order = session.query(Order).join(Product).filter(package_id==Order.package_id, 
                                                        Order.product_id==Product.id).first()
        if order is None:
            raise ValueError("Cannot find the order sent from front end")
        nearst_whid = findWarehouse(order.addr_x, order.addr_y,session)
        # update order to inclue warehouse id
        order.warehouse_id = nearst_whid
        session.commit()     
        x = order.addr_x
        y = order.addr_y
        #TODO: UPSACCOUNT??????
        ups_account = None
        if check_inventory_availability(nearst_whid, order.product_id, order.request_count) == False:
            product_id = order.product_id
            description = order.product.descriotion
            count = order.count
            purchase_command = create_ATWPurchase(nearst_whid, product_id, description, count)
            addToWorld(purchase_command)
        #Keep checking if the order is available
        #TODO: Create another thread?    
        while check_inventory_availability(nearst_whid, order.product_id, order.request_count) == False:
            continue
        requestPickUp_command = create_ATURequestPickup(description, package_id, ups_account, nearst_whid, x, y)
        addToUps(requestPickUp_command)
        session.close()


def amazonStart():
    #Port for world: connect to 23456
    #Port for ups: connect to 32345
    #Port for web: listen on 13145
    try:
        init_engine()
        # amazon_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # amazon_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # amazon_address = ('0.0.0.0', 13145)
        # # connect to front-end
        # print("Connect to front-end, create a thread to process order")
        # web_socket = accept_web(amazon_socket, amazon_address)
        # thread_handle_web = threading.Thread(target = process_order, args =(web_socket,))
        # thread_handle_web.start()

        # connect to ups
        atu_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        atu_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        ups_address = ('0.0.0.0', 32345)
        connect_ups_world(atu_socket, ups_address)

        #thread_handle_web.join()

        atu_socket.close()
        #amazon_socket.close()
    except ValueError as err:
        print("Raise error: ", err.args)


if __name__ == '__main__':
    amazonStart()
