from db_table import *
from utils import *


'''Create the message that is to send to UPS'''

def create_destionation(x, y):
    dest = upb2.Desti_loc()
    dest.x = x
    dest.y = y
    return dest

def send_ackCommand(ack, atu_socket):
    ATUCommands = upb2.ATUCommands()
    ATUCommands.acks.append(ack)
    sendMessage(ATUCommands, atu_socket)


def create_AUConnected(worldid):
    AUConnected = upb2.AUConnected()
    AUConnected.worldid = worldid
    return AUConnected


def create_AUErr(error, originseqnum):
    ATUCommands = upb2.AUTCommands()
    AUErr = ATUCommands.err
    AUErr.err = error
    AUErr.originseqnum = originseqnum
    AUErr.seqnum = seqnum
    return ATUCommands


def create_ATULoaded(package_id, truck_id):
    ATUCommands = upb2.AUTCommands()
    ATULoaded = ATUCommands.loaded
    ATULoaded.packageid = package_id
    ATULoaded.truckid = truck_id
    ATULoaded.seqnum = seqnum
    return ATUCommands


def create_ATURequestPickup(product_name, package_id, ups_account, wh_id, x, y):
    ATUCommands = upb2.AUTCommands()
    ATURequestPickup = ATUCommands.topickup
    ATURequestPickup.product_name = product_name
    ATURequestPickup.packageid = package_id
    if ups_account != "":
        ATURequestPickup.ups_account = ups_account
    ATURequestPickup.whid = wh_id
    destination = create_destionation(x, y)
    ATURequestPickup.destination = destination
    ATURequestPickup.seqnum = seqnum
    return ATUCommands


def create_ATULoad(package_id, truck_id):
    atuCommand = upb2.ATUCommands()
    loaded = atuCommand.loaded.add()
    loaded.packageid = package_id
    loaded.truckid = truck_id
    loaded.seqnum = seqnum
    return atuCommand


'''Create message to World'''

def create_ATWToload(warehouse_id, truck_id, package_id):
    Acommand = wpb2.ACommands()
    Acommand.disconnect = False
    load = Acommand.load.add()
    load.whnum = warehouse_id
    load.truckid = truck_id
    load.shipid = package_id
    load.seqnum = seqnum
    return Acommand

'''
@sendACKToWorld: send ack number to the world
'''
def sendACKToWorld(socket,ack):
    command = wpb2.ACommands()
    command.acks.append(ack)
    command.disconnect = False
    sendMessage(command,socket)

'''
@arg: things: a list of data type <AProduct>
'''
def create_ATWPurchase(warehouse_id, things):
    Acommand = wpb2.ACommands()
    Acommand.disconnect = False
    buy = Acommand.buy.add()
    buy.whnum = warehouse_id
    buy.seqnum = seqnum
    for thing in things:
        athing=buy.things.add()
        athing.id = thing.id
        athing.description = thing.description 
        athing.count = thing.count
    
    return Acommand

def create_ATWToPack(warehouse_id, things, package_id ):
    Acommand = wpb2.ACommands()
    Acommand.disconnect = False
    topack = Acommand.topack.add()
    topack.whnum = warehouse_id
    topack.seqnum = seqnum
    topack.shipid  = package_id
    for thing in things:
        athing = topack.things.add()
        athing.id = thing.id
        athing.description = thing.description 
        athing.count = thing.count
    return Acommand

def create_ATWQuery(package_id):
    Acommand = wpb2.ACommands()
    Acommand.disconnect = False
    toquery = Acommand.queries.add()
    toquery.packageid = package_id
    toquery.seqnum = seqnum
    return Acommand




