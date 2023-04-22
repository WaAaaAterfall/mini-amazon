from db_table import *
from utils import *
from db_connect import *
PORT = 13145

# '''
# @findWarehouse: given the order address x,y find the nearst warehouse and update order warehouse
# @Return:   the neareast warehouse id
# ''' 
def findWarehouse(addr_x, addr_y,session):
    min_distance = float('inf')
    # iterate all warehouse
    warehouses = session.query(Warehouse).all()
    nearst_whid = 0
    for warehouse in warehouses:
        x = warehouse.x
        y = warehouse.y
        distance = (x - addr_x)**2 + (y - addr_y)**2
        if distance < min_distance:
            min_distance = distance
            nearst_whid = warehouse.id
    return nearst_whid




def handle_web(web_fd,session):
    while(True):
        msg = web_fd.recv(1024)
        data = msg.decode()
        if not data:
            continue
        id = data
        order = session.query(Order).filter_by(package_id=id).first()
        nearst_whid = findWarehouse(order.addr_x, order.addr_y,session)
        # update order to inclue warehouse id
        session.query(Order).filter_by(package_id = id ).update({"warehouse_id" : nearst_whid})
        session.commit()

if __name__ == '__main__':
    engine = connectDB()
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(('localhost', PORT))
    sock.listen(100)
    web_fd, addr = sock.accept()
    session = getSession(engine)
    handle_web(web_fd,session)





