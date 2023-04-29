from db_table import *
import socket
import world_amazon_pb2 as wpb2
from google.protobuf.internal.decoder import _DecodeVarint32
from google.protobuf.internal.encoder import _EncodeVarint
import time
import threading

import ups_amazon_pb2 as upb2
import world_amazon_pb2 as wpb2


'''
@init_engin: Drop all the tables and restart
'''

g_seqnum = 1
seqnum_lock = threading.Lock()

#dict
toWorld = {}
toUps = {}
#Hashset
handled_world = set()
handled_ups = set()

def init_engine():
    # engine = create_engine(
    #     'postgresql://postgres:passw0rd@localhost:5432/hw4_568')
    # engine = create_engine(
    #     'postgresql://postgres:postgres@postgres_db_container:5432/postgres')
    # print('Opened database successfully')
    #Base.metadata.drop_all(engine)
    print('Drop tables successfully')
    # Base.metadata.create_all(engine)


'''
@sendMessage: encode data length to send and sendmessage to corrosponding socket
'''
def sendMessage(message, socket):
    msg = message.SerializeToString()
    _EncodeVarint(socket.sendall, len(msg), None)
    socket.sendall(msg)


'''
@getMessage: receive data from socket (including get length of real string)
'''
def getMessage(socket):
    var_int_buff = []
    while True:
        print(socket)
        buf = socket.recv(1)
        var_int_buff += buf
        msg_len, new_pos = _DecodeVarint32(var_int_buff, 0)
        if new_pos != 0:
            break
        # try:
        #     buf = socket.recv(1)
        #     var_int_buff += buf
        #     msg_len, new_pos = _DecodeVarint32(var_int_buff, 0)
        #     if new_pos != 0:
        #         break
        # except:
        #     whole_message = []
        #     return whole_message
    whole_message = socket.recv(msg_len)
    return whole_message


'''In case to prevent any repeated assignment with one seqnum, use global lock'''
def assign_unique_seqnum():
    global g_seqnum
    with seqnum_lock:
        assigned_seqnum = g_seqnum
        g_seqnum += 1
    return assigned_seqnum


'''
@addToWorld: add to dict and increment the sequence number
'''
def addToWorld(Acommand, current_seqnum):
    if current_seqnum in toWorld:
        raise ValueError("This seqnum has already been added into world command dict")
    toWorld[current_seqnum] = Acommand


'''
@addToUps: add to dict and increment the sequence number
'''
def addToUps(ATUcommand, current_seqnum):
    if current_seqnum in toUps:
        raise ValueError("This seqnum has already been added into UPS command dict")
    toUps[current_seqnum] = ATUcommand


'''
@sendToworld: keep sending the message in dict toworld to the world
@warning: dict is not thread safe, we need add thread lock later
'''
def sendToWorld(world_fd):
    while(True):
        time.sleep(5)
        print("Current world seqnum: ", toWorld.keys())
        print("Current handled world seqnum, ", handled_world)
        world_copy = toWorld.copy()
        count = 1
        for key, acommand in world_copy.items():
            sendMessage(acommand, world_fd)
            time.sleep(1)
            count += 1
            if count % 3 == 0:
                count = 1
                time.sleep(5)
            print("send world: ",acommand)


'''
@sendToUPS: keep sending the message in dict toUps to the world
@warning: dict is not thread safe, we need add thread lock later
'''
def sendToUPS(ups_fd):
    while(True):
        time.sleep(10)
        print("Current ups seqnum: ", toUps.keys())
        print("Current handled ups seqnum, ", handled_ups)
        ups_copy = toUps.copy()
        count = 1
        for key, ATUcommand in ups_copy.items():
            sendMessage(ATUcommand, ups_fd)
            count += 1
            if count % 3 == 0:
                count = 1
                time.sleep(5)
            #print("send ups: ", ATUcommand)


