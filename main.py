import serial
from serial.threaded import LineReader
from serial.threaded import ReaderThread
import sys
import traceback
import time
import math

#/dev/tty.wchusbserial1410

SERIAL_PORT_NAME = '/dev/tty.wchusbserial1420'
SERIAL_BAUD_RATE = 38400

FREQUENT = 200

class PrintLines(LineReader):
    TERMINATOR = b'\n'

    def connection_made(self, transport):
        super(PrintLines, self).connection_made(transport)
        sys.stdout.write('port opened\n')
        self.transport.serial.reset_input_buffer()

    #def data_received(self, data):
        #print('data received', repr(data))

    def handle_line(self, data):
        print('handle_line')
        sys.stdout.write('line received: {}\n'.format(repr(data)))

    def connection_lost(self, exc):
        if exc:
            traceback.print_exc(exc)
        sys.stdout.write('port closed\n')


class Control():

    def makeSin(self,time):
        return math.sin(2*math.pi*time*FREQUENT)

    def getOutStr(self,time):
        s = self.makeSin(time)
        return str(s)+str(s)+str(s)

class SASerial():

    def __init__(self,port,baudrate):
        self.ser = serial.serial_for_url(port, baudrate=baudrate, timeout=5)

    def main(self):
        with ReaderThread(self.ser, PrintLines) as protocol:
            control = Control()
            for time in range(0,100):
                outline = control.getOutStr(time)
                protocol.write_line(outline)



ser = SASerial(SERIAL_PORT_NAME,SERIAL_BAUD_RATE)
ser.main()
