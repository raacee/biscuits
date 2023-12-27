from csv import DictReader
from copy import deepcopy
import numpy as np

rng = np.random.default_rng()

with open('defects.csv', 'r') as f:
    defects_list = DictReader(f)

    # This throws a bug that empties defects_list
    # defect_types = set([defect['class'] for defect in defects_list])

    def x_to_float(elem):
        elem['x'] = float(elem['x'])
        return elem


    defects_list = map(x_to_float, defects_list)
    defects_list = list(sorted(defects_list, key=lambda d: d['x']))
    defect_types = set([defect['class'] for defect in defects_list])


class Biscuit:
    def __init__(self, size, value, tolerance):
        self.size = size
        self.value = value
        self.tolerance = tolerance

    def is_valid(self, defects):
        defects_sums = self.dict_sums_defects(defects)
        if defects_sums.keys() != self.tolerance.keys():
            raise ValueError('Defects keys are different')
        for k in defects_sums:
            if self.tolerance[k] < defects_sums[k]:
                return False
        return True

    @staticmethod
    def dict_sums_defects(defects):
        defects_sums = {defect_type: 0 for defect_type in defect_types}
        for defect in defects:
            defect_type = defect['class']
            defects_sums[defect_type] += 1

        return defects_sums


# array of different types of biscuit
# this array will contain the 4 types of biscuit
# it will also provide the program with 4 pointers (each for each type of biscuit),
# that will allow to access biscuit characteristics without copying the instance
biscuit_types = [
    Biscuit(8, 12, {'a': 5, 'b': 4, 'c': 4}),
    Biscuit(5, 8, {'a': 2, 'b': 3, 'c': 2}),
    Biscuit(4, 6, {'a': 4, 'b': 2, 'c': 3}),
    Biscuit(2, 1, {'a': 1, 'b': 2, 'c': 1})
]


class Roll:
    def __init__(self, roll_size=500):
        self.roll_size = roll_size
        self._biscuits = []

    def __str__(self):
        return str(self._biscuits)

    def get_biscuits(self, index1=0, index2=None):
        return self._biscuits[index1:index2]

    def insert_biscuits(self, index, biscuit):
        self._biscuits.insert(index, biscuit)

    def append_biscuits(self, biscuits):
        if isinstance(biscuits, list):
            self._biscuits += biscuits
        elif isinstance(biscuits, Biscuit) or isinstance(biscuits, dict):
            self._biscuits.append(biscuits)
        else:
            raise ValueError(f'Biscuits should be a list or a Biscuit, biscuit is {biscuits.__class__.__name__}')

    def invert_biscuits(self, index1, index2, copy=False):
        if copy:
            roll_copy = deepcopy(self)
            roll_copy.invert_biscuits(index1, index2)
            return roll_copy
        self._biscuits[index1], self._biscuits[index2] = self._biscuits[index2], self._biscuits[index1]

    def mix_biscuits(self, copy=False):
        if copy:
            new_biscuits = deepcopy(self._biscuits)
            rng.shuffle(new_biscuits)
            return new_biscuits
        else:
            return rng.shuffle(self._biscuits)

    # returns the price of all the biscuits in the roll to be sold
    # is the function to be optimized so the company can fit the arrangement of biscuits that will maximize
    def total_price(self):
        return sum([
            biscuit.value if isinstance(biscuit, Biscuit)
            else biscuit['biscuit'] if isinstance(biscuit, Biscuit)
            else 0 for biscuit in self._biscuits
        ])

    def number_of_biscuits(self):
        return len(self._biscuits)

    def dough_length(self):
        return sum([biscuit.size for biscuit in self._biscuits])

    # function that fills the roll randomly
    def fill_roll_random(self, check_biscuit_valid=True):
        # list of random integers between 0 and 3
        # the list goes from 0 to 250, as the smallest biscuit is of size 2 and the roll length is 500
        integers = rng.integers(0, 4, size=self.roll_size // 2)
        # the position cursor keeps track of the length of the all the biscuits currently on the roll
        position = 0
        for i in integers:
            new_biscuit = biscuit_types[i]
            defects_in_range = Roll.get_defects_between(position, position + new_biscuit.size)
            # if the biscuit spills over the roll, we try to find a biscuit that fits at the end among the biscuit types
            if position + new_biscuit.size >= self.roll_size:
                if check_biscuit_valid:
                    best_fit_biscuit = Roll.replace_defect_biscuit(position, size_limit=self.roll_size - position)
                    self.append_biscuits([best_fit_biscuit])
                    if best_fit_biscuit is not None:
                        position += best_fit_biscuit.size
                    else:
                        position += 1
                    return
                else:
                    return

            # if there's room for the biscuit, we add it to the roll and check its defects
            if check_biscuit_valid:
                if new_biscuit.is_valid(defects_in_range):
                    self.append_biscuits(new_biscuit)
                    position += new_biscuit.size
                # if the biscuit is not valid, we try to add an other biscuit from the biggest to the smallest
                # the array of biscuits is already sorted, so we can directly iterate over them
                else:
                    best_fit_biscuit = Roll.replace_defect_biscuit(position)
                    self.append_biscuits([best_fit_biscuit])
                    if best_fit_biscuit is not None:
                        position += best_fit_biscuit.size
                    else:
                        position += 1
            else:
                self.append_biscuits(new_biscuit)
                position += new_biscuit.size

    # Checks if the all the biscuits in the roll satisfy their constraint of defects
    def check_biscuits_tolerance(self):
        position = 0
        for i, biscuit in enumerate(self._biscuits):
            # if no biscuit is at position, advance and go to next iteration
            if biscuit is None:
                position += 1
                continue
            # else we have to retrieve the defects present on the biscuit from the defects_list
            # and check if the biscuit is valid
            defects_in_range = Roll.get_defects_between(position, position + biscuit.size)
            if not biscuit.is_valid(defects_in_range):
                return False
        return True

    # counts the number of biscuit of each type in the roll
    # returns a dict with biscuit size as key and the number of their occurrences in the roll
    def biscuit_type_count(self):
        biscuits_counts = {biscuit_type.size: 0 for biscuit_type in biscuit_types}
        for biscuit_type in self._biscuits:
            if biscuit_type is not None:
                biscuits_counts[biscuit_type.size] += 1
        return biscuits_counts

    # try to replace defect biscuit with an other biscuit
    @staticmethod
    def replace_defect_biscuit(position, size_limit=-1):
        for biscuit_type in biscuit_types:
            defects_in_range = Roll.get_defects_between(position, position + biscuit_type.size)
            if biscuit_type.is_valid(defects_in_range) and biscuit_type.size < size_limit:
                return biscuit_type
        return None

    # get defects on the roll between two positions
    @staticmethod
    def get_defects_between(a, b):
        return [defect for defect in defects_list if a < defect['x'] < b]

    # not implemented and not used
    # get defects on the roll between two positions
    # the idea was to store the position in a variable and to return a generator that would keep the position as a value
    # so the function would skip all the positions
    # that would have an x value before the current position of the generator and retrieves defects faster
    @staticmethod
    def get_defects_between_iter(a, b):
        raise NotImplementedError

    # returns a roll with options
    # not used
    @staticmethod
    def create_roll(**options):
        if options.get('random'):
            r = Roll()
            r.fill_roll_random()
            return r


if __name__ == '__main__':
    roll = Roll(500)
    roll.fill_roll_random()
    print(roll.total_price())
    print(roll.biscuit_type_count())
