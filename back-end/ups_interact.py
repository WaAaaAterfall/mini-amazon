from db_table import *
from utils import *

import ups_amazon_pb2 as pb2


'''Handle the commands from UPS'''

def handle_UTADelivered(UTADelivered, session):
    session.begin()
    package_id = UTADelivered.package_id
    delivered_order = session.query(Order).filter_by(Order.package_id == package_id).first()
    if delivered_order is None:
        raise ValueError("Cannot find delivered order")
    delivered_order.status = 'Delivered'
    session.commit()

def handle_UTAArrived(UTAArrived, session):
    arrived_seqnum = UTAArrived.seqnum
    ack_command = create_ackCommand(arrived_seqnum)
    addToWorld(ack_command)

    package_id = UTAArrived.packageid
    truck_id = UTAArrived.truckid
    wh_id = UTAArrived.whid
    session.begin()
    order_to_load = session.query(Order).filter_by(Order.packageid == package_id,
                                                   Order.warehouse_id == wh_id).first()
    if order_to_load is None:
        raise ValueError("Cannot find find the order to load")
    order_to_load.truck_id = truck_id
    session.commit()



def handle_UTAOutDelivery(UTAOutDelivery, session):

def handle_AUErr(AUErr, sesison):

def handle_acks(acks):

def handle_UTACommands(ups_socket):
    session = Session()
    while

def handle_UTAConnect(received_connect):   
    connect_request = pb2.UTAConnect()
    connect_request.ParseFromString(received_connect)
    if (connect_request.HasField('worldid')):
        # connect to that world
        worldid = connect_request.worldid
        return worldid
    else: 
        raise ValueError("The first message should be the request from ups to connect to the same world")


