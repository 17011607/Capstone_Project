from socket import *

client_sock = socket(AF_INET, SOCK_DGRAM)
client_sock.connect(('192.168.10.1', 8889))
#msg = 'land'
msg = 'forward 20'
#client_sock.send(msg.encode('utf-8'))
#msg = "land"
#msg = 'ap SK_WiFiGIGAA308_2.4G ECQ57@9605'
while(1):
    client_sock.send(msg.encode('utf-8'))