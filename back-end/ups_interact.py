from amazon_create_msg import *

'''Handle the commands from UPS'''

def handle_UTAArrived(UTAArrived, Session):
    session = Session()
    arrived_seqnum = UTAArrived.seqnum
    ack_command = create_ackCommand(arrived_seqnum)
    addToUps(ack_command)

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

def handle_UTAOutDelivery(UTAOutDelivery, Session):
    session = Session()
    out_del_seqnum = UTAOutDelivery.seqnum
    ack_command = create_ackCommand(out_del_seqnum)
    addToUps(ack_command)

    package_id = UTAOutDelivery.packageid
    session.begin()
    order_to_deliver = session.query(Order).filter_by(Order.packageid == package_id).first()
    if order_to_deliver is None:
        raise ValueError("Cannot find order to deliver")
    order_to_deliver.status = 'OutForDelivery'
    session.commit()

def handle_UTADelivered(UTADelivered, Session):
    session = Session()
    session.begin()
    package_id = UTADelivered.package_id
    delivered_order = session.query(Order).filter_by(Order.package_id == package_id).first()
    if delivered_order is None:
        raise ValueError("Cannot find delivered order")
    delivered_order.status = 'Delivered'
    session.commit()

def handle_AUErr(AUErr, Sesison):
    err_seqnum = AUErr.seqnum
    ack_command = create_ackCommand(err_seqnum)
    addToUps(ack_command)

    err_message = AUErr.err
    originseqnum = AUErr.originseqnum
    print("Error occurs at seqnum: ", originseqnum, "with error message: ", err_message)

def handle_ack(ack):
    if ack in toUps:
        toUps.pop(ack)
    else:
        raise ValueError("ack does not exist in ups queue")


def handle_UTACommands(ups_socket):
    while (1):
        UTACmd = upb2.UTACommands()
        # recv message from the world
        msg = getMessage(ups_socket)
        UTACmd.ParseFromString(msg)
        for err in UTACmd:
            handle_AUErr(err, Session)

        for ack in UTACmd.acks:
            # check if ack in toWorld key and remove from to send
            handle_ack(ack)
        
        for arrive in UTACmd.arrive:
            handle_UTAArrived(arrive, Session)
        
        for to_deliver in UTACmd.todeliver:
            handle_UTAOutDelivery(to_deliver, Session)

        for delivered in UTACmd.delivered:
            handle_UTADelivered(delivered, Session)


def handle_UTAConnect(received_connect):   
    connect_request = upb2.UTAConnect()
    connect_request.ParseFromString(received_connect)
    if (connect_request.HasField('worldid')):
        # connect to that world
        worldid = connect_request.worldid
        return worldid
    else: 
        raise ValueError("The first message should be the request from ups to connect to the same world")


