from db_table import *
from utils import *
from db_connect import *
from sqlalchemy.orm import query, Session, sessionmaker

from amazon_create_msg import *



# global varible
# two dict that should send to ups and world {seq:ACommands}
# when handle ups and handle world merge together we need put these two global vaiable in same place and just reference them


# '''
# @handlePurchase: send ack, edit database to addup the remain count
# @Arg:   APurchaseMore: data type APurchaseMore  in  world_amazon.proto
# '''

def handlePurchase(APurchaseMore, world_fd, session):
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

# '''
# @handleReady: send ack, change order status to packed. check whether ups truck arrived->inform world to load
# @Arg:   APacked: data type APacked  in  world_amazon.proto
# '''


def handleReady(APacked, world_fd, session):
    # firstly send ack to the
    seqnum = APacked.seqnum

    sendACKToWorld(world_fd, seqnum)
    session.begin()
    # edit order status to packed
    shipid = APacked.shipid
    session.query(Order).filter_by(
        package_id=shipid).update({"status": 'packed'})
    session.commit()
    order = session.query(Order).filter_by(package_id=shipid).first()
    if order.truck_id is not None:
        # inform the world to load the package
        # specifically add the acommand to dict
        Acommand = create_ATWToload(order.warehouse_id, order.truck_id, order.package_id)
        addToWorld(Acommand)

# '''
# @handleLoaded: send ack, change order status to loaded. inform ups the package has been loaded
# @Arg:   APacked: data type APacked  in  world_amazon.proto
# '''


def handleLoaded(ALoaded, world_fd, session):
    # firstly send ack to the
    seqnum = ALoaded.seqnum
    sendACKToWorld(world_fd, seqnum)
    # edit order status to packed
    shipid = ALoaded.shipid
    session.query(Order).filter_by(
        package_id=shipid).update({"status": 'loaded'})
    session.commit()
    order = session.query(Order).filter_by(package_id=shipid).first()
    # inform ups the package has been loaded
    atuCommand = create_ATULoad(order.package_id,order.truck_id)
    # loaded = atuCommand.loaded.add()
    # loaded.packageid = order.package_id
    # loaded.truckid = order.truck_id
    # loaded.seqnum = seqnum
    addToUps(atuCommand)

# '''
# @handlePackagestatus: send ack, change order status to according status.
# @Arg:   APackage: data type APackage  in  world_amazon.proto
# '''


def handlePackagestatus(APackage, world_fd, session):
    # firstly send ack to the
    seqnum = APackage.seqnum
    sendACKToWorld(world_fd, seqnum)
    # update order status
    session.query(Order).filter_by(package_id=APackage.packageid).update(
        {"status": APackage.status})
    session.commit()


def handleWorldResponse(world_fd):
    # each thread get one session
    session = Session()
    session.begin()
    while (True):
        Response = world_amazon_pb2.AResponses()
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
            handlePurchase(arrive, world_fd, session)
        for ready in Response.ready:
            handleReady(ready, world_fd, session)
        for loaded in Response.loaded:
            handleLoaded(loaded, world_fd, session)
        for packagestatus in Response.packagestatus:
            handlePackagestatus(packagestatus, world_fd, session)


if __name__ == '__main__':
    # before start drop all db and creat all table
    engine = init_engine()
    # without ups, create new world, leave world id blank
    Aconnect = wpb2.AConnect()
    # Create an empty dictionary to store warehouse information
    warehouse_dict = {}

   # Add a warehouse to the dictionary
    warehouse_dict[1] = {'x': 20, 'y': 20}
    warehouse_dict[2] = {'x': 300, 'y': 300}
    # Iterate over the dictionary of warehouse information
    for warehouse_id, warehouse_info in warehouse_dict.items():
        # Create a new warehouse object and set its properties
        warehouse = Aconnect.initwh.add()
        warehouse.id = warehouse_id
        warehouse.x = warehouse_info['x']
        warehouse.y = warehouse_info['y']

    Aconnect.isAmazon = True
    # keep connect to world until it success
    wold_fd = 0
    while (True):
        fd, Connected = connectWorld(Aconnect)
        wold_fd = fd
        if Connected:
            break
    # update database to put warehouse in
    session = getSession(engine)
    for warehouse_id, warehouse_info in warehouse_dict.items():
        New_Warehose = Warehouse(id = warehouse_id, x = warehouse_info['x'], y = warehouse_info['y'])
        session.add(New_Warehose)
        session.commit()
    session.close()



