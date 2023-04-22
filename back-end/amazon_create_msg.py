from db_table import *
from utils import *

import ups_amazon_pb2 as upb2
import world_amazon_pb2 as wpb2

'''Create the message that is to send to UPS'''


def create_ackCommand(acks):
    ATUCommands = upb2.ATUCommands()
    for ack in acks:
        ATUCommands.acks.append(ack)
    return ATUCommands


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


def create_ATURequestPickup(product_name, package_id, ups_account, wh_id, destination):
    ATUCommands = upb2.AUTCommands()
    ATURequestPickup = ATUCommands.topickup
    ATURequestPickup.product_name = product_name
    ATURequestPickup.packageid = package_id
    if ups_account != "":
        ATURequestPickup.ups_account = ups_account
    ATURequestPickup.whid = wh_id
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
