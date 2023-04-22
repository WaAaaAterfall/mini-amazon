from amazon_create_msg import *


'''Connect message'''

def send_ATUConnected(worldid, ups_socket):
    print("Connect to worldid: ", worldid)
    AUConnected = create_AUConnected(worldid)
    sendMessage(AUConnected, ups_socket)

def handle_UTAConnect(ups_socket):   
    connect_request = upb2.UTAConnect()
    received_connect = getMessage(ups_socket)
    connect_request.ParseFromString(received_connect)
    if (connect_request.HasField('worldid')):
        # connect to that world
        worldid = connect_request.worldid
        return worldid
    else: 
        raise ValueError("The first message should be the request from ups to connect to the same world")


'''Handle the commands from UPS'''

def handle_UTAArrived(UTAArrived, Session, ups_socket):
    session = Session()
    arrived_seqnum = UTAArrived.seqnum
    send_ackCommand(arrived_seqnum, ups_socket)

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
    # TODO: generate load message
    if order_to_load.status == 'packed':
        Acommand = create_ATWToload(order_to_load.warehouse_id, order_to_load.truck_id, order_to_load.package_id)
        addToWorld(Acommand)

def handle_UTAOutDelivery(UTAOutDelivery, Session, ups_socket):
    session = Session()
    out_del_seqnum = UTAOutDelivery.seqnum
    send_ackCommand(out_del_seqnum, ups_socket)

    package_id = UTAOutDelivery.packageid
    session.begin()
    order_to_deliver = session.query(Order).filter_by(Order.packageid == package_id).first()
    if order_to_deliver is None:
        raise ValueError("Cannot find order to deliver")
    order_to_deliver.status = 'OutForDelivery'
    session.commit()

def handle_UTADelivered(UTADelivered, Session, ups_socket):
    delivered_seqnum = UTADelivered.seqnum
    send_ackCommand(delivered_seqnum, ups_socket)
    session = Session()
    session.begin()
    package_id = UTADelivered.package_id
    delivered_order = session.query(Order).filter_by(Order.package_id == package_id).first()
    if delivered_order is None:
        raise ValueError("Cannot find delivered order")
    delivered_order.status = 'Delivered'
    session.commit()

def handle_AUErr(AUErr, ups_socket):
    err_seqnum = AUErr.seqnum
    send_ackCommand(err_seqnum, ups_socket)

    err_message = AUErr.err
    originseqnum = AUErr.originseqnum
    print("Error occurs at seqnum: ", originseqnum, "with error message: ", err_message)

def handle_ack(ack):
    if ack in toUps:
        toUps.pop(ack)
    else:
        raise ValueError("ack does not exist in ups queue")


def handle_UTACommands(ups_socket):
    while (True):
        UTACmd = upb2.UTACommands()
        # recv message from the world
        msg = getMessage(ups_socket)
        UTACmd.ParseFromString(msg)
        for err in UTACmd:
            handle_AUErr(err, ups_socket)

        for ack in UTACmd.acks:
            # check if ack in toWorld key and remove from to send
            handle_ack(ack)
        
        for arrive in UTACmd.arrive:
            handle_UTAArrived(arrive, Session, ups_socket)
        
        for to_deliver in UTACmd.todeliver:
            handle_UTAOutDelivery(to_deliver, Session, ups_socket)

        for delivered in UTACmd.delivered:
            handle_UTADelivered(delivered, Session, ups_socket)



