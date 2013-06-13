__author__ = 'Maarten'

import time
import math

import serial
from multibus import BusCore, BusServer


def findController():
    for i in range(256):
        try:
            #open serial to controller
            s = serial.Serial(i, 9600, timeout=1)
            time.sleep(2)

            #handshake with THE answer
            s.write(0x42)
            if s.read(0x41):
                return s
        except (serial.SerialException, serial.SerialTimeoutException) as e:
            print(e)
            pass


def sendAction(ser, motor, angle):
    #Send actions
    ser.send(0x10)
    ser.send(motor)
    ser.send(angle)
    ser.flush()

    #wait for 10 seconds
    for i in range(10):
        if ser.read() > 0:
            return True
    return False


if __name__ == '__main__':
    print("Motor controller Server: init")
    s = BusServer.BusServer(15001)
    s.listen()
    while True:
        packet = s.getPacket()
        if packet.action == BusCore.PacketType.SETMOTOR:
            motor = {
                'A': 0x01,
                'B': 0x02,
                'C': 0x03
            }.get(packet.data.motor)

            angle = math.mod(packet.data.angle, 360)
            ser = findController()
            if ser is not None:
                sendAction(ser, motor, angle)
            ser.close()