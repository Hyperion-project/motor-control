__author__ = 'Maarten'

import time
import math

import serial
from multibus import BusCore, BusServer, BusClient


def findController():
    for i in range(256):
        try:
            #open serial to controller
            s = serial.Serial(i, 9600, timeout=2)
            time.sleep(2)

            #handshake with THE answer
            s.write(chr(0x42))
            test = s.readline()
            if test == chr(0x41):
                return s
        except (error) as e:
            print(e)
            pass


def sendAction(ser, motor, angle):
    #Send actions
    ser.write(chr(0xF0))
    ser.write(chr(motor))
    ser.write(str(angle)+"\n")
    ser.write(chr(0x0F))
    ser.flush()

    #wait for 10 seconds
    for i in range(10):
        test = ser.read();
        if test == chr(0x44):
            return True
    return False


if __name__ == '__main__':
    print("Motor controller Server: init")
    s = BusServer.BusServer(15001)
    s.listen()
    myAngle = 0
    while True:
        packet = s.getPacket()
        if packet.action == BusCore.PacketType.SETMOTOR:
            motor = {
                'A': 0x01,
                'B': 0x02,
                'C': 0x03
            }.get(packet.data['motor'])

            angle = packet.data['angle'] % 360
            steps = myAngle - angle;
            ser = findController()
            if ser is not None:
                 result = sendAction(ser, motor, angle)
                 if packet.data['returnport'] is not None:
                    c = BusClient.BusClient(packet.data['returnport'])
                    try:
                        c.send(BusCore.Packet(BusCore.PacketType.SETMOTOR, {'result': result}))
                    except:
                        print("Motor controller Server: failed to send done")
                 ser.close()