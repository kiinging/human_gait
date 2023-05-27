# Test uasynchio
# Test pushbutton 

from machine import Pin
import uasyncio as asyncio
from primitives import Pushbutton
import time

def pulse(led, period_ms):
    led.on()
    await asyncio.sleep_ms(period_ms)
    led.off()

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
    pb.long_func(pulse, (red,4000))  # Note how function and args are passed
    pb.double_func(pulse, (red,8000))  # Note how function and args are passed
#    pb.press_func(pulse, (red,500))  # Note how function and args are passed
    asyncio.create_task(blink(blue, 500))
    
    while True:
        await asyncio.sleep(60)  # Dummy
        
    print("done")  # program will not come here

asyncio.run(my_app())  # Run main application code

