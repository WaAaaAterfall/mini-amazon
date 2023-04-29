from test_ups import *

def synax_test():
    print("ATUack:\n", send_ackCommand(10, 1111))
    print("ATConnected:\n", create_AUConnected(1))
    print("AUErr:\n", create_AUErr("this is an error", 5))
    print("ATURequestPickup:\n", create_ATURequestPickup("Product", 1, "", 3, 4, 5))
    print("ATURequestPickup:\n", create_ATURequestPickup("Product", 1, "name", 3, 4, 5))    
    print("ATULoaded: \n",create_ATULoaded(11,12))
    print("create_ATWToload: \n", create_ATWToload(1,2,3))
    print("create_ATWPurchase: \n", create_ATWPurchase(2,3,'This is a product', 10))
    print("create_ATWToPack: \n", create_ATWToPack(1, 2, "Product description", 10, 15))
    print("create_ATWQuery: \n", create_ATWQuery(40))
    print("sendACKToWorld: \n", sendACKToWorld(111,20))

if __name__ == '__main__':
    synax_test()

