# Test uasynchio
# Test mpu9250 and
# double click to calibrate magnetometer
# long click to calibrate gyro

from machine import Pin, I2C
import uasyncio as asyncio
from primitives import Pushbutton
import time
from mpu9250 import MPU9250
from mpu6500 import MPU6500, SF_G, SF_DEG_S
from ak8963 import AK8963

i2c = I2C(1, scl=Pin(22), sda=Pin(21))
mpu6500 = MPU6500(i2c, accel_sf=SF_G, gyro_sf=SF_DEG_S)
dummy = MPU9250(i2c) # this opens the bybass to access to the AK8963
ak8963 = AK8963(
    i2c,
    offset=(11.75362, 25.68516, -13.80234),
    scale=(1.025053, 0.9591727, 1.018459)   
)
sensor = MPU9250(i2c, mpu6500=mpu6500, ak8963=ak8963)
   
async def calibMag(led, period_ms):
    for x in range(6):
        led.on()
        await asyncio.sleep_ms(int(period_ms/4))
        led.off()
        await asyncio.sleep_ms(period_ms)
    offset, scale = ak8963.calibrate(count=256, delay=200)
    print("offset: {}".format(offset))
    print("scale:  {}".format(scale))   
    for x in range(6):
        led.on()
        await asyncio.sleep_ms(int(period_ms/4))
        led.off()
        await asyncio.sleep_ms(period_ms)

async def calibGyro(led, period_ms):
    for x in range(6):
        led.on()
        await asyncio.sleep_ms(int(period_ms/4))
        led.off()
        await asyncio.sleep_ms(period_ms)
    gyro = sensor.calibrate()
    print("offset: {}".format(gyro))

    for x in range(6):
        led.on()
        await asyncio.sleep_ms(int(period_ms/4))
        led.off()
        await asyncio.sleep_ms(period_ms)


async def my_app():
    red  = Pin(19, Pin.OUT)
    blue = Pin(23, Pin.OUT)
    pin     = Pin(4,  Pin.IN, Pin.PULL_UP)

    pb = Pushbutton(pin)
    pb.double_func(calibMag, (red,100))  # Note how function and args are passed
    pb.long_func(calibGyro, (blue,100))  # Note how function and args are passed
    
    
    while True:
        fstr = 'accel:{:.2f},{:.2f},{:.2f} gyro:{:.2f},{:.2f},{:.2f} mag:{:.2f},{:.2f},{:.2f}'         
        print(fstr.format(sensor.acceleration[0], sensor.acceleration[1], sensor.acceleration[2],
                          sensor.gyro[0], sensor.gyro[1], sensor.gyro[2],
                          sensor.magnetic[0], sensor.magnetic[1], sensor.magnetic[2]))
        await asyncio.sleep(1)  # Dummy
        
    print("done")  # program will not come here

asyncio.run(my_app())  # Run main application code

# Calibrated at 14-10-2022
# offset: (36.00352, 70.43027, -54.46934)
# scale:  (1.023896, 1.013462, 0.9646728)

