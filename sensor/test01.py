# Test uasynchio
# Test mpu9250 and
# double click to calibrate magnetometer

from machine import Pin, I2C
import uasyncio as asyncio
from primitives import Pushbutton
import time
from mpu9250 import MPU9250
from ak8963 import AK8963

i2c = I2C(1, scl=Pin(22), sda=Pin(21))

dummy = MPU9250(i2c) # this opens the bybass to access to the AK8963
ak8963 = AK8963(i2c)


sensor = MPU9250(i2c, ak8963=ak8963)
   

async def calibrate(led, period_ms):
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

async def blink(led, period_ms):
    while True:
        led.on()
        await asyncio.sleep_ms(500)
        led.off()
        await asyncio.sleep_ms(period_ms)
        

async def my_app():
    red  = Pin(19, Pin.OUT)
    blue = Pin(23, Pin.OUT)
    pin     = Pin(4,  Pin.IN, Pin.PULL_UP)

    pb = Pushbutton(pin)
    pb.double_func(calibrate, (red,100))  # Note how function and args are passed
#    pb.double_func(calibrate, (red))  # Note how function and args are passed
    asyncio.create_task(blink(blue, 500))
    
    while True:
        await asyncio.sleep(60)  # Dummy
        
    print("done")  # program will not come here

asyncio.run(my_app())  # Run main application code

# Calibrated at 14-10-2022
# offset: (36.00352, 70.43027, -54.46934)
# scale:  (1.023896, 1.013462, 0.9646728)

