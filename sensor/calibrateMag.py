# Magnetometer Calibration
from machine import I2C, Pin
from mpu9250 import MPU9250
from ak8963 import AK8963

i2c = I2C(scl=Pin(22), sda=Pin(21))

dummy = MPU9250(i2c) # this opens the bybass to access to the AK8963
ak8963 = AK8963(i2c)
print("start calibration")
offset, scale = ak8963.calibrate(count=256, delay=200)
print("complete calibration")
sensor = MPU9250(i2c, ak8963=ak8963)

print("offset:", offset)
print("scale:", scale)