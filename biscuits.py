from enum import Enum
import numpy as np

rng = np.random.default_rng()


class Biscuit:
    def __init__(self, length, value, tolerance):
        self.size = length
        self.tolerance = tolerance


biscuit_types = [
    Biscuit(4, 6, {'a': 4, 'b': 2, 'c': 3}),
    Biscuit(8, 12, {'a': 5, 'b': 4, 'c': 4}),
    Biscuit(2, 1, {'a': 1, 'b': 2, 'c': 1}),
    Biscuit(5, 8, {'a': 2, 'b': 3, 'c': 2})
]


class Roll:
    def __init__(self):
        self._biscuits = []

    def append_biscuits(self, biscuit):
        self._biscuits.append(biscuit)

    def invert_biscuits(self, index1, index2):
        self._biscuits[index1], self._biscuits[index2] = self._biscuits[index2], self._biscuits[index1]

    def mix_biscuits(self, copy=False):
        if copy:
            new_biscuits = self._biscuits.copy()
            rng.shuffle(new_biscuits)
            return new_biscuits
        else:
            return rng.shuffle(self._biscuits)

    def