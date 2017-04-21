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


usleep = lambda x: sleep(x/1000000.0)

SERIAL_PORT_NAME = 'COM3' if os.name == 'nt' else '/dev/tty.wchusbserial1420'
SERIAL_BAUD_RATE = 38400

'''
CSV書き込みを扱うクラス
'''
class CSVWriter:

    def __init__(self, filename):
        self.filename = filename
        self.file = open(filename, 'a')
        self.writer = csv.writer(self.file, lineterminator='\n')  # 改行コード（\n）を指定しておく

    def writeRow(self, time, axis1, axis2, axis3):
        self.writer.writerow([time, axis1, axis2, axis3])

    def writeRowText(self, time, text):
        self.writer.writerow([time, text])

    def __del__(self):
        self.file.close()

'''
時間を管理するクラス
'''
class TimeMeasure:

    def __init__(self):
        self.starttime = time.time()

    def getTimeString(self):
        return str(time.time() - self.starttime)

    def getTimeFloat(self):
        return time.time() - self.starttime

'''
制御値を計算するクラス
'''
class Control:
    def __init__(self, frequent, amplitude, raising):
        """
        :param frequent: 周波数[Hz] 
        :param amplitude: 振幅[edge]
        :param raising: 初期位置（下限でのロータリーエンコーダーの値を0とした時の，動作の最下値）[edge]
        """

        self.frequent = frequent
        self.amplitude = amplitude
        self.raising = raising
        self.MAX_TARGET_VALUE = 4000

    def make_sin(self,time):
        target_value = self.raising - math.cos(time * self.frequent / 2 * math.pi) * self.amplitude + self.amplitude
        if 0 > target_value or target_value > self.MAX_TARGET_VALUE :
            target_value = math.floor(target_value / self.MAX_TARGET_VALUE) * self.MAX_TARGET_VALUE
        return int(target_value)

    def make_square(self, time):
        target_value = self.raising +  self.amplitude if time % (1 / self.frequent) < (1 / self.frequent / 2) else self.raising
        if 0 > target_value or target_value > self.MAX_TARGET_VALUE :
            target_value = math.floor(target_value / self.MAX_TARGET_VALUE) * self.MAX_TARGET_VALUE
        return int(target_value)

    def get_out_sin_str(self, time1, time2, time3):
        return '{0:04x}'.format(self.make_sin(time1)) + '{0:04x}'.format(self.make_sin(time2)) + '{0:04x}'.format(self.make_sin(time3))

    def get_out_square_str(self, time1, time2, time3):
        return '{0:04x}'.format(self.make_square(time1)) + '{0:04x}'.format(self.make_square(time2)) + '{0:04x}'.format(self.make_square(time3))

'''
マイコンとのシリアル通信のクラス
'''
class SASerial:

    def __init__(self,port,baudrate):
        self.ser = serial.serial_for_url(port, baudrate=baudrate, timeout=5)
        self.writer = CSVWriter("SendControlData.csv")

    class PrintLines(LineReader):
        TERMINATOR = b'\n'

        def connection_made(self, transport):
            super(SASerial.PrintLines, self).connection_made(transport)
            sys.stdout.write('port opened\n')
            self.transport.serial.reset_input_buffer()
            self.writer = CSVWriter("RecievePosisionData.csv")

            # def data_received(self, data):
            # print('data received', repr(data))

        def handle_line(self, data):
            sys.stdout.write('line received: {}\n'.format(repr(data)))
            recieve = repr(data)
            if len(recieve) >= 14:
                axis1 = int(recieve[1:5], 16)
                axis2 = int(recieve[5:9], 16)
                axis3 = int(recieve[9:13], 16)
                global timer
                self.writer.writeRow(timer.getTimeString(), axis1, axis2, axis3)

        def connection_lost(self, exc):
            if exc:
                traceback.print_exc(exc)
            sys.stdout.write('port closed\n')

    def main(self):
        with ReaderThread(self.ser, self.PrintLines) as protocol:
            control = Control(2, 2000, 0)
            sleep(1)

            for roop in range(0,100):
                global timer
                now = timer.getTimeFloat()
                axis1 = control.make_sin(now)
                axis2 = control.make_sin(now)
                axis3 = control.make_sin(now)
#                outvalue = control.get_out_sin_str(now,now,now)
                outvalue = control.get_out_square_str(now, now, now)
                protocol.write_line(outvalue)
                self.writer.writeRow(timer.getTimeString(), axis1, axis2, axis3)
                usleep(100)

'''
メイン
'''
if __name__ == '__main__':
    timer = TimeMeasure()
    ser = SASerial(SERIAL_PORT_NAME,SERIAL_BAUD_RATE)
    ser.main()