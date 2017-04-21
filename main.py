import serial
from serial.threaded import LineReader
from serial.threaded import ReaderThread
import sys
import traceback
from time import sleep
import time
import math
import csv
import os

#/dev/tty.wchusbserial1410
SERIAL_PORT_NAME = 'COM3' if os.name == 'nt' else '/dev/tty.wchusbserial1420'
SERIAL_BAUD_RATE = 38400

FREQUENT = 200

class Control:

    def makeSin(self,time):
        return math.sin(2*math.pi*time*FREQUENT)

    def getOutStr(self,time):
        s = self.makeSin(time)
        return str(s)+str(s)+str(s)

class CSVWriter:

    def __init__(self, filename):
        self.filename = filename
        self.file = open(filename, 'a')
        self.writer = csv.writer(self.file, lineterminator='\n')  # 改行コード（\n）を指定しておく

    def writeRow(self, time, axis1, axis2, axis3):
        self.writer.writerow([time, axis1, axis2, axis3])

    def __del__(self):
        self.file.close()


class TimeMeasure:

    def __init__(self):
        self.starttime = time.time()

    def getTime(self):
        return str(time.time() - self.starttime)


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

class SASerial:

    def __init__(self,port,baudrate):
        self.ser = serial.serial_for_url(port, baudrate=baudrate, timeout=5)

    class PrintLines(LineReader):
        TERMINATOR = b'\n'

        def connection_made(self, transport):
            super(SASerial.PrintLines, self).connection_made(transport)
            sys.stdout.write('port opened\n')
            self.transport.serial.reset_input_buffer()
            self.writer = CSVWriter("data.csv")

            # def data_received(self, data):
            # print('data received', repr(data))

        def handle_line(self, data):
            # print('handle_line')
            sys.stdout.write('line received: {}\n'.format(repr(data)))
            recieve = repr(data)
            if len(recieve) >= 14:
                axis1 = int(recieve[1:5], 16)
                axis2 = int(recieve[5:9], 16)
                axis3 = int(recieve[9:13], 16)
                global timer
                self.writer.writeRow(timer.getTime(), axis1, axis2, axis3)


        def connection_lost(self, exc):
            if exc:
                traceback.print_exc(exc)
            sys.stdout.write('port closed\n')

    def main(self):
        with ReaderThread(self.ser, self.PrintLines) as protocol:
            control = Control()
            sleep(1)

            for time in range(0,100):
                protocol.write_line("AAAABBBBCCCC")

timer = TimeMeasure()
ser = SASerial(SERIAL_PORT_NAME,SERIAL_BAUD_RATE)
ser.main()
