from django.shortcuts import render
from amazon.models import *

import socket

# send a signal to backend when received a order
def send_signal(o_id):
  HOST = "server" #"127.0.0.1"  # The server's hostname or IP address
  PORT = 12345
  with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    s.sendall(o_id)
    s.close()


# Create your views here.
def place_order(request):
    if request.method == 'POST':
        package_id = request.POST.get('package_id')
        status = request.POST.get('status')
        truck_id = request.POST.get('truck_id')
        warehouse_id = request.POST.get('warehouse_id')
        addr_x = request.POST.get('addr_x')
        addr_y = request.POST.get('addr_y')
        product_id = request.POST.get('product_id')
        time = request.POST.get('time')
        order = Order(package_id=package_id, status=status, truck_id=truck_id, warehouse_id=warehouse_id, addr_x=addr_x, addr_y=addr_y, product_id=product_id, time=time)
        order.save()
        # TODO: transfer order_id through socket to backend
        send_signal(package_id)
        return render(request, 'amazon/success.html')
    else:
        return render(request, 'amazon/place_order.html')
