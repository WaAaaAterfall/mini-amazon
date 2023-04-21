from db_table import *
from utils import *
from sqlalchemy.orm import query, Session, sessionmaker
import ups_amazon_pb2
import world_amazon_pb2
import google.protobuf

# # drop all table before start
# Base.metadata.drop_all(engine)
# # create table
# Base.metadata.create_all(engine)
# global varible
# two dict that should send to ups and world {seq:ACommands}
# when handle ups and handle world merge together we need put these two global vaiable in same place and just reference them


# '''
# @handlePurchase: send ack, edit database to addup the remain count
# @Arg:   APurchaseMore: data type APurchaseMore  in  world_amazon.proto
# '''

def handlePurchase(APurchaseMore,world_fd,session):
    # firstly send ack to the world
    seqnum = APurchaseMore.seqnum 
    sendACKToWorld(world_fd,seqnum)
    # get warehouse id
    wh_id = APurchaseMore.whnum
    # for loop to get product info especially product_id, product_count
    # update the value in inventory database
    for product in APurchaseMore.things:
        pd_id = product.id 
        product_count = product.count 
        session.query(Inventory).filter_by(product_id= pd_id, warehouse_id = wh_id )\
        .update({"amount": Inventory.remain_count + product_count})
        session.commit()

# '''
# @handleReady: send ack, change order status to packed. check whether ups truck arrived->inform world to load
# @Arg:   APacked: data type APacked  in  world_amazon.proto
# ''' 
def handleReady(APacked ,world_fd,session):
    # firstly send ack to the 
    seqnum = APacked.seqnum 

    sendACKToWorld(world_fd,seqnum)
    # edit order status to packed
    shipid = APacked.shipid 
    session.query(Order).filter_by(package_id= shipid).update({"status" : 'packed'})
    session.commit()
    order = session.query(Order).filter_by(package_id= shipid).first()
    if order.truck_id is not None:
        # inform the world to load the package
        # specifically add the acommand to dict
        Acommand = world_amazon_pb2.ACommands()
        Acommand.disconnect = False
        load = Acommand.load.add()
        load.whnum = order.warehouse_id
        load.truckid = order.truck_id
        load.shipid = order.package_id
        load.seqnum = seqnum
        addToWorld(Acommand)

# '''
# @handleLoaded: send ack, change order status to loaded. inform ups the package has been loaded
# @Arg:   APacked: data type APacked  in  world_amazon.proto
# ''' 
def handleLoaded(ALoaded,world_fd,session):
    # firstly send ack to the 
    seqnum = ALoaded.seqnum 
    sendACKToWorld(world_fd,seqnum)
    # edit order status to packed
    shipid = ALoaded.shipid 
    session.query(Order).filter_by(package_id= shipid).update({"status" : 'loaded'})
    session.commit()
    order = session.query(Order).filter_by(package_id= shipid).first()
    # inform ups the package has been loaded
    atuCommand = ups_amazon_pb2.ATUCommands()
    loaded = atuCommand.loaded.add()
    loaded.packageid = order.package_id
    loaded.truckid = order.truck_id
    loaded.seqnum = seqnum
    addToUps(atuCommand)

# '''
# @handlePackagestatus: send ack, change order status to according status. 
# @Arg:   APackage: data type APackage  in  world_amazon.proto
# ''' 
def handlePackagestatus(APackage,world_fd,session):
    # firstly send ack to the 
    seqnum = APackage.seqnum 
    sendACKToWorld(world_fd,seqnum)
    # update order status
    session.query(Order).filter_by(package_id= APackage.packageid ).update({"status" : APackage.status})
    session.commit()
    




def handleWorldResponse(world_fd):
    #each thread get one session
    session = Session()
    session.begin()
    while (True):
        Response = world_amazon_pb2.AResponses()
        # recv message from the world
        msg = getMessage(world_fd)
        Response.ParseFromString(msg)
        # firstly let we deal with all errors----print them
        for error in Response.error:
            #send ack to the world
            sendACKToWorld(world_fd,error.seqnum)
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
            handlePurchase(arrive,world_fd,session)
        for ready in Response.ready:
            handleReady(ready,world_fd,session)
        for loaded in Response.loaded:
            handleLoaded(loaded,world_fd,session)
        for packagestatus in Response.packagestatus:
            handlePackagestatus(packagestatus,world_fd,session)
        

if __name__ == '__main__':
   # without ups, create new world, leave world id blank
   Aconnect = world_amazon_pb2.AConnect()
   warehouse_1 = Aconnect.initwh.add()
   warehouse_1.id = 1
   warehouse_1.x = 20
   warehouse_1.y = 20
   warehouse_2 = Aconnect.initwh.add()
   warehouse_2.id = 2
   warehouse_2.x = 40
   warehouse_2.y = 40
   Aconnect.isAmazon = True
   # keep connect to world until it success
   while(True):
    wold_fd, Connected = connectWorld(Aconnect)
    if Connected:
        break
    



   




            
