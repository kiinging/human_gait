# This file is executed on every boot (including wake-boot from deepsleep)
#import esp
#esp.osdebug(None)
#import webrepl
#webrepl.start()
import sys
sys.path.append('/mpu9250Lib')
sys.path.append('/fusionLib')
sys.path.append('/mqttLib')
sys.path.append('/lib')
sys.path.append('/aioble')
