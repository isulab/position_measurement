import serial
from serial.threaded import LineReader
from serial.threaded import ReaderThread
import sys
import traceback
import time
import math

#/dev/tty.wchusbserial1410
SERIAL_PORT_NAME = 'COM5' if os.name == 'nt' else '/dev/tty.wchusbserial1420'
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
    def __init__(self, frequent, amplitude, raising):
        """
        :param frequent: 周波数[Hz] 
        :param amplitude: 振幅[edge]
        :param raising: 初期位置（下限でのロータリーエンコーダーの値を0とした時の，動作の最下値）[edge]
        """

        self.frequent = frequent
        self.max_inclination = max_inclination
        self.amplitude = amplitude
        self.raising = raising
        self.MAX_TARGET_VALUE = 4000

    def make_sin(self,time):
        target_value = self.raising + math.sin(time * self.frequent / 2000 * math.pi) * self.amplitude
        if 0 > target_value or target_value > self.MAX_TARGET_VALUE :
            target_value = math.floor(target_value / self.MAX_TARGET_VALUE) * self.MAX_TARGET_VALUE
        return hex(target_value)

    def make_square(self, time):
        target_value = self.raising +  self.amplitude if time / 1000 / frequent < frequent / 2 else self.amplitude
        if 0 > target_value or target_value > self.MAX_TARGET_VALUE :
            target_value = math.floor(value / self.MAX_TARGET_VALUE) * self.MAX_TARGET_VALUE
        return hex(target_value)

    def get_out_sin_str(self, time1, time2, time3):
        return  self.make_square(time1) + self.make_square(time2) + self.make_square(time1)

    def get_out_square_str(self, time1, time2, time3):
        return self.make_square(time1) + self.make_square(time2) + self.make_square(time1)


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
