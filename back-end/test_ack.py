from amazon_server import *


if __name__ == '__main__':
    try:
        #addToWorld(1, 1)
        addToWorld(2, 22)
        addToWorld(4, 44)
        addToWorld(1, 11)
        addToUps(3, 33)
        addToUps(5, 55)
        addToWorld(3,33)
        addToUps(4,44)
        addToUps(6,66)
        print(toWorld)
        print(toUps)
        #sendToUPS(1111)
        thread_handle_web = threading.Thread(target = sendToWorld, args =(222,))
    except ValueError as err:
        print("Raise error: ", err.args)
