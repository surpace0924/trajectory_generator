import math
import cmath
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import matplotlib.dates as mdates
from statistics import mean, median, variance, stdev

# リストyをリストxで微分する（dy/dx）
def differentiate(y, x):
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


# 配色リスト[黒，青，赤，緑，黄，紫，水色]
color_list = ["#000000", "#296fbc", "#cb360d",
              "#3d9435", "#e1aa13", "#a54675", "#138bae"]

# x軸の目盛線が内向き('in')か外向き('out')か双方向か('inout')
plt.rcParams['xtick.direction'] = 'in'
# y軸の目盛線が内向き('in')か外向き('out')か双方向か('inout')
plt.rcParams['ytick.direction'] = 'in'
plt.rcParams['xtick.major.width'] = 1.0  # x軸主目盛り線の線幅
plt.rcParams['ytick.major.width'] = 1.0  # y軸主目盛り線の線幅
plt.rcParams['font.size'] = 9           # フォントの大きさ
plt.rcParams['axes.linewidth'] = 0.7    # 軸の線幅edge linewidth。囲みの太さ

fig = plt.figure(figsize=(12.5/2.54, 11/2.54))
ax = fig.add_subplot(1, 1, 1)

x = np.linspace(0, 10, 5000)

def min_jerk(frequency, startVel, endVel, topVel, topAcc, totalLength):
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

        for t in range((accelTime + decelTime) * frequency):
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

# differentiate
frequency = 50
punctuation = min_jerk(frequency, 0, 0, 0.7, 1, 1.5)
t = []
for i in range(len(punctuation)):
    t.append(i/frequency)
ax.plot(t, punctuation, color=color_list[1], linewidth=1, label='pose')
ax.plot(t, differentiate(punctuation, t), color=color_list[2], linewidth=1, label='vel')
ax.plot(t, differentiate(differentiate(punctuation, t), t), color=color_list[3], linewidth=1, label='acc')

plt.xlabel("$t$ [s]", fontsize=10)
plt.ylabel("", fontsize=10)

# 目盛のスタイル
plt.setp(ax.get_xticklabels(), fontsize=10.5)
plt.setp(ax.get_yticklabels(), fontsize=10.5)
ax.grid(ls="--")

# グラフタイトル
# plt.title('')

# グラフ範囲
# plt.xlim()
# plt.ylim(0.0, 0.7)

# 余白設定
plt.subplots_adjust(left=0.11, right=0.98, bottom=0.11, top=0.95)


# グラフの凡例
ax.legend(fancybox=False, framealpha=1, edgecolor="#000000", loc='upper right', fontsize=10)

# 表示
plt.show()
