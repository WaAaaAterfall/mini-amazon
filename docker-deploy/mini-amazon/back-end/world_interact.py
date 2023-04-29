from db_table import *
from utils import *
#from db_connect import *

from amazon_create_msg import *


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
        inventory = session.query(Inventory).filter_by(product_id=pd_id, warehouse_id=wh_id).first()
        if inventory is None:
            new_invent = Inventory(product_id = pd_id, remain_count = product_count, warehouse_id = wh_id)
            session.add(new_invent)
        else:
            inventory.remain_count += product_count
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
    order = session.query(Order).filter(Order.package_id==shipid).with_for_update().first()
    #print("AAAAAAAAAAAAAAAAA", order)
    order.status = 'packed'
    session.commit()
    product_id = order.product_id
    wh_id = order.warehouse_id
    inventory = session.query(Inventory).filter(Inventory.product_id==product_id,
                                                Inventory.warehouse_id==wh_id).first()
    inventory.remain_count -= order.count
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
    #TODO: CHANGE HERE!
    ## inform ups the package has been loaded
    # order = session.query(Order).filter_by(package_id=shipid).first()
    # atuCommand = create_ATULoaded(order.package_id,order.truck_id)
    # addToUps(atuCommand)
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

def handle_AErr(error):
    print("error information: " + error.err)
    print("error originseqnum: " + error.originseqnum)
    print("error seqnum: " + error.seqnum)

def handle_ack(ack):
    # check if ack in toWorld key and remove from to send
    if ack in toWorld:
        toWorld.pop(ack)

def process_WorldCmd(Response, world_fd):
    for error in Response.error:
        # send ack to the world
        sendACKToWorld(world_fd, error.seqnum)
        handle_AErr(error)

    # deal with ack
    # find each ack in AResponses, and remove relenvent seq:ACommand from dict toWorld
    for ack in Response.acks:
        handle_ack(ack)
        print("!!!! received world ack: ", ack)
    # now we need to handle purchase, pack, load
    for arrive in Response.arrived:
        if arrive.seqnum in handled_world:
            continue
        handled_world.add(arrive.seqnum)
        print("!!!! received world purchase arrive: ", arrive)
        handlePurchase(arrive, world_fd)
    for ready in Response.ready:
        if ready.seqnum in handled_world:
            continue
        handled_world.add(ready.seqnum)
        print("!!!! received world packed ready: ", ready)
        handleReady(ready, world_fd)
    for loaded in Response.loaded:
        if loaded.seqnum in handled_world:
            continue
        handled_world.add(loaded.seqnum)
        print("!!!! received world loaded: ", loaded)
        handleLoaded(loaded, world_fd)
    for packagestatus in Response.packagestatus:
        if packagestatus.seqnum in handled_world:
            continue
        handled_world.add(packagestatus.seqnum)
        print("!!!! received world packagestatus: ", packagestatus)
        handlePackagestatus(packagestatus, world_fd)


def handleWorldResponse(world_fd):
    # each thread get one session
    while (True):
        Response = wpb2.AResponses()
        # recv message from the world
        msg = getMessage(world_fd)
        # if len(msg) == 0:
        #     continue
        Response.ParseFromString(msg)
        thread_handle_ups = threading.Thread(target = process_WorldCmd, args = (Response, world_fd,))
        thread_handle_ups.start()
        