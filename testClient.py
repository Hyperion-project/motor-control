__author__ = 'Maarten'
from multibus import BusCore, BusClient

if __name__ == '__main__':
    c = BusClient.BusClient(15001)
    c.send(BusCore.Packet(BusCore.PacketType.SETMOTOR, {'motor': 'B','angle': 360,'returnport':15002}))