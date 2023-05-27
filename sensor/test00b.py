# Testing using timer and interrupt.

from machine import Timer, Pin

ledRed=Pin(19, Pin.OUT)
ledBlue=Pin(23, Pin.OUT)
but=Pin(4,  Pin.IN)

def buttons_irq(pin):
    ledBlue.value(not ledBlue.value())
    
    
timer=Timer(0)
timer.init(period=1000, mode=Timer.PERIODIC, callback= lambda t: ledRed.value(not ledRed.value()))

but.irq(trigger=Pin.IRQ_FALLING, handler=buttons_irq)