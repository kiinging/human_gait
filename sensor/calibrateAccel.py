# print the accelerometer data and use the python code in VS code to read
# and store the data for calibration purposes.
# The code print comma-separated values (CSV) from the serial port, with
# each line of input representing one set of accelerometer measurements.

import utime
from machine import I2C, Pin
from mpu9250 import MPU9250
from mpu6500 import MPU6500, SF_G, SF_DEG_S

i2c = I2C(scl=Pin(22), sda=Pin(21))
mpu6500 = MPU6500(i2c, accel_sf=SF_G, gyro_sf=SF_DEG_S)
sensor = MPU9250(i2c, mpu6500=mpu6500)

print("MPU9250 id: " + hex(sensor.whoami))

while True:
    accel = sensor.acceleration
    print(str(accel[0]) + "," + str(accel[1]) + "," + str(accel[2]))

    utime.sleep_ms(20)