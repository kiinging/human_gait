import serial
import json

class SerialDataInput:
    """ Reads data from the serial port """
    """ Data from imu in json string"""

    def __init__(self, device, baud):
        self.port = serial.Serial(device, baud) # Connect to the device on serial port
        self.port.readline() # FIXME: Skip the first line, so we don't parse partial data
    
    def read(self):
        """ Reads sensor data and parses it """
        raw_line = self.port.readline()
        values = json.loads(raw_line)
        return values