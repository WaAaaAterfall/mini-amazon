from datetime import datetime
from db_table import *
import socket
import world_amazon_pb2
from google.protobuf.internal.decoder import _DecodeVarint32
from google.protobuf.internal.encoder import _EncodeVarint


'''
@init_engin: Drop all the tables and restart
'''
seqnum = 1

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
