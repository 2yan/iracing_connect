# -*- coding: utf-8 -*-
"""
Created on Fri Mar  8 17:16:00 2024

@author: Rdrac
"""

import win32api
import win32process
import win32con
import os
import iracing
from enum import Enum
import irsdk
import threading
import time
import serial.tools.list_ports as list_ports
import serial
import queue

class IRacingStatus(Enum):
    CONNECTED_ON_TRACK = "Connected - On Track!"
    CONNECTED_NOT_ON_TRACK = "Connected - Not on track"
    GAME_NOT_STARTED = "Game Not Started"
    BOOTING = 'Booting'
    CRASHED = 'CRASHED'
    GAME_STARTED = "Game Started"

class SerialStatus(Enum):
    CONNECTED = 'Connected'
    SEARCHING = 'Searching'
    BOOTING = 'Booting'
    DEVICE_FOUND = "Device Found"
    DEVICE_NOT_FOUND = "Device Not Found"
    DISCONNECTED = "Disconnected"

def find_port():
    ports = list_ports.comports()
    for port, desc, hwid in sorted(ports):
        try:
            ser = serial.Serial(port, 115200, timeout=1)
            line = ser.readline().decode().strip()
            if "ID: RyGuysAdapter" in line:
                ser.close()
                return port
            ser.close()
        except:
            pass
    return False





def launch(f):
    t = threading.Thread(target=f)
    t.start()
    return t

            
def get_text(ir):

    session_time = ir['SessionTime']
    enter_exit_reset = ir['EnterExitReset']
    lap = ir['Lap']
    lap_dist_pct = ir['LapDistPct']
    on_pit_road = int(ir['OnPitRoad'])
    speed = ir['Speed']
    throttle_raw = ir['ThrottleRaw']
    brake_raw = ir['BrakeRaw']
    steering_wheel_angle = ir['SteeringWheelAngle']
    rpm = ir['RPM']
    velocity_x = ir['VelocityX']
    velocity_y = ir['VelocityY']
    velocity_z = ir['VelocityZ']
    lat_accel = ir['LatAccel']
    long_accel = ir['LongAccel']
    vert_accel = ir['VertAccel']
    yaw_rate = ir['YawRate']
    pitch_rate = ir['PitchRate']
    roll_rate = ir['RollRate']
    pitch = ir['Pitch']
    roll = ir['Roll']
    yaw_north = ir['YawNorth']
    
    text = f"$IRTEL,{session_time:.3f},{enter_exit_reset:d},{lap:d},{lap_dist_pct:f},{on_pit_road:d},0.000000,0.000000,0.000000,{speed:f},{throttle_raw:f},{brake_raw:f},{steering_wheel_angle:f},{rpm:f},{velocity_x:f},{velocity_y:f},{velocity_z:f},{lat_accel:f},{long_accel:f},{vert_accel:f},{yaw_rate:f},{pitch_rate:f},{roll_rate:f},{pitch:f},{roll:f},{yaw_north:f}"

    return text 


    
    
class Robot:
    
        
    def __init__(self):

        # Initalize variables
        self.serial_status = SerialStatus.BOOTING
        self.iracing_status = IRacingStatus.CONNECTED_ON_TRACK
        self.serial = False
        self.last_message = 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXx'
        self.ir = False
        self.port = False
        self.data_queue = queue.Queue()
        
        self.data_pull_thread = False
        self.data_send_thread = False
        
        self.stop_pull = False
        self.stop_send = False
        
        
        
        return 
    



    def run(self):
        i = 0
        while True:
            i = i + 1
            if i > 60:
                i = 0
            
            
            if iracing.sim_is_on():
                self.iracing_status = IRacingStatus.GAME_STARTED
                
                if self.ir: 
                    if self.ir.is_connected and self.ir.is_initialized:
                       if self.ir['IsOnTrack']:
                           self.iracing_status = IRacingStatus.CONNECTED_ON_TRACK
                       else:
                           self.iracing_status = IRacingStatus.CONNECTED_NOT_ON_TRACK
                    else:
                        self.ir.startup()
                else:
                    self.ir = irsdk.IRSDK()
                    self.ir.startup()
            else:
                self.iracing_status = IRacingStatus.GAME_NOT_STARTED
                if self.ir:
                    self.ir.shutdown()
                

                

                    
                    
            if not(self.serial):
                if (not self.port): 
                    self.serial_status = SerialStatus.SEARCHING
                    self.set_port()
                    
                if self.port and (self.serial_status == SerialStatus.DEVICE_FOUND):
                    self.serial = serial.Serial(self.port, 115200,)
                    self.serial_status = SerialStatus.CONNECTED
                
            elif self.plugged_in():
                self.serial_status = SerialStatus.CONNECTED
            else:
                self.serial.close()
                self.serial_status = SerialStatus.DISCONNECTED
                self.port = False
                self.serial = False
                
            # CHECK THE DATA PULL LOOP
            if not(self.data_pull_thread):
                if (self.iracing_status == IRacingStatus.CONNECTED_ON_TRACK) and  (self.serial_status == SerialStatus.CONNECTED):
                    self.data_pull_thread = launch(self.data_pull_loop)
            else:
                if not(self.data_pull_thread.is_alive()):
                    self.IRacingStatus = IRacingStatus.CRASHED
                    self.data_pull_thread = False
                
            if not(self.data_send_thread):
                if (self.iracing_status == IRacingStatus.CONNECTED_ON_TRACK) and  (self.serial_status == SerialStatus.CONNECTED):
                    self.data_send_thread = launch(self.data_send_loop)
            else:
                if not(self.data_send_thread.is_alive()):
                    self.serial_status = SerialStatus.DISCONNECTED
                    self.data_send_thread = False
                
            serial_status = self.serial_status.value
            iracing_status = self.iracing_status.value
            port = self.port
            if port == False:
                port = ''
                
            print(f"""\r IRACING Status:{iracing_status} RyGuy STATUS: {serial_status} - {port}| Queue Size:{r.data_queue.qsize()} : DATASPEED {i}      """, end = '')

            
        
    def data_pull_loop(self):        
        while True:
            if (self.iracing_status == IRacingStatus.CONNECTED_ON_TRACK) and  (self.serial_status == SerialStatus.CONNECTED):
                text = get_text(self.ir)
                self.data_queue.put(text)
                time.sleep(.1)
                self.last_message = text
            else:
                
                return 
                
                
    def data_send_loop(self):
        texts = []
        
        while True:
            if (self.iracing_status == IRacingStatus.CONNECTED_ON_TRACK) and  (self.serial_status == SerialStatus.CONNECTED):
                if not self.data_queue.empty():
                    texts.append(self.data_queue.get())
                    
                if len(texts) > 5:
                    data = ''.join(texts)+ '\n'
                    self.serial.write(data.encode()) 
                    texts = []
            else: 
                
                return 
                    

        
    def set_port(self):
        port = find_port()
        self.port = port
        if port: 
            self.serial_status = SerialStatus.DEVICE_FOUND
        else:
            self.serial_status = SerialStatus.DEVICE_NOT_FOUND
    

        
    def plugged_in(self):
        my_port = self.port
        ports = list_ports.comports()
        for port, desc, hwid in sorted(ports):
            if my_port == port:
                return True
        return False

    

handle = win32api.OpenProcess(win32con.PROCESS_ALL_ACCESS, True, os.getpid())
win32process.SetPriorityClass(handle, win32process.REALTIME_PRIORITY_CLASS) # you could set this to REALTIME_PRIORITY_CLASS etc.

if __name__ == '__main__':
    r = Robot()
    r.run()