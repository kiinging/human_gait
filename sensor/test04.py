# 25-3-2023
# Display data on PC
# I need to read another code in VS code to plot the results using matplotlib function

import machine
from machine import I2C, Pin, Timer
import uasyncio
import time
import utime
from machine import I2C, Pin
from mpu9250 import MPU9250
from mpu6500 import MPU6500, SF_G, SF_DEG_S
from ak8963 import AK8963
from fusion import Fusion
from config import offsetMag, scaleMag, offsetAccel, scaleAccel
import micropython
import ujson

micropython.alloc_emergency_exception_buf(100)

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


async def read_sensor(delay):
    increment = 0
    counter = 0
    while True:
        # Calculate delta time since last update
        lastUpdate = utime.ticks_us()

        dict = {}
        # read accelerometer, gyro, and magnetic sensor readings
        accel_raw, gyro_raw, mag_raw = sensor.acceleration, sensor.gyro, sensor.magnetic     
        # modify accelerometer and gyro readings
        
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
        
        # convert lists back to tuples before using them in imu.update method
        accel_mod = tuple((-accel_raw[1], -accel_raw[0], accel_raw[2]))
        gyro_mod = (gyro_raw[1], gyro_raw[0], -gyro_raw[2])
               
        # update the IMU sensor with the modified sensor readings
        imu.update(accel_mod, gyro_mod, mag_raw)
        head = imu.heading
        pitch = imu.pitch
        roll = imu.roll
        ypr=(head,pitch,roll)
        
        # print every 8th sample
        increment += 1
        if increment % 5 == 0:
            dict["accel"]=accel_raw
            dict["gyro"] =gyro_raw
            dict["mag"]  =mag_raw
            dict["ypr"]  =ypr
            dict["counter"]  =counter
            jsonStr=ujson.dumps(dict)
            print(jsonStr)
            counter += 1
        
        await uasyncio.sleep_ms(delay)
    
# The original Madgwick study indicated that an update rate of 10-50Hz was adequate for accurate results
async def main():  
    uasyncio.create_task(read_sensor(20)) # Sample at 20mS
    while True:
        await uasyncio.sleep_ms(10_000)
    print("done")
 
uasyncio.run(main())
