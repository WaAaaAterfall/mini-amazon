from db_table import *
from utils import *
#from db_connect import *

from amazon_create_msg import *

WORLD_HOSTNAME = 'localhost'
WORLD_PORTNUM = 23456


# '''
# @handlePurchase: send ack, edit database to addup the remain count
# @Arg:   APurchaseMore: data type APurchaseMore  in  world_amazon.proto
# '''
def handlePurchase(APurchaseMore, world_fd):
    session = Session()
    session.begin()
    # firstly send ack to the world
    seqnum = APurchaseMore.seqnum
    sendACKToWorld(world_fd, seqnum)
    # get warehouse id
    wh_id = APurchaseMore.whnum
    # for loop to get product info especially product_id, product_count
    # update the value in inventory database
    for product in APurchaseMore.things:
        pd_id = product.id
        product_count = product.count
        session.query(Inventory).filter_by(product_id=pd_id, warehouse_id=wh_id)\
            .update({"amount": Inventory.remain_count + product_count})
        session.commit()
    session.close()


# '''
# @handleReady: send ack, change order status to packed. check whether ups truck arrived->inform world to load
# @Arg:   APacked: data type APacked  in  world_amazon.proto
# '''
def handleReady(APacked, world_fd):
    session = Session()
    # firstly send ack to the
    seqnum = APacked.seqnum
    sendACKToWorld(world_fd, seqnum)
    session.begin()
    # edit order status to packed
    shipid = APacked.shipid
    session.query(Order).filter_by(
        package_id=shipid).update({"status": 'packed'})
    session.commit()
    session.close()
    # order = session.query(Order).filter_by(package_id=shipid).first()
    # if order.truck_id is not None:
    #     # inform the world to load the package
    #     # specifically add the acommand to dict
    #     Acommand = create_ATWToload(order.warehouse_id, order.truck_id, order.package_id)
    #     addToWorld(Acommand)



# '''
# @handleLoaded: send ack, change order status to loaded. inform ups the package has been loaded
# @Arg:   APacked: data type APacked  in  world_amazon.proto
# '''
def handleLoaded(ALoaded, world_fd):
    session = Session()
    session.begin()
    # firstly send ack to the
    seqnum = ALoaded.seqnum
    sendACKToWorld(world_fd, seqnum)
    # edit order status to packed
    shipid = ALoaded.shipid
    session.query(Order).filter_by(
        package_id=shipid).update({"status": 'loaded'})
    session.commit()
    order = session.query(Order).filter_by(package_id=shipid).first()
    #TODO: CHANGE HERE!
    # inform ups the package has been loaded
    atuCommand = create_ATULoaded(order.package_id,order.truck_id)
    addToUps(atuCommand)
    session.close()


# '''
# @handlePackagestatus: send ack, change order status to according status.
# @Arg:   APackage: data type APackage  in  world_amazon.proto
# '''
def handlePackagestatus(APackage, world_fd):
    session = Session()
    session.begin()
    # firstly send ack to the
    seqnum = APackage.seqnum
    sendACKToWorld(world_fd, seqnum)
    # update order status
    session.query(Order).filter_by(package_id=APackage.packageid).update(
        {"status": APackage.status})
    session.commit()
    session.close()


def handleWorldResponse(world_fd):
    # each thread get one session
    while (True):
        Response = wpb2.AResponses()
        # recv message from the world
        msg = getMessage(world_fd)
        Response.ParseFromString(msg)
        # firstly let we deal with all errors----print them
        for error in Response.error:
            # send ack to the world
            sendACKToWorld(world_fd, error.seqnum)
            print("error information: " + error.err)
            print("error originseqnum: " + error.originseqnum)
            print("error seqnum: " + error.seqnum)

        # deal with ack
        # find each ack in AResponses, and remove relenvent seq:ACommand from dict toWorld
        for ack in Response.acks:
            # check if ack in toWorld key and remove from to send
            if ack in toWorld:
                toWorld.pop(ack)
        # now we need to handle purchase, pack, load
        # in each section, we need to send ack to the world to avoid the world send the response multiply times
        for arrive in Response.arrived:
            if arrive.seqnum in handled_world:
                continue
            handled_world.add(arrive.seqnum)
            handlePurchase(arrive, world_fd)
        for ready in Response.ready:
            if ready.seqnum in handled_world:
                continue
            handled_world.add(ready.seqnum)
            handleReady(ready, world_fd)
        for loaded in Response.loaded:
            if loaded.seqnum in handled_world:
                continue
            handled_world.add(loaded.seqnum)
            handleLoaded(loaded, world_fd)
        for packagestatus in Response.packagestatus:
            if packagestatus.seqnum in handled_world:
                continue
            handled_world.add(packagestatus.seqnum)
            handlePackagestatus(packagestatus, world_fd)


def connectWorld(warehouse_dict, worldid = None):
    #generate Aconncet
    Aconnect = wpb2.AConnect()
    # Iterate over the dictionary of warehouse information
    for warehouse_id, warehouse_info in warehouse_dict.items():
        # Create a new warehouse object and set its properties
        warehouse = Aconnect.initwh.add()
        warehouse.id = warehouse_id
        warehouse.x = warehouse_info['x']
        warehouse.y = warehouse_info['y']
    Aconnect.isAmazon = True
    if(worldid != None):
        Aconnect.worldid = worldid
    print("World initialization over")
    world_fd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    world_ip = socket.gethostbyname(WORLD_HOSTNAME)
    world_fd.connect((world_ip, WORLD_PORTNUM))
    sendMessage(Aconnect,world_fd)
    print("AConnect sent with world id: ", worldid)
    Aconnected = wpb2.AConnected()
    msg = getMessage(world_fd)
    Aconnected.ParseFromString(msg)
    #print world id and result
    world_id = Aconnected.worldid
    print(Aconnected.result)
    connected = False
    if Aconnected.result == 'connected!':
        connected = True

    return world_fd, connected, world_id
