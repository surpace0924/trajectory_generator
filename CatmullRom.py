# -*- coding: utf-8 -*-
import numpy as np

class CatmullRom():
    def __init__(self):
        self.control_point = []
        self.result_point = []

    def setControlPoint(self, points):
        self.control_point = points

    def getResult(self):
        return self.result_point

    # 計算
    def calculate(self):
        point = self.control_point
        for i in range(len(self.control_point) - 1):
            for t in np.arange(0, 1, 0.1):
                if i == 0:
                    self.result_point.append(self.__calculateFirst(t, point[i], point[i+1], point[i+2]))
                elif i == len(self.control_point) - 2:
                    self.result_point.append (self.__calculateLast(t, point[i-1], point[i], point[i+1]))
                else:
                    self.result_point.append(self.__calculateMiddle(t, point[i-1], point[i], point[i+1], point[i+2]))

        print(len(self.result_point))

    # 各セクションの計算
    def __calculateFirst(self, t, p0, p1, p2):
        b = p0 - 2 * p1 + p2
        c = -3 * p0 + 4 * p1 - p2
        d = 2 * p0
        return 0.5 * ((b * t * t) + (c * t) + d)

    def __calculateMiddle(self, t, p0, p1, p2, p3):
        a = -1 * p0 + 3 * p1 - 3 * p2 + p3
        b = 2 * p0 - 5 * p1 + 4 * p2 - p3
        c = -1 * p0 + p2
        d = 2 * p1
        return 0.5 * ((a * t * t * t) + (b * t * t) + (c * t) + d)

    def __calculateLast(self, t, p0, p1, p2):
        b = p0 - 2 * p1 + p2
        c = -p0 + p2
        d = 2 * p1
        return 0.5 * ((b * t * t) + (c * t) + d)
