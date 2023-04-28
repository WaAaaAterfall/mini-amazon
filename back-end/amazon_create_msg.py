from db_table import *
from utils import *


'''Create the message that is to send to UPS'''

def create_destionation(x, y):
    dest = upb2.Desti_loc()
    dest.x = x
    dest.y = y
    return dest

def send_ackCommand(ack, atu_socket):
    print("send ack to ups: ", ack)
    ATUCommands = upb2.ATUCommands()
    ATUCommands.acks.append(ack)
    sendMessage(ATUCommands, atu_socket)


def create_AUConnected(worldid):
    AUConnected = upb2.AUConnected()
    AUConnected.worldid = worldid
    return AUConnected


def create_AUErr(error, originseqnum):
    ATUCommands = upb2.ATUCommands()
    AUErr = ATUCommands.err.add()
    AUErr.err = error
    AUErr.originseqnum = originseqnum
    AUErr.seqnum = assign_unique_seqnum()
    return ATUCommands, AUErr.seqnum


def create_ATURequestPickup(product_name, package_id, ups_account, wh_id, x, y):
    ATUCommands = upb2.ATUCommands()
    ATURequestPickup = ATUCommands.topickup.add()
    ATURequestPickup.product_name = product_name
    ATURequestPickup.packageid = package_id
    if ups_account != "":
        ATURequestPickup.ups_account = ups_account
    ATURequestPickup.whid = wh_id
    dest = ATURequestPickup.destination
    dest.x = x
    dest.y = y
    ATURequestPickup.seqnum = assign_unique_seqnum()
    return ATUCommands, ATURequestPickup.seqnum


def create_ATULoaded(truck_id):
    atuCommand = upb2.ATUCommands()
    loaded = atuCommand.loaded.add()
    loaded.truckid = truck_id
    loaded.seqnum = assign_unique_seqnum()
    return atuCommand, loaded.seqnum



'''Create message to World'''

def create_ATWToload(warehouse_id, truck_id, package_id):
    Acommand = wpb2.ACommands()
    #Acommand.disconnect = False
    load = Acommand.load.add()
    load.whnum = warehouse_id
    load.truckid = truck_id
    load.shipid = package_id
    load.seqnum = assign_unique_seqnum()
    return Acommand, load.seqnum

def create_ATWPurchase(warehouse_id, product_id, title, count):
    Acommand = wpb2.ACommands()
    #Acommand.disconnect = False
    buy = Acommand.buy.add()
    buy.whnum = warehouse_id
    buy.seqnum = assign_unique_seqnum()
    athing=buy.things.add()
    athing.id = product_id
    athing.description = title 
    athing.count = count
    return Acommand, buy.seqnum

def create_ATWToPack(warehouse_id, product_id, title, count, package_id):
    Acommand = wpb2.ACommands()
    #Acommand.disconnect = False
    topack = Acommand.topack.add()
    topack.whnum = warehouse_id
    topack.seqnum = assign_unique_seqnum()
    topack.shipid  = package_id
    athing = topack.things.add()
    athing.id = product_id
    athing.description = title 
    athing.count = count
    return Acommand, topack.seqnum

def create_ATWQuery(package_id):
    Acommand = wpb2.ACommands()
    #Acommand.disconnect = False
    toquery = Acommand.queries.add()
    toquery.packageid = package_id
    toquery.seqnum = assign_unique_seqnum()
    return Acommand, toquery.seqnum


'''
@sendACKToWorld: send ack number to the world
'''
def sendACKToWorld(socket,ack):
    command = wpb2.ACommands()
    print("send ack to world: ", ack)
    command.acks.append(ack)
    #command.disconnect = False
    sendMessage(command,socket)




