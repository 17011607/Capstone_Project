from socket import *

client_sock = socket(AF_INET, SOCK_DGRAM)
client_sock.connect(('192.168.137.247', 8889))
#msg = 'land'
msg = 'takeoff'
#client_sock.send(msg.encode('utf-8'))
#msg = "land"
#msg = 'ap Tello_Drone eltmznjem'
client_sock.send(msg.encode('utf-8'))
