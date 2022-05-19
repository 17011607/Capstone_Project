import os
import sys
import socket

class TelloGestureController:
    def __init__(self):
        self._is_landing = False
        self.drone_ip='192.168.10.1'
        self.drone_port= 8889
        self.drone_address=(self.drone_ip,self.drone_port)
        self.socket=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)

        # RC control velocities
        self.forw_back_velocity = 0
        self.up_down_velocity = 0
        self.left_right_velocity = 0
        self.yaw_velocity = 0

    def gesture_control(self, gesture_buffer):
        gesture_id = gesture_buffer.get_gesture()
        print("GESTURE", gesture_id)

        if not self._is_landing:
            if gesture_id == 0:  # Stop
                self.forw_back_velocity = self.up_down_velocity = \
                    self.left_right_velocity = self.yaw_velocity = 0
            elif gesture_id == 1:  # Land
                self._is_landing = True
                self.forw_back_velocity = self.up_down_velocity = \
                    self.left_right_velocity = self.yaw_velocity = 0
                self.socket.sendto(f"land".encode('utf-8'), self.drone_address)
                
                self.socket.sendto(f"rc {self.left_right_velocity} {self.forw_back_velocity} {self.up_down_velocity} {self.yaw_velocity}".encode('utf-8'), self.drone_address)