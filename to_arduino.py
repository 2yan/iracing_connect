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

def get_telemetry_data():
    global data_queue
    lag = .05
    last = time.time()
    
    status = 'not connected'
    last_message = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
    while True:
        try:
            if ir.is_connected:
                if not(ir['IsInGarage']):
                    if status == 'not connected':
                        print('Starting Logging')
                    status = 'connected'
                    text = get_text()
                    if last_message[16:] != text[16:]:    
                        data_queue.put(text)
                        last_message =  text
                        
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
    texts = []
    while True:
        if not data_queue.empty():
            texts.append(data_queue.get())
            
        if len(texts) > 5:
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