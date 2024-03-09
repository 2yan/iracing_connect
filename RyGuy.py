# -*- coding: utf-8 -*-
"""
Created on Fri Mar  8 16:20:40 2024

@author: Rdrac
"""
import irsdk
import os
import win32api
import win32process
import win32con
import serial
import queue
import threading
import time
import serial.tools.list_ports as list_ports


def set_high_priority():
    handle = win32api.OpenProcess(win32con.PROCESS_ALL_ACCESS, True, os.getpid())
    win32process.SetPriorityClass(handle, win32process.REALTIME_PRIORITY_CLASS) # you could set this to REALTIME_PRIORITY_CLASS etc.

def find_port():
    ports = list_ports.comports()
    
    
    for port, desc, hwid in sorted(ports):
        try:
            ser = serial.Serial(port, 115200, timeout=1)
            start = time.time()
            now = time.time()
            while now - start < 5:
                line = ser.readline().decode().strip()
                if "ID: RyGuysAdapter" in line:
                    ser.close()
                    return port
                now = time.time()
            ser.close()
        except:
            pass
        
    return False


       


class Robot:
    
    def __init__(self):
        
        self.iracing_connected = False
        self.serial_connected = False
        
        print("Initalizing")
        
        set_high_priority()
        self.reset_queue()
        self.set_ir()
        
        
    def reset_queue(self):
        self.data_queue = queue.Queue()
        print('Data Initalized')
        
    def set_ir(self):
        ir = irsdk.IRSDK()
        ir.startup()
        self.ir = ir
        print("Iracing Connector Booted")
        
        
            
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

    def start_telemetry_thread(self):
        self.last_message = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
        self.get_thread = threading.Thread(target=self.__get_telemetry_data)
        self.get_thread.start()

    def start_sending_thread(self):
        self.send_thread = threading.Thread(target=self.send_to_bluetooth)
        self.send_thread.start()
        
    def __get_telemetry_data(self):
        ir = self.ir
        lag = .1
        last = time.time()
        
        while True:
            try:
                if ir.is_connected:
                    if not(ir['IsInGarage']):
                        text = self.get_text()
                        if self.last_message[16:] != text[16:]:    
                            self.data_queue.put(text)
                            self.last_message =  text
                            
                        now = time.time()
                        delta = now - last
                        time.sleep(max(lag - delta, .0000001))
                        last = now

            except Exception as e:
                print(f'Error {e}')
                pass
            
    def set_serial(self):
        self.serial_connected = False
        while True:
            port = find_port()
            if port:
                s = serial.Serial(port, 115200,)
                self.serial_connected = True
                self.serial = s
                return s
            time.sleep(1)
        
            
    def send_to_bluetooth(self):
        texts = []
        while True:
            try:
                if self.serial_connected:
                    if not self.data_queue.empty():
                        texts.append(self.data_queue.get())
                        
                    if len(texts) > 5:
                        data = ''.join(texts)+ '\n'
                        self.serial.write(data.encode()) 
                        texts = []
                else:
                    self.set_serial()
            except Exception as e:
                texts = [] # Clear Texts
                self.data_queue.get()# Clear Queue
                continue
    
    def run(self):
        self.start_telemetry_thread()
        self.start_sending_thread()
        while True:
            print(f"\rIRACING Connected: {self.iracing_connected} - RyGuy Connected {self.serial_connected} ", end = '')
    
if __name__ == '__main__':
    r= Robot()
    r.run()