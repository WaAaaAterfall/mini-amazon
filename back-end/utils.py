from datetime import datetime
from db_table import *
import socket
import world_amazon_pb2
from google.protobuf.internal.decoder import _DecodeVarint32
from google.protobuf.internal.encoder import _EncodeVarint
import time


'''
@init_engin: Drop all the tables and restart
'''

seqnum = 1
Word_HostName = ''
Word_PortNum = 23456
toWorld = {}
toUps = {}

def init_engine():
    # engine = create_engine(
    #     'postgresql://postgres:passw0rd@localhost:5432/hw4_568')
    # engine = create_engine(
    #     'postgresql://postgres:postgres@postgres_db_container:5432/postgres')
    # print('Opened database successfully')
    Base.metadata.drop_all(engine)
    print('Drop tables successfully')
    Base.metadata.create_all(engine)


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
        buf = socket.recv(1)
        var_int_buff += buf
        msg_len, new_pos = _DecodeVarint32(var_int_buff, 0)
        if new_pos != 0:
            break
    whole_message = socket.recv(msg_len)
    return whole_message


'''
@sendACKToWorld: send ack number to the world
'''
def sendACKToWorld(socket,ack):
    command = world_amazon_pb2.ACommands()
    command.acks.append(ack)
    command.disconnect = False
    sendMessage(command,socket)

'''
@addToWorld: add to dict and increment the sequence number
'''
def addToWorld(Acommand):
    toWorld[seqnum] = Acommand
    seqnum = seqnum + 1

'''
@addToUps: add to dict and increment the sequence number
'''
def addToUps(Acommand):
    toUps[seqnum] = Acommand
    seqnum = seqnum + 1

'''
@sendToworld: keep sending the message in dict toworld to the world
@warning: dict is not thread safe, we need add thread lock later
'''
def sendToWorld(Acommand,world_fd):
    while(True):
        time.sleep(1)
        for key, acommand in toWorld.items():
            sendMessage(world_fd, acommand)
         
'''
@sendToUPS: keep sending the message in dict toUps to the world
@warning: dict is not thread safe, we need add thread lock later
'''
def sendToUPS(Acommand,ups_fd):
    while(True):
        time.sleep(1)
        for key, acommand in toUps.items():
            sendMessage(ups_fd, acommand)


def connectWorld(Aconnect):
    world_fd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    world_fd.connect(Word_HostName,Word_PortNum)
    sendMessage(Aconnect,world_fd)
    Aconnected = world_amazon_pb2.AConnected()
    msg = getMessage(world_fd)
    Aconnected.ParseFromString(msg)
    #print world id and result
    #do i need to try catch if result is not connected
    print(Aconnected.worldid)
    print(Aconnected.result )
    connected = False
    if Aconnected.result == 'connected':
        connected = True
    return world_fd, connected






