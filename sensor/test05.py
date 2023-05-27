# 25-3-2023
# Display data on PC
# I need to run another code in VS code to plot the results using matplotlib function
# add Bluetooth -26-4-2023

import bluetooth
import random
import struct
import time
from ble_advertising import advertising_payload
from micropython import const

import machine
from machine import I2C, Pin, Timer
import uasyncio
import utime
from mpu9250 import MPU9250
from mpu6500 import MPU6500, SF_G, SF_DEG_S
from ak8963 import AK8963
from fusion import Fusion
from config import offsetMag, scaleMag, offsetAccel, scaleAccel
import micropython
import ujson

micropython.alloc_emergency_exception_buf(100)

# Define maximum characteristic size
MAX_CHAR_SIZE = const(100)

offsetMag = offsetMag
scaleMag  = scaleMag
offsetAccel = offsetAccel
scaleAccel  = scaleAccel

i2c = I2C(scl=Pin(22), sda=Pin(21))
dummy = MPU9250(i2c) # this opens the bybass to access to the AK8963
ak8963 = AK8963(
    i2c,
    offset=offsetMag,
    scale=scaleMag
)
mpu6500 = MPU6500(i2c, accel_sf=SF_G, gyro_sf=SF_DEG_S) # Fusion expects deg/s
sensor = MPU9250(i2c, mpu6500=mpu6500, ak8963=ak8963)

print("start gyro calibration")
gyro_offset=sensor.calibrate()
print("completed gyro calibration")

imu = Fusion()

_IRQ_CENTRAL_CONNECT = const(1)
_IRQ_CENTRAL_DISCONNECT = const(2)
_IRQ_GATTS_INDICATE_DONE = const(20)

_FLAG_READ = const(0x0002)
_FLAG_NOTIFY = const(0x0010)
_FLAG_INDICATE = const(0x0020)

# MPU9250 service and characteristics UUIDs
_MPU9250_UUID = bluetooth.UUID(0x181A)
_ORIENTATION_CHAR = (
    bluetooth.UUID(0x2A6E),
    _FLAG_READ | _FLAG_NOTIFY | _FLAG_INDICATE,
)
_MPU9250_SERVICE = (
    _MPU9250_UUID,
    (_ORIENTATION_CHAR,),
)


class BLEMPU9250:
    def __init__(self, ble, name="mpy-mpu9250"):
        self._ble = ble
        
        self._ble.active(True)
        self._ble.config(mtu=256)
#        self._ble.config(rxbuf = 400)
#        print("MTU size:",self._ble.config('mtu'))
       
       # self._ble.gattc_exchange_mtu(100)
        self._ble.irq(self._irq)
        
        ((self._handle,),) = self._ble.gatts_register_services((_MPU9250_SERVICE,))
#         self._ble.gatts_set_buffer(self._handle, 400)
        self._connections = set()
        self._payload = advertising_payload(name=name, services=[_MPU9250_UUID] )
        self._advertise()
        
    def _irq(self, event, data):
        # Track connections so we can send notifications.
        if event == _IRQ_CENTRAL_CONNECT:
            conn_handle, _, _ = data
            self._connections.add(conn_handle)
        elif event == _IRQ_CENTRAL_DISCONNECT:
            conn_handle, _, _ = data
            self._connections.remove(conn_handle)
            # Start advertising again to allow a new connection.
            self._advertise()
        elif event == _IRQ_GATTS_INDICATE_DONE:
            conn_handle, value_handle, status = data

    def set_orientation(self, orientation_json, notify=False, indicate=False):
        # Convert JSON string to bytes
        data = orientation_json.encode()

        self._ble.gatts_write(self._handle, data)
        if notify or indicate:
            for conn_handle in self._connections:
                if notify:
                    # Notify connected centrals.
                    self._ble.gatts_notify(conn_handle, self._handle)
                if indicate:
                    # Indicate connected centrals.
                    self._ble.gatts_indicate(conn_handle, self._handle)

    def _advertise(self, interval_us=500000):
        self._ble.gap_advertise(interval_us, adv_data=self._payload)


###############################################

def read_sensor():
    # read accelerometer, gyro, and magnetic sensor readings
    accel_raw, gyro_raw, mag_raw = sensor.acceleration, sensor.gyro, sensor.magnetic     
    
    # convert tuples to lists for modification
    accel_raw = list(accel_raw)
        
    # Apply accel offset bias from calibration
    accel_raw[0] -= offsetAccel[0]
    accel_raw[1] -= offsetAccel[1]
    accel_raw[2] -= offsetAccel[2]

    # Apply accel scale bias from calibration
    accel_raw[0] *= scaleAccel[0]
    accel_raw[1] *= scaleAccel[1]
    accel_raw[2] *= scaleAccel[2]
        
    # convert lists back to tuples for accel and modify both accelerometer and gyro readings
    accel_mod = tuple((-accel_raw[1], -accel_raw[0], accel_raw[2]))
    gyro_mod = (gyro_raw[1], gyro_raw[0], -gyro_raw[2])
               
    # update the IMU sensor with the modified sensor readings
    imu.update(accel_mod, gyro_mod, mag_raw)
    head = imu.heading
    pitch = imu.pitch
    roll = imu.roll
    ypr=(head, pitch, roll)
    
    return ypr, accel_raw, gyro_raw, mag_raw

import bluetooth

def demo():
    ble = bluetooth.BLE()
    ori = BLEMPU9250(ble) # create instance of BLEMPU9250 class with modified BLE object

    # Perform the MTU exchange process
    conn_handle = 0x12 # Replace with the actual connection handle

    i = 0
    increment = 0
    counter = 0

    while True:
        ypr, accel_raw, gyro_raw, mag_raw = read_sensor()
     
        increment += 1
     
        if increment % 10 == 0:            
            dict={}
            dict["accel"]=[round(val, 4) for val in accel_raw] # data round to 3 decimal points
            dict["gyro"] =[round(val, 4) for val in gyro_raw]
            dict["mag"]  =[round(val, 4) for val in mag_raw]
            dict["ypr"]  =[round(val, 4) for val in ypr]
            dict["counter"]  =counter
            jsonStr=ujson.dumps(dict)
            i = (i + 1) % 10
            ori.set_orientation(jsonStr, notify=i == 0, indicate=False)
#            print(jsonStr)
      
            counter += 1  
        
        time.sleep_ms(10)


if __name__ == "__main__":
    demo()
        

    
