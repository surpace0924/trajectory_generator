import matplotlib.pyplot as plt
import numpy as np

class MinimumJerkModel():
    def __init__(self, maxVelocity, maxAcceleration):
        self._length = 1
        self._maxVelocity = maxVelocity
        self._maxAcceleration = maxAcceleration
        self._originalMaxVelocity = None
        self._originalMaxAcceleration = None
        self._matchVelocity = None
        self._mjmLength = None
        self._posScale = None
        self._vScale = None
        self._accScale = None
        self._period = None
        self._constantLengthPeriod = None
        self._originalMaxVelocity = self.getRawVelocity(0.5)
        self._originalMaxAcceleration = self.getRawAcceleration(0.21132486540519)

    def setLength(self, length):
        self._length = length
        self.calcuPeriod()

    def calcuPeriod(self):
        # _xxScale: 出力の値を元の躍度最小モデルの何倍にするか
        self._posScale = 1.0
        self._vScale = self._maxVelocity / self._originalMaxVelocity
        self._accScale = self._maxAcceleration / self._originalMaxAcceleration

        if self._vScale <= self._accScale:
            self._matchVelocity = True
            self._accScale = self._vScale
        else:
            self._matchVelocity = False
            # self._vScale = self._accScale

        self._mjmLength = self._accScale

        if self._length >= self._mjmLength:
            # 加減速にかかる時間
            self._period = 1.0

            # 一定速度で移動する時間
            self._constantLengthPeriod = (self._length - self._mjmLength)/(self._maxVelocity)

            if self._matchVelocity == False:
                self._constantLengthPeriod /= self._vScale
        else:
            periodScale = self._length*self._accScale
            self._mjmLength = self._length
            self._period = np.sqrt(periodScale)/self._accScale/self._vScale
            # self._vScale *= np.sqrt(periodScale)
            # self._posScale = self._length*self._accScale

            self._constantLengthPeriod = 0.0

    def getPeriod(self):
        return (self._period + self._constantLengthPeriod)

    def getPosition(self, t):
        t = self.guard(t, 0.0, self.getPeriod())

        if t >= 0.5*self._period + self._constantLengthPeriod:
            # 減速
            t -= 0.5*self._period + self._constantLengthPeriod
            t /= self._period
            t += 0.5
            return (self._length-self._mjmLength+(self._accScale*self.getRawPosition(t)))*self._posScale
        elif t >= 0.5*self._period and self._constantLengthPeriod > 0.0:
            # 一定速度
            t -= 0.5*self._period
            t /= self._constantLengthPeriod
            return (0.5*self._mjmLength + self.leap(0.0, self._length-self._mjmLength, t))
        else:
            # 加速
            t /= self._period
            return self._accScale*self.getRawPosition(t)*self._posScale

    def getVelocity(self, t):
        t = self.guard(t, 0.0, self.getPeriod())

        if t >= 0.5*self._period + self._constantLengthPeriod:
            # 減速
            t -= 0.5*self._period + self._constantLengthPeriod
            t /= self._period
            t += 0.5
        elif t >= 0.5*self._period and self._constantLengthPeriod > 0.0:
            # 一定速度
            return self._maxVelocity
        else:
            # 加速
            t /= self._period

        # 加減速
        velocity = self.getRawVelocity(t)
        velocity *= self._vScale
        print(str(self.getRawVelocity(t)) + "  " + str(self._vScale) + "  " + str(velocity))

        return velocity

    def getAcceleration(self, t):
        # double result
        # const double n = 0.125
        # double tempT[3]
        # t /= self._period
        # t = self.guard(t, 0.0, 1.0)
        # tempT[0] = t
        # tempT[1] = tempT[0] * t
        # tempT[2] = tempT[1] * t
        # result = 120 * tempT[2] - 180 * tempT[1] + 60 * tempT[0]
        # return result * self._length
        return 0.0

    def getJerk(self, t):
        # double result
        # const double n = 0.125
        # double tempT[3]
        # t /= self._period
        # t = self.guard(t, 0.0, 1.0)
        # tempT[0] = 1
        # tempT[1] = tempT[0] * t
        # tempT[2] = tempT[1] * t
        # result = 360 * tempT[2] - 360 * tempT[1] + 60 * tempT[0]
        # return result * self._length
        return 0.0

    def getRawPosition(self, t):
        tempT = [0, 0, 0]
        t = self.guard(t, 0.0, 1.0)
        tempT[0] = t * t * t
        tempT[1] = tempT[0] * t
        tempT[2] = tempT[1] * t
        result = 6 * tempT[2] - 15 * tempT[1] + 10 * tempT[0]
        return result

    def getRawVelocity(self, t):
        tempT = [0, 0, 0]
        t = self.guard(t, 0.0, 1.0)
        tempT[0] = t * t
        tempT[1] = tempT[0] * t
        tempT[2] = tempT[1] * t
        result = 30 * tempT[2] - 60 * tempT[1] + 30 * tempT[0]
        return result


    def getRawAcceleration(self, t):
        tempT = [0, 0, 0]
        t = self.guard(t, 0.0, 1.0)
        tempT[0] = t
        tempT[1] = tempT[0] * t
        tempT[2] = tempT[1] * t
        result = 120 * tempT[2] - 180 * tempT[1] + 60 * tempT[0]
        return result

    def getRawJerk(self, t):
        tempT = [0, 0, 0]
        t = self.guard(t, 0.0, 1.0)
        tempT[0] = 1
        tempT[1] = tempT[0] * t
        tempT[2] = tempT[1] * t
        result = 360 * tempT[2] - 360 * tempT[1] + 60 * tempT[0]
        return result

    def testCalculation(self, splitNum):
        maxVelocity = 0.0
        maxAcc = 0.0
        state = 0
        period = self.getPeriod()
        errorRate = 1.01
        for i in range(splitNum):
            pos = []*3
            pos[0] = getPosition((period*(i+0))/splitNum)
            pos[1] = getPosition((period*(i+1))/splitNum)
            pos[2] = getPosition((period*(i+2))/splitNum)

            v = abs((pos[1] - pos[0])*splitNum/period)
            acc = abs((pos[2] - 2*pos[1] + pos[0])*sq(splitNum/period))

            # printf("%.3lf %.3lf %.3lf\r\n", pos[0],
            #     self.guard(v/self._maxVelocity, 0.0, 5.0),
            #     self.guard(acc/self._maxAcceleration, 0.0, 5.0))

            maxVelocity = max(maxVelocity, v)
            maxAcc = max(maxAcc, acc)

        if maxVelocity > (self._maxVelocity*errorRate):
            state |= OverMaxVelocity

        if maxAcc > (self._maxAcceleration*errorRate):
            state |= OverMaxAcceleration

        return state

    def guard(self, x, _min, _max):
        if x < _min:
            x = _min
        elif x > _max:
            x = _max
        return x

    def leap(self, a, b, t):
        t = self.guard(t, 0.0, 1.0)
        return (a + (b - a) * t)


# if __name__ == '__main__':
#     mjm = MinimumJerkModel(1, 1)
#     mjm.setLength(0.1)

#     x = np.arange(0, 6, 0.01)
#     vel = []
#     pos = []
#     for elm in x:
#         vel.append(mjm.getVelocity(elm))
#         pos.append(mjm.getPosition(elm))
#     plt.scatter(x,vel, 3)
#     plt.scatter(x,pos, 3)
#     plt.show()
