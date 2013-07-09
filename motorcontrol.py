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
        except (serial.SerialException, serial.SerialTimeoutException) as e:
            print(e)
            pass
    try:
        #open serial to controller
        s = serial.Serial('/dev/ttyUSB0', 9600, timeout=2)
        time.sleep(2)

        #handshake with THE answer
        s.write(chr(0x42))
        test = s.readline()
        if test == chr(0x41):
            return s
    except (serial.SerialException, serial.SerialTimeoutException) as e:
        print(e)


def sendAction(ser, motor, angle):
    #Send actions
    ser.write(chr(0xF0))
    ser.write(chr(motor))
    if(angle < 0):
        ser.write(chr(0x02))
    if(angle > 0):
        ser.write(chr(0x01))
    ser.write(str(abs(angle)) + "\n")
    ser.write(chr(0x0F))
    ser.flush()

    #wait for 10 seconds or until controller is done
    for i in range(10):
        test = ser.read()
        print test;
    return False


if __name__ == '__main__':
    #setup server
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

            angle = packet.data['angle']
            steps = myAngle - angle
            steps = round(steps * 1600/360)
            print str(steps) + "\n";
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