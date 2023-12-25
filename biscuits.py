from csv import DictReader
from copy import deepcopy
import numpy as np

rng = np.random.default_rng()

with open('defects.csv', 'r') as f:
    defects_dict = DictReader(f)


    def x_to_float(elem):
        elem['x'] = float(elem['x'])
        return elem


    defects_dict = map(x_to_float, defects_dict)
    defects_dict = sorted(defects_dict, key=lambda d: d['x'])


class Biscuit:
    def __init__(self, size, value, tolerance):
        self.size = size
        self.value = value
        self.tolerance = tolerance


biscuit_types = [
    Biscuit(4, 6, {'a': 4, 'b': 2, 'c': 3}),
    Biscuit(8, 12, {'a': 5, 'b': 4, 'c': 4}),
    Biscuit(2, 1, {'a': 1, 'b': 2, 'c': 1}),
    Biscuit(5, 8, {'a': 2, 'b': 3, 'c': 2})
]


class Roll:
    def __init__(self, roll_size=500):
        self.roll_size = roll_size
        self._biscuits = []

    def append_biscuits(self, biscuits):
        if isinstance(biscuits, list):
            self._biscuits += biscuits
        elif isinstance(biscuits, Biscuit):
            self._biscuits.append(biscuits)
        else:
            raise ValueError('Biscuits should be a list or a Biscuit')

    def invert_biscuits(self, index1, index2):
        self._biscuits[index1], self._biscuits[index2] = self._biscuits[index2], self._biscuits[index1]

    def mix_biscuits(self, copy=False):
        if copy:
            new_biscuits = self._biscuits.copy()
            rng.shuffle(new_biscuits)
            return new_biscuits
        else:
            return rng.shuffle(self._biscuits)

    def total_price(self):
        sum([biscuit.value for biscuit in self._biscuits])

    def number_of_biscuits(self):
        return len(self._biscuits)

    def fill_roll_random(self, adjust_invalid_biscuits=False):
        integers = rng.integers(0, 3, 500)
        length_of_roll = 0
        for i in integers:
            new_biscuit = deepcopy(biscuit_types[i])
            self._biscuits.append(new_biscuit)
            length_of_roll += new_biscuit.size
            if length_of_roll >= self.roll_size:
                return

    def check_roll_biscuits(self):
        pass
