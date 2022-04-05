import logging
import contextlib
from re import T
import socket
import sys
import time
from unittest.mock import DEFAULT
from xml.dom.expatbuilder import theDOMImplementation

logging.basicConfig(level=logging.INFO, stream=sys.stdout)
logger=logging.getLogger(__name__)

DEFAULT_DISTANCE=0.30 # drone move 길이 => 30cm
DEFAULT_SPEED=10 # drone speed
DEFAULT_DEGREE=10 # drone degree

class DroneManager(object):
    def __init__(self, host_ip='192.168.10.2', host_port=8889, 
                 drone_ip='192.168.10.1',drone_port=8889,
                 is_imperial=False,speed=DEFAULT_SPEED): # is_imperial은 대충 영국의 길이 기준? 이런거 말하는 건데 false로 설정!
        self.host_ip=host_ip
        self.host_port=host_port
        self.drone_ip=drone_ip
        self.drone_port=drone_port
        self.drone_address=(drone_ip,drone_port)
        self.is_imperial=is_imperial
        self.speed=speed
        #self.socket=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        #self.socket.bind((self.host_ip,self.host_port))
        #self.send_command('command')
        #self.send_command('streamon')
        self.set_speed(self.speed)
        
    def __dell__(self):
        self.stop()
        
    def stop(self):
        self.socket.close()
        
    def send_command(self,command):
        logger.info({'action':'send_command','command':command}) # drone command log in terminal
        # self.socket.sendto(command.encode('utf-8'),self.drone_address) drone에 command 전송
        
    def takeoff(self):
        self.send_command('takeoff')
        
    def land(self):
        self.send_command('land')
        
    def set_speed(self,speed):
        return self.send_command(f'speed {speed}')
    
    def clockwise(self,degree=DEFAULT_DEGREE): # 시계 방향
        return self.send_command(f'cw {degree}')
    
    def counter_clockwise(self,degree=DEFAULT_DEGREE): # 반시계 방향
        return self.send_command(f'ccw {degree}')
    
    def flip(self,direction):
        return self.send_command(f'flip {direction}')
    
    def flip_left(self):
        return self.flip('l')
    
    def flip_right(self):
        return self.flip('r')
    
    def flip_forward(self):
        return self.flip('f')
    
    def flip_back(self):
        return self.flip('b')
    
    def move(self, direction, distance):
        distance=float(distance)
        if self.is_imperial:
            distance=int(round(distance*30.48)) # cm 기준으로 변환
        else:
            distance=int(round(distance*100))
        return self.send_command(f'{direction} {distance}')
    
    def up(self,distance=DEFAULT_DISTANCE):
        return self.move('up',distance)
    
    def down(self,distance=DEFAULT_DISTANCE):
        return self.move('down',distance)
    
    def left(self,distance=DEFAULT_DISTANCE):
        return self.move('left',distance)
    
    def right(self,distance=DEFAULT_DISTANCE):
        return self.move('right',distance)
    
    def forward(self,distance=DEFAULT_DISTANCE):
        return self.move('forward',distance)
    
    def back(self,distance=DEFAULT_DISTANCE):
        return self.move('back',distance)

    def streamon(self):
        self.send_command('streamon')

    def streamoff(self):
        self.send_command('streamoff')

    def hover(self):
        self.send_command('stop')
        
if __name__=='__main__':
    drone_manager=DroneManager()
    drone_manager.takeoff()
    drone_manager.streamon()
    
    drone_manager.flip_back()
    
    drone_manager.set_speed(100)
    
    time.sleep(5)
    
    drone_manager.land()
    drone_manager.up()