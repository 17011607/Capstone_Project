import socket
from time import sleep


class drone_status():
    local_ip = ''
    local_port = 8890 ## read port
    socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # socket for sending cmd
    socket.bind((local_ip, local_port))

    def __init__(self):
        self.local_ip = ''
        self.local_port = 8890
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        socket.bind((self.local_ip, self.local_port))

        self.tello_ip = '192.168.10.1'
        self.tello_port = 8889
        self.tello_address = (self.tello_ip, self.tello_port)

    def data_filter(self,key,data):
        if data.find(key) == -1:
            return data
        data=data.split(key)
        data=data[1].split(';')
        data=data[0].lstrip(':')
        return data

    def battery(self):
        socket.sendto('command'.encode('utf-8'), self.tello_address) ## Enter SDK Mode   
        response, ip = socket.recvfrom(1024)
        data=response.decode()
        print(data)
        data = self.data_filter('bat',data)
        return data

'''    
if __name__ == "__main__":
    print(battery())
    
    local_ip = ''
    local_port = 8890 ## read port
    socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # socket for sending cmd
    socket.bind((local_ip, local_port))

    tello_ip = '192.168.10.1'
    tello_port = 8889 ## write port
    tello_address = (tello_ip, tello_port)
    socket.sendto('command'.encode('utf-8'), tello_address) ## Enter SDK Mode   
    socket.sendto('battery?'.encode('utf-8'), tello_address) ## Enter SDK Mode   
    response = socket.recvfrom(1024)
    outStr = 'Tello Battery:' + str(response.decode)
    print(outStr)
    try:
        index = 0
        while True:
            outStr=""
            response, ip = socket.recvfrom(1024)
            if response == 'ok':
                continue
            outStr = 'Tello State:' + str(response)
            print(outStr)
            sleep(0.2)
    except KeyboardInterrupt:
        pass
    '''
