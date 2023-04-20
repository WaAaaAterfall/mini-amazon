from db_table import *
from utils import *
from sqlalchemy.orm import query, Session, sessionmaker
import world_amazon_pb2
import google.protobuf

# drop all table before start
Base.metadata.drop_all(engine)
# create table
Base.metadata.create_all(engine)
# global varible
# two dict that should send to ups and world {seq:ACommands}
# when handle ups and handle world merge together we need put these two global vaiable in same place and just reference them
toWorld = {}
toUps = {}

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
# @handleReady: send ack, change order status to packed
# @Arg:   APurchaseMore: data type APurchaseMore  in  world_amazon.proto
# ''' 
def handleReady(APacked ,world_fd,session):
    # firstly send ack to the 
    seqnum = APacked.seqnum 
    sendACKToWorld(world_fd,seqnum)
    # edit order status to packed
    shipid = APacked.shipid 
    session.query(Order).filter_by(package_id= shipid)







def handleWorldResponse(world_fd):
    #each thread get one session
    session = Session()
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

if __name__ == '__main__':
   print(google.protobuf.__version__)


            
