from amazon_create_msg import *

'''send error and raise erorr message'''

def atu_send_raise_error(error_message, seqnum):
    error = error_message
    AUErr = create_AUErr(error, seqnum)
    addToUps(AUErr)
    #raise ValueError(error)

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
        error = "The first message should be the request from ups to connect to the same world"
        create_AUErr(error, 0)
        raise ValueError(error)


'''Handle the commands from UPS'''

def handle_UTAArrived(UTAArrived, ups_socket):
    arrived_seqnum = UTAArrived.seqnum
    send_ackCommand(arrived_seqnum, ups_socket)
    truck_id = UTAArrived.truckid
    wh_id = UTAArrived.whid
    #check if all the required packages are packed
    # for every required, the loop will make sure every package is ready, then check the next one until ready 
    for package_id in UTAArrived.packageid:
        print("starting asking world to pack package id:", package_id)
        session = Session()
        session.begin()
        order_to_load = session.query(Order).filter(Order.package_id == package_id,
                                                Order.warehouse_id == wh_id).with_for_update().first()
        if order_to_load is None:
            atu_send_raise_error("Cannot find find the order to load", arrived_seqnum)
        order_to_load.truck_id = truck_id
        session.commit()
        session.close()
        while (1):
            session = Session()
            session.begin()
            order_to_load = session.query(Order).filter(Order.package_id == package_id,
                                                Order.warehouse_id == wh_id).first()
            if order_to_load.status == 'packed':
                break
            #time.sleep(3)
            #print("packageid not packed, ", package_id)
            #print(order_to_load.status)
            session.close()
    print("all package required from ups should finish packing. Start loading order for truck: ", truck_id)
    #Tell world to load all the requited package
    for package_id in UTAArrived.packageid:
        session = Session()
        session.begin()
        order_to_load = session.query(Order).filter(Order.package_id == package_id,
                                                    Order.warehouse_id == wh_id).first()
        if order_to_load is None:
            atu_send_raise_error("Cannot find find the order to load", arrived_seqnum)    
        Acommand, toload_sn = create_ATWToload(order_to_load.warehouse_id, order_to_load.truck_id, order_to_load.package_id)
        addToWorld(Acommand, toload_sn)
        session.close()

    print("all package should be sent to load to world")
    # TODO: CHANGE HERE!
    #Check if all the package status have become loaded
    for package_id in UTAArrived.packageid:
        while (1):
            session = Session()
            session.begin()
            order_check = session.query(Order).filter(Order.package_id == package_id,
                                                Order.warehouse_id == wh_id).first()
            if order_check.status == 'loaded':
                break
            # time.sleep(3)
            # print("packageid not loaded, ", package_id)
            # print(order_to_load.status)
            session.close()

    print("all package shoud be loaded on truck for truckid: ", truck_id)
    #Send the ATULoaded message to UPS
    ATULoaded, loaded_sn= create_ATULoaded(truck_id)   
    addToUps(ATULoaded, loaded_sn) 
    

def handle_UTAOutDelivery(UTAOutDelivery, ups_socket):
    session = Session()
    out_del_seqnum = UTAOutDelivery.seqnum
    #print("send ack to ups with seqnum: ", out_del_seqnum)
    send_ackCommand(out_del_seqnum, ups_socket)

    package_id = UTAOutDelivery.packageid
    new_x = UTAOutDelivery.x
    new_y = UTAOutDelivery.y
    print("Receive new address from ups: ", (new_x, new_y))
    session.begin()
    order_to_deliver = session.query(Order).filter(Order.package_id == package_id).first()
    if order_to_deliver is None:
        atu_send_raise_error("Cannot find order to deliver", out_del_seqnum)
    if order_to_deliver.status != 'Delivered':
        order_to_deliver.status = 'OutForDelivery'
    order_to_deliver.addr_x = new_x
    order_to_deliver.addr_y = new_y    
    session.commit()
    session.close()


def handle_UTADelivered(UTADelivered, ups_socket):
    delivered_seqnum = UTADelivered.seqnum
    #print("send ack to ups with seqnum: ", delivered_seqnum)
    send_ackCommand(delivered_seqnum, ups_socket)
    session = Session()
    session.begin()
    package_id = UTADelivered.packageid
    delivered_order = session.query(Order).filter(Order.package_id == package_id).first()
    if delivered_order is None:
        atu_send_raise_error("Cannot find delivered order", delivered_seqnum)
    delivered_order.status = 'Delivered'
    session.commit()
    session.close()


def handle_AUErr(AUErr, ups_socket):
    err_seqnum = AUErr.seqnum
    send_ackCommand(err_seqnum, ups_socket)

    err_message = AUErr.err
    originseqnum = AUErr.originseqnum
    print("Error occurs at seqnum: ", originseqnum, "with error message: ", err_message)
    #raise ValueError("received an error from ups")


def handle_ack(ack):
    if ack in toUps:
        toUps.pop(ack)
    # ack may send multiple times, if acks does not exist in our send list 
    # then we should handled them, not an error
    # else:
    #     raise ValueError("ack does not exist in ups queue")

def process_UTACommands(UTACmd, ups_socket):
    for err in UTACmd.err:
            handle_AUErr(err, ups_socket)

    for ack in UTACmd.acks:
        # check if ack in toWorld key and remove from to send
        print("\n!!!!received ups ack, ", ack)
        handle_ack(ack)
    
    for arrive in UTACmd.arrive:
        if arrive.seqnum in handled_ups:
            continue
        handled_ups.add(arrive.seqnum)
        print("\n!!!received ups arrive: ", arrive)
        handle_UTAArrived(arrive, ups_socket)
    
    for to_deliver in UTACmd.todeliver:
        if to_deliver.seqnum in handled_ups:
            continue
        handled_ups.add(to_deliver.seqnum)
        print("\n!!!received ups todeliver: ", to_deliver)
        handle_UTAOutDelivery(to_deliver, ups_socket)

    for delivered in UTACmd.delivered:
        if delivered.seqnum in handled_ups:
            continue
        handled_ups.add(delivered.seqnum)
        print("\n!!!received ups delivered: ", delivered)
        handle_UTADelivered(delivered, ups_socket)

def handle_UTACommands(ups_socket):
    while (True):
        UTACmd = upb2.UTACommands()
        # recv message from the world
        msg = getMessage(ups_socket)
        UTACmd.ParseFromString(msg)
        thread_handle_ups = threading.Thread(target = process_UTACommands, args =(UTACmd, ups_socket,))
        thread_handle_ups.start()
        



