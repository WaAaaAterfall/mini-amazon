'''Create the message that is to send to UPS'''

def create_ackCommand(acks):
    ATUCommands = pb2.ATUCommands()
    for ack in acks:
        ATUCommands.acks.append(ack)
    return ATUCommands

def create_AUConnected(worldid):
    AUConnected = pb2.AUConnected()
    AUConnected.worldid = worldid
    return AUConnected

def create_AUErr(error, originseqnum):
    ATUCommands = pb2.AUTCommands()
    AUErr = ATUCommands.err
    AUErr.err = error
    AUErr.originseqnum = originseqnum
    AUErr.seqnum = seqnum
    return ATUCommands

def create_ATULoaded(package_id, truck_id):
    ATUCommands = pb2.AUTCommands()
    ATULoaded = ATUCommands.loaded
    ATULoaded.packageid = package_id
    ATULoaded.truckid = truck_id
    ATULoaded.seqnum = seqnum
    return ATUCommands

def create_ATURequestPickup(product_name, package_id, ups_account, wh_id, destination):
    ATUCommands = pb2.AUTCommands()
    ATURequestPickup = ATUCommands.topickup
    ATURequestPickup.product_name = product_name
    ATURequestPickup.packageid = package_id
    if ups_account != "":
        ATURequestPickup.ups_account = ups_account
    ATURequestPickup.whid = wh_id
    ATURequestPickup.destination = destination
    ATURequestPickup.seqnum = seqnum
    return ATUCommands
