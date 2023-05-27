# 23-3-2023
# MPU9250 has two devices, the magnetometer and the accelerometer-gyro on the same board.
# The axes of these two devices are different.
# The axes of accelerometer-gyro is align with the magnetometer to obtain NED coordination.
# The testing shows that the orientation results are correct.

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
from config import offset, scale
import micropython

micropython.alloc_emergency_exception_buf(100)

offset = offset
scale  = scale

i2c = I2C(scl=Pin(22), sda=Pin(21))
dummy = MPU9250(i2c) # this opens the bybass to access to the AK8963
ak8963 = AK8963(
    i2c,
    offset=offset,
    scale=scale
)
mpu6500 = MPU6500(i2c, accel_sf=SF_G, gyro_sf=SF_DEG_S) # Fusion expects deg/s
sensor = MPU9250(i2c, mpu6500=mpu6500, ak8963=ak8963)

print("start gyro calibration")
gyro_offset=sensor.calibrate()
print("completed gyro calibration")

imu = Fusion()

async def read_sensor(delay):
    counter = 0
    while True:
        # read accelerometer, gyro, and magnetic sensor readings
        accel_raw, gyro_raw, mag_raw = sensor.acceleration, sensor.gyro, sensor.magnetic
        
        # modify accelerometer and gyro readings
        accel_mod = (-accel_raw[1], -accel_raw[0], accel_raw[2])
        gyro_mod = (gyro_raw[1], gyro_raw[0], -gyro_raw[2])
               
        # update the IMU sensor with the modified sensor readings
        imu.update(accel_mod, gyro_mod, mag_raw)
        
        # print every 10th sample
        counter += 1
        if counter % 8 == 0:
            print("Heading: {:3.1f}, Pitch: {:3.1f}, Roll : {:3.1f}".format(imu.heading, imu.pitch, imu.roll))
        
        await uasyncio.sleep_ms(delay)
    

async def main():  
    uasyncio.create_task(read_sensor(100))
    while True:
        await uasyncio.sleep_ms(10_000)
    print("done")
 
uasyncio.run(main())