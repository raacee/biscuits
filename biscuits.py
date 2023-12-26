from csv import DictReader
from copy import deepcopy
import numpy as np

rng = np.random.default_rng()

with open('defects.csv', 'r') as f:
    defects_list = DictReader(f)

    def x_to_float(elem):
        elem['x'] = float(elem['x'])
        return elem

    defects_list = map(x_to_float, defects_list)
    defects_list = list(sorted(defects_list, key=lambda d: d['x']))


class Biscuit:
    def __init__(self, size, value, tolerance):
        self.size = size
        self.value = value
        self.tolerance = tolerance

    def is_valid(self, defects):
        for defect_type, defect_number in defects.items():
            if defect_number >= self.tolerance[defect_type]:
                return False
        return True


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

    def get_biscuits(self):
        return self._biscuits

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
            new_biscuits = deepcopy(self._biscuits)
            rng.shuffle(new_biscuits)
            return new_biscuits
        else:
            return rng.shuffle(self._biscuits)

    def total_price(self):
        sum([biscuit.value for biscuit in self._biscuits])

    def number_of_biscuits(self):
        return len(self._biscuits)

    def fill_roll_random(self, remove_invalid_biscuits=False):
        integers = rng.integers(0, 3, 250)
        position = 0
        for i in integers:
            new_biscuit = biscuit_types[i]
            if position + new_biscuit.size >= self.roll_size:
                return
            else:
                if remove_invalid_biscuits:
                    defects_in_range = Roll.get_defects_between(position, position + new_biscuit.size)
                    if not new_biscuit.is_valid(defects_in_range):
                        self.append_biscuits([None])
                    else:
                        self.append_biscuits(new_biscuit)
                else:
                    self.append_biscuits(new_biscuit)

    def check_biscuits_tolerance(self):
        position = 0
        for i, biscuit in enumerate(self._biscuits):
            if biscuit is None:
                position += 1
                continue

            total_defects_at_position = dict()
            for defect in Roll.get_defects_between(position, position + biscuit.size):
                defect_class = defect['class']
                total_defects_at_position[defect_class] += 1
            if biscuit.is_valid(total_defects_at_position):
                return False, i

        return True

    @staticmethod
    def get_defects_between(a, b):
        return filter(lambda roll_defect: a < roll_defect['x'] < b, defects_list)

    @staticmethod
    def get_defects_between_iter(a, b):
        pass
