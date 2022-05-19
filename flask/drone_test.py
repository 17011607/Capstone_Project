from socket import *

client_sock = socket(AF_INET, SOCK_DGRAM)
client_sock.connect(('192.168.137.143', 8889))
msg = "rc 10 -10 0 0"
client_sock.send(msg.encode('utf-8'))
