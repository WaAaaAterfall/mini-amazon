from db_table import *
from utils import *

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
        y = warehouses.y
        distance = (x - addr_x)**2 + (y - addr_y)**2
        if distance < min_distance:
            min_distance = distance
            nearst_whid = warehouse.id
    return nearst_whid




def handle_web(web_fd,session):
    while(True):
        id = web_fd.recv(4)
        order = Session.query(Order).filter_by(package_id=id).first()
        nearst_whid = findWarehouse(order.addr_x, order.addr_y,session)
        # update order to inclue warehouse id
        session.query(Order).filter_by(package_id= id ).update({"warehouse_id" : nearst_whid})
        session.commit()




