
import math

import numpy as np
import sys
import os

# add pycubicspline library
# https://github.com/AtsushiSakai/pycubicspline
sys.path.append(os.path.abspath('../pycubicspline/'))
import pycubicspline


def make_angles_continuous(angles):
    angles = np.array(angles)
    for i in range(len(angles)-1):
        d_angle = angles[i+1] - angles[i]
        if d_angle >= np.pi:
            angles[i+1:] -= 2.0 * np.pi
        elif d_angle <= -np.pi:
            angles[i+1:] += 2.0 * np.pi
    return angles


def calc_curvature_range_kutta(x, y):
    dists = np.array([np.hypot(dx, dy) for dx, dy in zip(np.diff(x), np.diff(y))])
    curvatures = [0.0, 0.0]
    for i in np.arange(2, len(x)-1):
        dx = (x[i+1] - x[i])/dists[i]
        dy = (y[i+1] - y[i])/dists[i]
        ddx = (x[i-2] - x[i-1] - x[i] + x[i+1])/(2*dists[i]**2)
        ddy = (y[i-2] - y[i-1] - y[i] + y[i+1])/(2*dists[i]**2)
        curvature = (ddy * dx - ddx * dy) / ((dx ** 2 + dy ** 2) ** 1.5)
        curvatures.append(abs(curvature))
    curvatures.append(0.0)
    return curvatures


def calc_curvature_2_derivative(x, y):

    curvatures = [0.0]
    for i in np.arange(1, len(x)-1):
        dxn = x[i] - x[i - 1]
        dxp = x[i + 1] - x[i]
        dyn = y[i] - y[i - 1]
        dyp = y[i + 1] - y[i]
        dn = np.hypot(dxn, dyn)
        dp = np.hypot(dxp, dyp)
        dx = 1.0 / (dn + dp) * (dp / dn * dxn + dn / dp * dxp)
        ddx = 2.0 / (dn + dp) * (dxp / dp - dxn / dn)
        dy = 1.0 / (dn + dp) * (dp / dn * dyn + dn / dp * dyp)
        ddy = 2.0 / (dn + dp) * (dyp / dp - dyn / dn)
        curvature = (ddy * dx - ddx * dy) / ((dx ** 2 + dy ** 2) ** 1.5)
        curvatures.append(curvature)

    curvatures.append(curvatures[-1])
    return curvatures


def calc_curvature_with_yaw_diff(x, y, yaw):
    dists = np.array([np.hypot(dx, dy) for dx, dy in zip(np.diff(x), np.diff(y))])
    d_yaw = np.diff(make_angles_continuous(yaw))
    curvatures = d_yaw / dists
    curvatures = np.concatenate([curvatures, [0.0]])

    return curvatures


def calc_curvature_circle_fitting(x, y, npo=1):
    """
    Calc curvature
    x,y: x-y position list
    npo: the number of points using Calculation curvature
    ex) npo=1: using 3 point
        npo=2: using 5 point
        npo=3: using 7 point
    """

    cv = []
    n_data = len(x)

    for i in range(n_data):
        lind = i - npo
        hind = i + npo + 1

        if lind < 0:
            lind = 0
        if hind >= n_data:
            hind = n_data

        xs = x[lind:hind]
        ys = y[lind:hind]
        (cxe, cye, re) = CircleFitting(xs, ys)

        if len(xs) >= 3:
            # sign evaluation
            c_index = int((len(xs) - 1) / 2.0)
            sign = (xs[0] - xs[c_index]) * (ys[-1] - ys[c_index]) - (
                    ys[0] - ys[c_index]) * (xs[-1] - xs[c_index])

            # check straight line
            a = np.array([xs[0] - xs[c_index], ys[0] - ys[c_index]])
            b = np.array([xs[-1] - xs[c_index], ys[-1] - ys[c_index]])
            theta = math.degrees(math.acos(
                np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))))

            if theta == 180.0:
                cv.append(0.0)  # straight line
            elif sign > 0:
                cv.append(1.0 / -re)
            else:
                cv.append(1.0 / re)
        else:
            cv.append(0.0)

    return cv


def CircleFitting(x, y):
    """Circle Fitting with least squared
        input: point x-y positions
        output  cxe x center position
                cye y center position
                re  radius of circle
    """

    sumx = sum(x)
    sumy = sum(y)
    sumx2 = sum([ix ** 2 for ix in x])
    sumy2 = sum([iy ** 2 for iy in y])
    sumxy = sum([ix * iy for (ix, iy) in zip(x, y)])

    F = np.array([[sumx2, sumxy, sumx],
                  [sumxy, sumy2, sumy],
                  [sumx, sumy, len(x)]])

    G = np.array([[-sum([ix ** 3 + ix * iy ** 2 for (ix, iy) in zip(x, y)])],
                  [-sum([ix ** 2 * iy + iy ** 3 for (ix, iy) in zip(x, y)])],
                  [-sum([ix ** 2 + iy ** 2 for (ix, iy) in zip(x, y)])]])

    try:
        T = np.linalg.inv(F).dot(G)
    except np.linalg.LinAlgError:
        return 0, 0, float("inf")

    cxe = float(T[0] / -2)
    cye = float(T[1] / -2)

    try:
        re = math.sqrt(cxe ** 2 + cye ** 2 - T[2])
    except np.linalg.LinAlgError:
        return cxe, cye, float("inf")
    return cxe, cye, re


"""
Cubic Spline library on python

author Atsushi Sakai

"""
import bisect
import math

import numpy as np


class Spline:
    """
    Cubic Spline class
    """

    def __init__(self, x, y):
        self.b, self.c, self.d, self.w = [], [], [], []

        self.x = x
        self.y = y

        self.nx = len(x)  # dimension of x
        h = np.diff(x)

        # calc coefficient c
        self.a = [iy for iy in y]

        # calc coefficient c
        A = self.__calc_A(h)
        B = self.__calc_B(h)
        self.c = np.linalg.solve(A, B)

        # calc spline coefficient b and d
        for i in range(self.nx - 1):
            self.d.append((self.c[i + 1] - self.c[i]) / (3.0 * h[i]))
            tb = (self.a[i + 1] - self.a[i]) / h[i] - h[i] * \
                 (self.c[i + 1] + 2.0 * self.c[i]) / 3.0
            self.b.append(tb)

    def calc(self, t):
        """
        Calc position

        if t is outside of the input x, return None

        """

        if t < self.x[0]:
            return None
        elif t > self.x[-1]:
            return None

        i = self.__search_index(t)
        dx = t - self.x[i]
        result = self.a[i] + self.b[i] * dx + self.c[i] * dx ** 2.0 + self.d[i] * dx ** 3.0

        return result

    def calc_d(self, t):
        """
        Calc first derivative

        if t is outside of the input x, return None
        """

        if t < self.x[0]:
            return None
        elif t > self.x[-1]:
            return None

        i = self.__search_index(t)
        dx = t - self.x[i]
        result = self.b[i] + 2.0 * self.c[i] * dx + 3.0 * self.d[i] * dx ** 2.0
        return result

    def calc_dd(self, t):
        """
        Calc second derivative
        """

        if t < self.x[0]:
            return None
        elif t > self.x[-1]:
            return None

        i = self.__search_index(t)
        dx = t - self.x[i]
        result = 2.0 * self.c[i] + 6.0 * self.d[i] * dx
        return result

    def __search_index(self, x):
        return bisect.bisect(self.x, x) - 1

    def __calc_A(self, h):
        A = np.zeros((self.nx, self.nx))
        A[0, 0] = 1.0
        for i in range(self.nx - 1):
            if i != (self.nx - 2):
                A[i + 1, i + 1] = 2.0 * (h[i] + h[i + 1])
            A[i + 1, i] = h[i]
            A[i, i + 1] = h[i]

        A[0, 1] = 0.0
        A[self.nx - 1, self.nx - 2] = 0.0
        A[self.nx - 1, self.nx - 1] = 1.0
        #  print(A)
        return A

    def __calc_B(self, h):
        """
        calc matrix B for spline coefficient c
        """
        B = np.zeros(self.nx)
        for i in range(self.nx - 2):
            B[i + 1] = 3.0 * (self.a[i + 2] - self.a[i + 1]) / \
                       h[i + 1] - 3.0 * (self.a[i + 1] - self.a[i]) / h[i]
        #  print(B)
        return B

    def calc_curvature(self, t):
        j = int(math.floor(t))
        if j < 0:
            j = 0
        elif j >= len(self.a):
            j = len(self.a) - 1

        dt = t - j
        df = self.b[j] + 2.0 * self.c[j] * dt + 3.0 * self.d[j] * dt * dt
        ddf = 2.0 * self.c[j] + 6.0 * self.d[j] * dt
        k = ddf / ((1 + df ** 2) ** 1.5)
        return k


class Spline2D:
    """
    2D Cubic Spline class
    """

    def __init__(self, x, y):
        self.s = self.__calc_s(x, y)
        self.sx = Spline(self.s, x)
        self.sy = Spline(self.s, y)

    def __calc_s(self, x, y):
        dx = np.diff(x)
        dy = np.diff(y)
        self.ds = [math.sqrt(idx ** 2 + idy ** 2)
                   for (idx, idy) in zip(dx, dy)]
        s = [0.0]
        s.extend(np.cumsum(self.ds))
        return s

    def calc_position(self, s):
        """
        calc position
        """
        x = self.sx.calc(s)
        y = self.sy.calc(s)

        return x, y

    def calc_curvature(self, s):
        """
        calc curvature
        """
        dx = self.sx.calc_d(s)
        ddx = self.sx.calc_dd(s)
        dy = self.sy.calc_d(s)
        ddy = self.sy.calc_dd(s)
        k = (ddy * dx - ddx * dy) / (dx ** 2 + dy ** 2) ** 1.5
        return k

    def calc_yaw(self, s):
        """
        calc yaw
        """
        dx = self.sx.calc_d(s)
        dy = self.sy.calc_d(s)
        yaw = math.atan2(dy, dx)
        return yaw


def calc_2d_spline_interpolation(x, y, num=100):
    """
    Calc 2d spline course with interpolation

    :param x: interpolated x positions
    :param y: interpolated y positions
    :param num: number of path points
    :return:
        - x     : x positions
        - y     : y positions
        - yaw   : yaw angle list
        - k     : curvature list
        - s     : Path length from start point
    """
    sp = Spline2D(x, y)
    s = np.linspace(0, sp.s[-1], num+1)[:-1]

    r_x, r_y, r_yaw, r_k = [], [], [], []
    for i_s in s:
        ix, iy = sp.calc_position(i_s)
        r_x.append(ix)
        r_y.append(iy)
        r_yaw.append(sp.calc_yaw(i_s))
        r_k.append(sp.calc_curvature(i_s))

    travel = np.cumsum([np.hypot(dx, dy) for dx, dy in zip(np.diff(r_x), np.diff(r_y))]).tolist()
    travel = np.concatenate([[0.0], travel])

    return r_x, r_y, r_yaw, r_k, travel


def test_spline2d():
    print("Spline 2D test")
    import matplotlib.pyplot as plt
    input_x = [-2.5, 0.0, 2.5, 5.0, 7.5, 3.0, -1.0]
    input_y = [0.7, -6, 5, 6.5, 0.0, 5.0, -2.0]

    x, y, yaw, k, travel = calc_2d_spline_interpolation(input_x, input_y, num=200)

    plt.subplots(1)
    plt.plot(input_x, input_y, "xb", label="input")
    plt.plot(x, y, "-r", label="spline")
    plt.grid(True)
    plt.axis("equal")
    plt.xlabel("x[m]")
    plt.ylabel("y[m]")
    plt.legend()

    plt.subplots(1)
    plt.plot(travel, [math.degrees(i_yaw) for i_yaw in yaw], "-r", label="yaw")
    plt.grid(True)
    plt.legend()
    plt.xlabel("line length[m]")
    plt.ylabel("yaw angle[deg]")

    plt.subplots(1)
    plt.plot(travel, k, "-r", label="curvature")
    plt.grid(True)
    plt.legend()
    plt.xlabel("line length[m]")
    plt.ylabel("curvature [1/m]")

    plt.show()


def test_spline():
    print("Spline test")
    import matplotlib.pyplot as plt
    x = [-0.5, 0.0, 0.5, 1.0, 1.5]
    y = [3.2, 2.7, 6, 5, 6.5]

    spline = Spline(x, y)
    rx = np.arange(-2.0, 4, 0.01)
    ry = [spline.calc(i) for i in rx]

    plt.plot(x, y, "xb")
    plt.plot(rx, ry, "-r")
    plt.grid(True)
    plt.axis("equal")
    plt.show()



def main():
    print("Spline 2D test")
    import matplotlib.pyplot as plt
    cx = [-2.5, 0.0, 2.5, 5.0, 7.5, 3.0, -1.0]
    cy = [0.7, -6, 5, 6.5, 0.0, 5.0, -2.0]
    x, y, yaw, k, travel = calc_2d_spline_interpolation(cx, cy, num=200)

    fig, axes = plt.subplots(2)
    axes[0].plot(cx, cy, "xb", label="input")
    axes[0].plot(x, y, "-r", label="spline")
    axes[0].grid(True)
    axes[0].axis("equal")
    axes[0].set_xlabel("x[m]")
    axes[0].set_ylabel("y[m]")
    axes[0].legend()

    # circle fitting
    # travel = [np.hypot(dx, dy) for dx, dy in zip(np.diff(x), np.diff(y))]
    curvature_circle_fitting = calc_curvature_circle_fitting(x, y)
    curvature_yaw_diff = calc_curvature_with_yaw_diff(x, y, yaw)
    # Note: range_kutta returns absolute curvature
    curvature_range_kutta = calc_curvature_range_kutta(x, y)
    curvature_2_derivative = calc_curvature_2_derivative(x, y)

    print(len(travel))
    print(len(curvature_2_derivative))
    axes[1].plot(travel, k, "-r", label="analytic curvature")
    axes[1].plot(travel, curvature_circle_fitting, "-b", label="circle_fitting")
    axes[1].plot(travel, curvature_yaw_diff, "-g", label="yaw_angle_diff")
    axes[1].plot(travel, curvature_range_kutta, "-c", label="range_kutta")
    axes[1].plot(travel, curvature_2_derivative, "-k", label="2_derivative")
    axes[1].grid(True)
    axes[1].legend()
    axes[1].set_xlabel("line length[m]")
    axes[1].set_ylabel("curvature [1/m]")

    plt.show()


if __name__ == '__main__':
    main()
