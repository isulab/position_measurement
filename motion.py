import math
from enum import Enum

class MotionType(Enum):
    WHITENOISE = 0
    RANDOMNOISE = 1
    SIN = 2
    SQUARE = 3
    SENSORDATA = 4

class MotionOfTable:
    def __init__(self, motion_type, frequent, amplitude, raising):
        self.front_axis = MotionOfAxis(motion_type, frequent, amplitude, raising)
        self.right_axis = MotionOfAxis(motion_type, frequent, amplitude, raising)
        self.left_axis = MotionOfAxis(motion_type, frequent, amplitude, raising)

class MotionOfAxis:
    def __init__(self, motion_type, frequent, amplitude, raising):
        """
        :param frequent: 周波数[Hz] 
        :param amplitude: 振幅[edge]
        :param raising: 初期位置（下限でのロータリーエンコーダーの値を0とした時の，動作の最下値）[edge]
        """

        self.frequent = frequent
        self.amplitude = amplitude
        self.raising = raising
        self.MAX_TARGET_VALUE = 4000
        if (motion_type == MotionType.SIN):
            self.use_motion_func = self.sin_wave
            print("sin ok")
        elif(motion_type == MotionType.SQUARE):
            self.use_motion_func = self.square_wave

    def sin_wave(self, time):
        target_value = self.raising - math.cos(time * self.frequent / 2 * math.pi) * self.amplitude + self.amplitude
        if 0 > target_value :
            target_value = 0
        elif target_value > self.MAX_TARGET_VALUE :
            target_value = math.floor(target_value / self.MAX_TARGET_VALUE) * self.MAX_TARGET_VALUE
        return int(target_value)

    def square_wave(self, time):
        target_value = self.raising +  self.amplitude if time % (1 / self.frequent) < (1 / self.frequent / 2) else self.raising
        if 0 > target_value :
            target_value = 0
        elif target_value > self.MAX_TARGET_VALUE :
            target_value = math.floor(target_value / self.MAX_TARGET_VALUE) * self.MAX_TARGET_VALUE
        return int(target_value)

    def get_motion(self, time):
        return self.use_motion_func(time)

'''
テスト用仮のメイン
'''
if __name__ == '__main__':
    motion_of_axis = MotionOfAxis(MotionType.SIN, 1, 2000, 0)
    for i in range(1000):
        print(motion_of_axis.get_motion(i/1000))
