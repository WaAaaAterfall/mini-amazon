from db_table import *
from utils import *

import ups_amazon_pb2 as pb2

def generage_AUConnected(worldid):
    AUConnected = pb2.AUConnected()
    AUConnected.worldid = worldid
    return AUConnected

def generate_ATUCommands():
    ATUCmd = pb2.AUTCommands()

def generate_AUErr(error, originseqnum, seqnum):
    AUErr = pb2.AUErr()
    AUErr.err = error
    AUErr.originseqnum = originseqnum
    AUErr.seqnum = seqnum
    return AUErr

# def generate_ATULoaded():

# def generate_ATURequestPickup():

def handle_UTADelivered(UTADelivered, session):
    session.begin()
    package_id = UTADelivered.package_id
    delivered_order = session.query(Order).filter_by(Order.package_id == package_id).first()
    if delivered_order is None:
        raise ValueError(
            "Cannot find delivered order")
    delivered_order.status = 'Delivered'
    session.commit()

# def handle_UTACommands(ups_socket):
#     session = Session()
#     session.begin()

def handle_upsConnect(received_connect):   
    connect_request = pb2.UTAConnect()
    connect_request.ParseFromString(received_connect)
    if (connect_request.HasField('worldid')):
        # connect to that world
        worldid =connect_request.worldid
    else: 
        raise ValueError("The first message should be the request from ups to connect to the same world")


def handle_ups(ups_socket):
    received_connect = getMessage(ups_socket)
    handle_upsConnect(received_connect)
    AUConnected = generage_AUConnected()
    sendMessage(ups_socket, AUConnected)

