import socket

class camera:
    def __init__(self, HOST, PORT):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.HOST = HOST
        self.PORT = PORT
        self.sock.bind(('0.0.0.0', 9998))
    def send(self, data):
        self.sock.sendto(data.encode(), (self.HOST, self.PORT)); # Camera Commnad are only SS, LS, RS, LU, LD, RU, RD

'''
cam = camera('192.168.137.47', 4210)
value = input("value :")
cam.send(value)
'''
