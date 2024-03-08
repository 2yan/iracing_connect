import irsdk
import os
import win32api
import win32process
import win32con
import serial
import queue
import threading
import time



def set_high_priority():
    handle = win32api.OpenProcess(win32con.PROCESS_ALL_ACCESS, True, os.getpid())
    win32process.SetPriorityClass(handle, win32process.REALTIME_PRIORITY_CLASS) # you could set this to REALTIME_PRIORITY_CLASS etc.


def get_text():
    text = f"$IRTEL,{ir['SessionTime']:.3f},{ir['EnterExitReset']:d},{ir['Lap']:d},{ir['LapDistPct']:f},{int(ir['OnPitRoad']):d},0.000000,0.000000,0.000000,{ir['Speed']:f},{ir['ThrottleRaw']:f},{ir['BrakeRaw']:f},{ir['SteeringWheelAngle']:f},{ir['RPM']:f},{ir['VelocityX']:f},{ir['VelocityY']:f},{ir['VelocityZ']:f},{ir['LatAccel']:f},{ir['LongAccel']:f},{ir['VertAccel']:f},{ir['YawRate']:f},{ir['PitchRate']:f},{ir['RollRate']:f},{ir['Pitch']:f},{ir['Roll']:f},{ir['YawNorth']:f}"
    return text


def get_telemetry_data():
    global data_queue
    lag = .05
    last = time.time()
    
    status = 'not connected'
    while True:
        try:
            if ir.is_connected:
                if not(ir['IsInGarage']):
                    if status == 'not connected':
                        print('Starting Logging')
                    status = 'connected'
                    text = get_text()
                    data_queue.put(text)
                    now = time.time()
                    delta = now - last
                    time.sleep(max(lag - delta, .0000001))
                    last = now
                else:
                    if status == 'connected':
                        print('disconnected')
                    status = 'not connected'
            else: 
                if status == 'connected':
                    print('disconnected')
                status = 'not connected'
        except Exception as e:
            pass
                



def send_to_bluetooth():
    while True:
        texts = []
        if not data_queue.empty():
            texts.append(data_queue.get())
            
        if len(texts) > 0:
            data = ''.join(texts)+ '\n'
            s.write(data.encode()) 
            texts = []

            


set_high_priority()
print('priority set')

data_queue = queue.Queue()
print('Que setup')

ir = irsdk.IRSDK()
ir.startup()
print('Iracing Connected')

s = serial.Serial('COM8', 115200,)
print('serial connected')

    


ir_thread = threading.Thread(target=get_telemetry_data)
b_thread = threading.Thread(target=send_to_bluetooth)

ir_thread.start()
b_thread.start()