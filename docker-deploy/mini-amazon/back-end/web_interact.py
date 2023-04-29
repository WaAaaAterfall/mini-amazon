from db_table import *
from utils import *
from db_connect import *
from amazon_create_msg import *
PORT = 13145

# '''
# @findWarehouse: given the order address x,y find the nearst warehouse and update order warehouse
# @Return:   the neareast warehouse id
# ''' 

def check_inventory_availability(warehouse_id, product_id, request_count):
    session = Session()
    request_inventory = session.query(Inventory).filter(Inventory.warehouse_id == warehouse_id,
                                                           Inventory.product_id == product_id)
    total_count = 0
    for inventory in request_inventory:
        total_count += inventory.remain_count
    if request_count <= total_count:
        print("!!!!!!!!!!!!!!!!!!!!The inventory for ", product_id, " is ", total_count)
        return True
    else:
        return False

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




