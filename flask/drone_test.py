from socket import *
from time import sleep

client_sock = socket(AF_INET, SOCK_DGRAM)

client_sock.bind(('', 8890))
tello_ip = '192.168.10.1'
tello_port = 8889
tello_address = (tello_ip, tello_port)
#msg = 'land'
msg = 'battery?'
client_sock.sendto(msg.encode('utf-8'), tello_address)
#msg = "land"
#msg = 'ap SK_WiFiGIGAA308_2.4G ECQ57@9605'
response, ip = client_sock.recvfrom(1024)
outStr = 'Tello State:' + str(response.decode())
print(outStr)