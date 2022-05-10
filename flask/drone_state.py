import socket
from time import sleep


class drone_status():
    def __init__(self, drone_ip = '192.168.10.1', host_ip = '192.168.10.2'):
        self.host_ip = host_ip
        self.host_port = 8890
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((self.host_ip, self.host_port))

        self.tello_ip = drone_ip
        self.tello_port = 8889
        self.tello_address = (self.tello_ip, self.tello_port)

    def data_filter(self,key,data):
        if data.find(key) == -1:
            return data
        data=data.split(key)
        data=data[1].split(';')
        data=data[0].lstrip(':')
        return data

    def get_state(self):
        self.socket.sendto('command'.encode('utf-8'), self.tello_address) ## Enter SDK Mode
        response = 'ok'
        try:
            while response == 'ok' or response == b'ok':
                outstr = ""
                response, ip = self.socket.recvfrom(1024)
                sleep(0.2)
            outstr = str(response)              
        except KeyboardInterrupt:
            pass
        return outstr

    def print_state(self, state):
        '''
        state == bat : battery
        state == tof : tof sensor
        '''
        response = self.get_state()
        data = self.data_filter(state,response)
        return data


if __name__ == "__main__":
    status = drone_status(drone_ip = '192.168.137.198', host_ip = '192.168.137.196')
    while True:
        print(status.print_state("tof"))
        sleep(0.2)