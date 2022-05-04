import socket
from time import sleep

   
if __name__ == "__main__":
    local_ip = ''
    local_port = 8890 ## read port
    socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # socket for sending cmd
    socket.bind((local_ip, local_port))

    tello_ip = '192.168.10.1'
    tello_port = 8889 ## write port
    tello_address = (tello_ip, tello_port)
    socket.sendto('command'.encode('utf-8'), tello_address) ## Enter SDK Mode   
    socket.sendto('battery?'.encode('utf-8'), tello_address) ## Enter SDK Mode   
    response,ip = socket.recvfrom(1024)
    outStr = 'Tello Battery:' + str(response.decode())
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