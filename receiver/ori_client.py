 # This example use aioble library
 # Receive orientation data
 # working !!.. (29-4-2023)
 # 

import sys
sys.path.append("")

from micropython import const
import uasyncio as asyncio
import aioble
import bluetooth

import random
import struct

# org.bluetooth.service.environmental_sensing
_MPU9250_UUID = bluetooth.UUID(0x181A)
# org.bluetooth.characteristic.temperature
_MPU9250_ORIENT_UUID = bluetooth.UUID(0x2A6E)


# Helper to decode the temperature characteristic encoding (sint16, hundredths of a degree).
def _decode_orientation(data):
    return  data.decode()
           
           
async def find_MPU9250_sensor():
    aioble.config(rxbuf=512)  # increase the receive buffer size to 512 bytes
    # Scan for 5 seconds, in active mode, with very low interval/window (to
    # maximise detection rate).
    async with aioble.scan(5000, interval_us=30000, window_us=30000, active=True) as scanner:
        async for result in scanner:
            # See if it matches our name and the environmental sensing service.
            if result.name() == "mpy-mpu9250" and _MPU9250_UUID in result.services():
                return result.device
    return None


async def main():
    device = await find_MPU9250_sensor()
    if not device:
        print("MPU9250 sensor not found")
        return

    try:
        print("Connecting to", device)
        connection = await device.connect()
        
        
    except asyncio.TimeoutError:
        print("Timeout during connection")
        return

    async with connection:
        try:
            orient_service = await connection.service(_MPU9250_UUID)
            orient_characteristic = await orient_service.characteristic(_MPU9250_ORIENT_UUID)
            mtu = await connection.exchange_mtu(256)  # negotiate an MTU of 256 bytes
            print("MTU negotiated:", mtu)
        except asyncio.TimeoutError:
            print("Timeout discovering services/characteristics")
            return

        while True:
            data = _decode_orientation(await orient_characteristic.read())
            # convert the 16-bit integer values back to float values
            print(data)
            await asyncio.sleep_ms(100)


asyncio.run(main())