# -*- coding: utf-8 -*-
import numpy as np

class CatmullRom():
    def __init__(self):
        self.control_point = []
        self.result_point = []
        self.length = 0

    def setControlPoint(self, points):
        self.control_point = points

    def getResult(self):
        return self.result_point, self.length

    # 計算
    def calculate(self):
        self.result_point, self.length = self.__calculateTrajectory(self.control_point, 10000)

    # CatmullRomの計算
    def __calculateTrajectory(self, point, div):
        trajectory = [] # 経路点の座標
        length = 0      # 経路長[m]
        point_num = 0   # 経路数

        # 区間のループ
        for i in range(len(point) - 1):
            # 媒介変数のループ
            for t in np.arange(0, 1, 1/div):
                # 始点，終点，中間点で式が違うため，関数の振り分け
                if i == 0:
                    trajectory.append(self.__calculateFirst(t, point[i], point[i+1], point[i+2]))
                elif i == len(point) - 2:
                    trajectory.append(self.__calculateLast(t, point[i-1], point[i], point[i+1]))
                else:
                    trajectory.append(self.__calculateMiddle(t, point[i-1], point[i], point[i+1], point[i+2]))

                # 経路長は経路点間のユークリッド距離の積算で計算
                length += np.linalg.norm(trajectory[point_num] - trajectory[point_num - 1])
                point_num += 1

        return trajectory, length

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
