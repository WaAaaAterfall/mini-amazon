from amazon_server import *

def addOrderToDB():
    session = Session()
    session.begin()
    new_order = {}
    new_order[1] = Order(package_id = 3, count = 10, status = 'Processing', 
                         addr_x = 30, addr_y = 25, product_id = 2)
    new_order[2] = Order(package_id = 5, count = 15, status = 'Processing', 
                         addr_x = 30, addr_y = 25, product_id = 2)
    new_order[3] = Order(package_id = 1, count = 20, status = 'Processing', 
                         addr_x = 300, addr_y = 250, product_id = 1)
    new_order[4] = Order(package_id = 2, count = 30, status = 'Processing', 
                         addr_x = 300, addr_y = 250, product_id = 1)
    print(new_order)
    for key, order in new_order.items():
        session.add(order)
        session.commit()
    session.close()    

    
if __name__ == '__main__':
    web_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    web_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    amazon_address = ('0.0.0.0', 13145)
    web_socket.connect(amazon_address)
    addOrderToDB()
    print("send package 3 to amazon")
    web_socket.sendall(str(3).encode('utf8'))
    print("send package 5 to amazon")
    web_socket.sendall(str(5).encode('utf8'))
    print("send package 1 to amaozn")
    web_socket.sendall(str(1).encode('utf8'))
    print("send package 2 to amaozn")
    web_socket.sendall(str(2).encode('utf8'))

