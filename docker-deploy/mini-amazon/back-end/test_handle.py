from ups_interact import *
from world_interact import *
from web_interact import *
UPS_HOSTNAME = 'vcm-30458.vm.duke.edu'
UPS_PORTNUM = 32345
def amazonStart():
    #Port for world: connect to 23456
    #Port for ups: connect to 32345
    #Port for web: listen on 13145
    try:
        init_engine()

        # connect to ups
        atu_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        atu_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        ups_address = (UPS_HOSTNAME, UPS_PORTNUM)

        atu_socket.connect(ups_address)
        ATUCmd, num = create_ATURequestPickup("111", 1, "", 1,2,3)
        sendMessage(ATUCmd, atu_socket)
        print("Create a thread to handle ups command")
        thread_handle_ups = threading.Thread(target = handle_UTACommands, args =(atu_socket,))
        thread_handle_ups.start()


        while 1:
            continue
        #atu_socket.close()
        #amazon_socket.close()
    except ValueError as err:
        print("Raise error: ", err.args)


if __name__ == '__main__':
    amazonStart()