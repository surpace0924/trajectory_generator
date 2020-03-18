# -*- coding: utf-8 -*-
import numpy as np

class CatmullRom():
    def __init__(self):
        print("init CatmullRom")

    def calculate(self, t, p0, p1, p2, p3):
        a = -1 * p0 + 3 * p1 - 3 * p2 + p3
        b = 2 * p0 - 5 * p1 + 4 * p2 - p3
        c = -1 * p0 + p2
        d = 2 * p1
        return 0.5 * ((a * t * t * t) + (b * t * t) + (c * t) + d)
