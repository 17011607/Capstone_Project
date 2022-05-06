import logging
import contextlib
from re import T
import socket
import sys
import time
import threading
import os
import subprocess
import cv2 as cv
import numpy as np
from unittest.mock import DEFAULT
from xml.dom.expatbuilder import theDOMImplementation
from base import Singleton
import drone_state

logging.basicConfig(level=logging.INFO, stream=sys.stdout)
logger=logging.getLogger(__name__)

DEFAULT_DISTANCE=0.30 # drone move 길이 => 30cm
DEFAULT_SPEED=100 # drone speed
DEFAULT_DEGREE=10 # drone degree

FRAME_X = int(960)
FRAME_Y = int(720)
FRAME_AREA = FRAME_X * FRAME_Y
FRAME_SIZE = FRAME_AREA * 3
FRAME_CENTER_X = FRAME_X / 2
FRAME_CENTER_Y = FRAME_Y / 2
CMD_FFMPEG = f'ffmpeg -hwaccel auto -hwaccel_device opencl -i pipe:0 -pix_fmt bgr24 -s {FRAME_X}x{FRAME_Y} -f rawvideo pipe:1'

class DroneManager(metaclass=Singleton):
    def __init__(self, host_ip='192.168.10.4', host_port=8889, 
                 drone_ip='192.168.10.1',drone_port=8889,
                 is_imperial=False,speed=DEFAULT_SPEED): # is_imperial은 대충 영국의 길이 기준? 이런거 말하는 건데 false로 설정!
        self.host_ip=host_ip
        self.host_port=host_port
        self.drone_ip=drone_ip
        self.drone_port=drone_port
        self.drone_address=(drone_ip,drone_port)
        self.is_imperial=is_imperial
        self.speed=speed
        self.socket=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        self.socket.bind((self.host_ip,self.host_port))
        
        self.response = None
        self.stop_event = threading.Event()
        self._response_thread = threading.Thread(target=self.receive_response, args=(self.stop_event))

        self._response_thread.start()
        
        self.proc = subprocess.Popen(CMD_FFMPEG.split(' '), stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        self.proc_stdin = self.proc.stdin
        self.proc_stdout = self.proc.stdout

        self.video_port = 11111

        self._receive_video_thread = threading.Thread(target=self.receive_video, args=(self.stop_event, self.proc_stdin, self.host_ip, self.video_port))
        self._receive_video_thread.start()

        self._command_semaphore = threading.Semaphore(1)
        self._command_thread = None
        self.send_command('command')
        self.send_command('streamon')
        self.set_speed(self.speed)
     
    def receive_response(self, stop_event):
        while not stop_event.is_set():
            try:
                self.response, ip = self.socket.recvfrom(3000)
                logger.info({'action' : 'receive_response', 'response' : self.response})
            except socket.error as ex:
                logger.error({'action' : 'receive response', 'ex' : ex})
                break
        
    def __dell__(self):
        self.stop()
        
    def stop(self):
        self.stop_event.set()
        retry = 0
        while self._response_thread.isAlive():
                time.sleep(0.3)
                if retry > 30:
                    break
                retry += 1
        self.socket.close()

        import signal # Windows
        os.kill(self.proc.pid, signal.CTRL_C_EVENT)
          
    def send_command(self, command, blocking=True):  # send_command(f"go {drone x} {drone y} {drone z} {spped} blocking =False)
        self._command_thread = threading.Thread(
            target=self._send_command,
            args=(command, blocking,))
        self._command_thread.start()
    
    def _send_command(self, command, blocking=True):
        is_acquire = self._command_semaphore.acquire(blocking=blocking)
        if is_acquire:
            with contextlib.ExitStack() as stack:
                stack.callback(self._command_semaphore.release)
                logger.info({'action': 'send_command', 'command': command})
                self.socket.sendto(command.encode('utf-8'), self.drone_address)

                retry = 0
                
                while self.response is None:
                    time.sleep(0.01)
                    if retry > 3:
                        break
                    retry += 1
                
                if self.response is None:
                    response = None
                else:
                    response = self.response.decode('utf-8')
                self.response = None
                return response
        else:
            logger.warning({'action': 'send_command', 'command': command, 'status': 'not_acquire'})
    '''        
    def send_command(self,command):
        logger.info({'action':'send_command','command':command}) # drone command log in terminal
        self.socket.sendto(command.encode('utf-8'),self.drone_address) #drone에 command 전송
    '''     
    def battery(self):
        status = drone_state.drone_status()
        return status.battery()
    
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
            distance=int(round(distance))
        return self.send_command(f'{direction} {distance}',blocking=False)
    
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

    def receive_video(self, stop_event, pipe_in, host_ip, video_port):
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock_video:
            sock_video.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock_video.settimeout(.5)
            sock_video.bind((host_ip, video_port))
            data = bytearray(2048)
            while not stop_event.is_set():
                try:
                    size, addr = sock_video.recvfrom_into(data)
                    #logger.info({'action':'receive_video', 'data':data})
                except socket.timeout as ex:
                    logger.warning({'action':'receive_video','ex':ex})
                    time.sleep(0.5)
                    continue
                except socket.error as ex:
                    logger.error({'action':'receive_video', 'ex':ex})
                    break

                try:
                    pipe_in.write(data[:size])
                    pipe_in.flush()
                except Exception as ex:
                    logger.error({'action' : 'receive_video', 'ex' : ex})
                    break
    
    def video_binary_generator(self):
        while True:
            try:
                frame = self.proc_stdout.read(FRAME_SIZE)
            except Exception as ex:
                logger.error({'action':'video_binary_generator', 'ex':ex})
                continue

            if not frame:
                continue

            frame = np.fromstring(frame, np.uint8).reshape(FRAME_Y, FRAME_X, 3)
            yield frame

    def video_jpeg_generator(self):
        for frame in self.video_binary_generator():
            _, jpeg = cv.imencode('.jpg', frame)
            jpeg_binary = jpeg.tobytes()
            yield jpeg_binary
        
if __name__=='__main__':
    drone_manager = DroneManager()
    drone_manager.takeoff()
    drone_manager.streamon()
    drone_manager.forward(20)
    drone_manager.forward(20)
    drone_manager.forward(20)
    drone_manager.forward(20)
    time.sleep(1)
    drone_manager.land()
