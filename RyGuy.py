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
    CONNECTED_NOT_ON_TRACK = "Connected - Car Not on track"
    GAME_NOT_STARTED = "Waiting For Game"
    BOOTING = 'Booting'
    CRASHED = 'CRASHED'
    GAME_STARTED = "Game Loading"

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
                print('\n')
                print("Device Found", line)
                print('\n')
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
        
        self.max_time = 0
        
        print("Booted")

        return 
    
    
    
               
    def get_text(self):
        ir = self.ir
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
                    self.serial = serial.Serial(self.port, 115200, timeout=3)
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
                
            if (self.iracing_status != IRacingStatus.CONNECTED_ON_TRACK) and (self.serial_status == SerialStatus.CONNECTED):
                blank = iracing.get_blank()
                self.max_time = self.max_time + .1
                blank = blank.replace('TIME', f'{self.max_time:.3f}')
                if '\n' not in blank:
                    blank = blank + '\n'
                time.sleep(.1)
                try:
                    self.send_data(blank)
                except Exception as e:
                    continue

                
            
            serial_status = self.serial_status.value
            iracing_status = self.iracing_status.value
            port = self.port
            if port == False:
                port = ''
                
            print(f"""\r Iracing:{iracing_status} XX RyGuy:{serial_status} XX {port} XX Queue Size:{r.data_queue.qsize()} XX DATASPEED {i}       """, end = '')

            
        
    def data_pull_loop(self):        
        while True:
            if (self.iracing_status == IRacingStatus.CONNECTED_ON_TRACK) and  (self.serial_status == SerialStatus.CONNECTED):
                text = self.get_text()
                self.last_message = self.ir['SessionTime']
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
                    
                if len(texts) > 0:
                    data = ''.join(texts)+ '\n'
                    self.send_data(data)
                    texts = []
            else: 
                return 

    def send_data(self, data):
        self.serial.write(data.encode()) 
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
instructions = """
Instructions:

1. Make Sure this is your computer that will run iRacing. 
2. Plug in the RyGuy Adapter. The status will change to "RyGuy:Connected" from "RyGuy:Device not Found""
3. On your Phone Connect to the Adapter via Bluetooth. 
4. Boot Solostorm

Next is:
SOLOSTORM SETTINGS

Under Application Settings:

GPS/Logger >
     GPS/ Logger Source 
     > Select iRacing + Bluetooth Telemetry
     Bluetooth Device
     > Select RyGuysAdapter (You might need to connect your phone to it first)
     > Secure Bluetooth Connection - Leave Unchecked.

Vehicle Telemetry>
Select None / GPS Logger

New Event > Race Mode: Timeattack and Select your circuit. Automatic circuit detection doesn't work YET.

Logger and Maths Channels: 
RPM
Throttle
Brakes
and Steering Angle are available. Select Iracing <variable>



"""
if __name__ == '__main__':

    print("Welcome To RyGuy Version 1.0 - Beta")
    print(instructions)
    input('PRESS ENTER TO CONTINUE')
    r = Robot()
    r.run()