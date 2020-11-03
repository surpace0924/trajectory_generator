# -*- coding: utf-8 -*-
import numpy as np
import matplotlib.pyplot as plt
import CatmullRom
import MinimumJerkModel

class TrajectoryCalculator():
    def __init__(self):
        # 各種制約条件
        self.__dot_gap = 0.001                    # 打点間隔[m]
        self.__dot_method = "equally_spaced"      # 打点方法（"equally_spaced" or "supports_profiles"）
        self.__speed_profile_method = "curvature" # 速度プロファイル生成方法（"curvature", "min_jerk" or "linear"）
        self.__hz = 1                             # 制御周期[Hz]
        self.__max_linear_speed = 1               # 並進最高速度[m/s]
        self.__max_angular_speed = 1              # 並進最高速度[rad/s]
        self.__max_linear_Acceleration = 1        # 回転最高速度[m/s^2]
        self.__max_angular_Acceleration = 1       # 回転最高速度[rad/s^2]
        self.__max_lateral_Acceleration = 1       # 許容横加速度[m/s^2]
        self.__via_point = []                     # 経由点
        self.__via_speed = []                     # 経由点における司令速度

        # 出力
        self.__trajectory = []
        self.__curvature = []
        self.__speed_profile = []
        self.__acceleration_profile = []
        self.__trajectory_length_list = []
        self.__time_stamp = []
        self.__length = 0
        self.__time = 0
        self.__expected_time = 0


    def setDotGap(self, dot_gap):
        self.__dot_gap = dot_gap

    def setDotMethod(self, dot_method):
        self.__dot_method = dot_method

    def setSpeedProfileMethod(self, speed_profile_method):
        self.__speed_profile_method = speed_profile_method

    def setFrequency(self, frequency):
        self.__hz = frequency

    def setMaxLinearSpeed(self, max_linear_speed):
        self.__max_linear_speed = max_linear_speed

    def setMaxAngularSpeed(self, max_angular_speed):
        self.__max_angular_speed = max_angular_speed

    def setMaxLinearAcceleration(self, max_linear_Acceleration):
        self.__max_linear_Acceleration = max_linear_Acceleration

    def setMaxAngularAcceleration(self, max_angular_Acceleration):
        self.__max_angular_Acceleration = max_angular_Acceleration

    def setViaPoint(self, via_point):
        self.__via_point = via_point

    def setViaSpeed(self, via_speed):
        self.__via_speed = via_speed


    def getTrajectory(self):
        return self.__trajectory

    def getCurvature(self):
        return self.__curvature

    def getTrajectoryLengthList(self):
        return self.__trajectory_length_list

    def getTrajectoryLength(self):
        return self.__length

    def getTimeStamp(self):
        return self.__time_stamp

    def getExpectedTime(self):
        return self.__expected_time

    def getSpeedProfileProfile(self):
        return self.__speed_profile

    def getAccelerationProfile(self):
        return self.__acceleration_profile

    # 計算
    def calculate(self):
        cr = CatmullRom.CatmullRom()
        cr.setControlPoint(self.__via_point)

        # 経路の分割数を計算するために大まかな経路長を算出する
        about_length = 0
        for i in range(len(self.__via_point)-1):
            dx = self.__via_point[i + 1][0] - self.__via_point[i][0]
            dy = self.__via_point[i + 1][1] - self.__via_point[i][1]
            dl = np.sqrt(dx ** 2 + dy ** 2)
            about_length += dl

        # 経路打点数の約10倍の個数で経路を分割する
        div_num = int(100 * about_length / self.__dot_gap)

        # 曲線の計算
        curve, curve_length_list, via_point_length = cr.calculate(div_num)
        curve_length = curve_length_list[-1]

        # 打点プロファイルの生成
        # dot_profile = self.__getEquallyDistanceProfile(curve_length, self.__dot_gap)
        dot_profile = self.min_jerk(self.__hz, 0, 0, self.__max_linear_speed, self.__max_linear_Acceleration, curve_length)

        # 打点プロファイルに一番近い点を曲線から計算し，それを経路とする
        self.__trajectory, self.__trajectory_length_list = self.__pickupTrajectory(curve, curve_length_list, dot_profile)

        # 曲率計算
        self.__curvature = self.__calculateCurvature(self.__trajectory)
        for i, curvature in zip(range(len(self.__curvature)), self.__curvature):
            self.__curvature[i] = abs(curvature)

        # self.__time = len(dot_profile) / self.__hz

        # タイムスタンプ，速度プロファイルの生成
        self.__speed_profile = [0]
        self.__time_stamp = [0]
        dt = 1 / self.__hz
        for i in range(len(self.__trajectory) - 1):
            # タイムスタンプ
            self.__time_stamp.append(self.__time_stamp[-1] + dt)

            # 速度プロファイル
            sqt_x = (self.__trajectory[i+1][0] - self.__trajectory[i][0])**2
            sqt_y = (self.__trajectory[i + 1][1] - self.__trajectory[i][1]) ** 2
            dl = np.sqrt(sqt_x + sqt_y)
            vel = dl / dt
            self.__speed_profile.append(vel)

        # 加速度計算
        self.__acceleration_profile = self.__differentiate(self.__speed_profile, self.__time_stamp)


    # リストyをリストxで微分する（dy/dx）
    def __differentiate(self, y, x):
        if len(y) != len(x):
            print("Differentiate Error: List size is different!")
            return []

        # 微分計算（初期条件は要検討）
        y_prime = [(y[1]-y[0])/(x[1]-x[0])]
        for i in range(len(y)-1):
            dy = y[i + 1] - y[i]
            dx = x[i + 1] - x[i]
            y_prime.append(dy / dx)

        return y_prime


    # 等間隔
    def __getEquallyDistanceProfile(self, length, dot_gap):
        return np.arange(0, length, dot_gap)


    # 単純躍度最小
    def __getMinimumJerkProfile(self, length, max_linear_speed, max_linear_Acceleration, hz):
        # time = length / max_linear_speed # 到達時間
        # num = time * hz  # 分割数
        t = np.arange(0, 40, 1/hz)

        mjm = MinimumJerkModel.MinimumJerkModel(max_linear_speed, max_linear_Acceleration)
        mjm.setLength(length)

        profile = []
        for elm in t:
            profile.append(mjm.getPosition(elm))
        plt.scatter(t, profile, 3)
        plt.show()
        return profile


    # プロファイルにしたがって，一番近い座標を選択
    def __pickupTrajectory(self, curve, length_list, profile):
        trajectory = []
        trajectory_length_list = []
        for item in profile:
            length, idx = self.__getNearestValue(length_list, item)
            trajectory.append(curve[idx])
            trajectory_length_list.append(length_list[idx])
        return trajectory, trajectory_length_list


    # リストからある値に最も近い値を返却する関数
    # @param list: データ配列
    # @param num: 対象値
    # @return 対象値に最も近い値
    def __getNearestValue(self, list, num):
        # リスト要素と対象値の差分を計算し最小値のインデックスを取得
        idx = np.abs(np.asarray(list) - num).argmin()
        return list[idx], idx


    # 線形補間
    def __lerp(self, x0, y0, x1, y1, t):
        return y0 + (y1 - y0) * (t - x0) / (x1 - x0)

    def __calculateCurvature(self, curve):
        curvatures = [0.0]
        for i in np.arange(1, len(curve)-1):
            dxn = curve[i][0]     - curve[i - 1][0]
            dxp = curve[i + 1][0] - curve[i][0]
            dyn = curve[i][1]     - curve[i - 1][1]
            dyp = curve[i + 1][1] - curve[i][1]
            dn = np.hypot(dxn, dyn)
            dp = np.hypot(dxp, dyp)
            dx = 1.0 / (dn + dp) * (dp / dn * dxn + dn / dp * dxp)
            ddx = 2.0 / (dn + dp) * (dxp / dp - dxn / dn)
            dy = 1.0 / (dn + dp) * (dp / dn * dyn + dn / dp * dyp)
            ddy = 2.0 / (dn + dp) * (dyp / dp - dyn / dn)
            curvature = (ddy * dx - ddx * dy) / ((dx ** 2 + dy ** 2) ** 1.5)
            curvatures.append(curvature)

        curvatures.append(abs(curvatures[-1]))
        return curvatures

    def min_jerk(self, frequency, startVel, endVel, topVel, topAcc, totalLength):
        # frequency = 50
        # startVel = 0
        # endVel = 0
        # topVel = 1
        # topAcc = 1.5
        # totalLength = 1.5

        accelTime = 16 / 9 * (topVel - startVel) / topAcc
        decelTime = 16 / 9 * (topVel - endVel) / topAcc
        accelLength = (2 * topVel + 3 * startVel) * accelTime / 5
        decelLength = (2 * topVel + 3 * endVel) * decelTime / 5
        flatLength = totalLength - accelLength - decelLength

        punctuation = []

        if flatLength < 0.0: # 加速超過
            virtualTopVel = -1 / 8 * (np.sqrt(45 * topAcc * totalLength + 49 * (np.power(startVel, 2) + np.power(endVel, 2)) + 2 * startVel * endVel) + startVel + endVel)
            accelTime = 16 / 9 * (virtualTopVel - startVel) / topAcc
            decelTime = 16 / 9 * (virtualTopVel - endVel) / topAcc
            accelLength = (2 * virtualTopVel + 3 * startVel) * accelTime / 5
            decelLength = (2 * virtualTopVel + 3 * endVel) * decelTime / 5
            accelCoefficientA = (6 * accelLength - 3 * accelTime * (topVel + startVel)) / np.power(accelTime, 5)
            accelCoefficientB = (-15 * accelLength + accelTime * (7 * topVel + 8 * startVel)) / np.power(accelTime, 4)
            decelCoefficientA = (6 * decelLength - 3 * decelTime * (topVel + endVel)) / np.power(accelTime, 5)
            decelCoefficientB = (-15 * decelLength + decelTime * (7 * topVel + 8 * endVel)) / np.power(accelTime, 4)

            for t in range(int((accelTime + decelTime) * frequency)):
                sectionTime = t / frequency
                if sectionTime < accelTime: #加速
                    punctuation.append(accelCoefficientA * np.power(sectionTime, 5) + accelCoefficientB * np.power(sectionTime, 4))
                else: #減速
                    reverseTime = decelTime - (sectionTime - accelTime)
                    punctuation.append(totalLength - decelCoefficientA * np.power(reverseTime, 5) - decelCoefficientB * np.power(reverseTime, 4) - endVel * reverseTime)
        else:
            accelCoefficientA = (6 * accelLength - 3 * accelTime * (topVel + startVel)) / np.power(accelTime, 5)
            accelCoefficientB = (-15 * accelLength + accelTime * (7 * topVel + 8 * startVel)) / np.power(accelTime, 4)
            decelCoefficientA = (6 * decelLength - 3 * decelTime * (topVel + endVel)) / np.power(accelTime, 5)
            decelCoefficientB = (-15 * decelLength + decelTime * (7 * topVel + 8 * endVel)) / np.power(accelTime, 4)
            flatTime = flatLength / topVel
            for t in range(int((accelTime + decelTime + flatTime) * frequency)):
                sectionTime = t / frequency
                if sectionTime < accelTime: #加速
                    punctuation.append(accelCoefficientA * np.power(sectionTime, 5) + accelCoefficientB * np.power(sectionTime, 4))
                elif (sectionTime >= (accelTime + flatTime)): #減速
                    reverseTime = decelTime - (sectionTime - accelTime - flatTime)
                    punctuation.append(totalLength - decelCoefficientA * np.power(reverseTime, 5) - decelCoefficientB * np.power(reverseTime, 4) - endVel * reverseTime)
                else: # 定速
                    punctuation.append(accelLength + topVel * (sectionTime - accelTime))

        return punctuation
