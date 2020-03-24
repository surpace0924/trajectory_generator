# -*- coding: utf-8 -*-
import numpy as np

class CatmullRom():
    def __init__(self):
        self.control_point = []
        self.result_point = []
        self.length = 0
        self.time = 0

        self.hz = 1             # 制御周期[Hz]
        self.max_speed = 0.22   # 最高速度[m/s]
        self.max_acc = 0.22     # 最高加速度[m/s^2]

    def setControlPoint(self, points):
        self.control_point = points

    def getResult(self):
        return self.result_point, self.length, self.time

    # 計算
    def calculate(self):
        trajectory, self.length, length_list = self.__calculateTrajectory(self.control_point, 10000)
        profile = self.__getEquallyDistanceProfile(self.length, self.max_speed, self.hz)
        self.result_point = self.__pickupTrajectory(trajectory, length_list, profile)
        self.time = len(profile) / self.hz

    # CatmullRomの計算
    def __calculateTrajectory(self, point, div):
        trajectory = [] # 経路点の座標
        length = 0      # 経路長[m]
        length_list = []
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
                length_list.append(length)
                point_num += 1

        return trajectory, length, length_list

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

    # 等間隔
    def __getEquallyDistanceProfile(self, length, max_speed, hz):
        time = length / max_speed # 到達時間
        num = time * hz         # 分割数
        return np.arange(0, length, length/num)

    # プロファイルにしたがって，一番近い座標を選択
    def __pickupTrajectory(self, trajectory, length_list, profile):
        result = []
        for item in profile:
            length, idx = self.__getNearestValue(length_list, item)
            result.append(trajectory[idx])
        return result

    # リストからある値に最も近い値を返却する関数
    # @param list: データ配列
    # @param num: 対象値
    # @return 対象値に最も近い値
    def __getNearestValue(self, list, num):
        # リスト要素と対象値の差分を計算し最小値のインデックスを取得
        idx = np.abs(np.asarray(list) - num).argmin()
        return list[idx], idx
