import numpy as np
from biscuits_racel import Roll, biscuit_types
from numpy.random import default_rng

# assign rng
rng = default_rng()

# name of bees
# We added these names for debugging purposes
names = ["Patricia",
         "Jaqueline",
         "Georgia",
         "Valentine",
         "Sylvie",
         "Aurore",
         "Sandrine",
         "Catherine",
         "Véronique",
         "Marie-Paule",
         "Annelise",
         "Olga",
         "Édmée",
         "Anahide",
         "Zoé"]


def evaluate_roll(roll):
    if roll.check_biscuits_tolerance():
        return roll.total_price()
    else:
        return 0.0


# This function by default searches for the maximum of the objective function
# Use the opposite of the function if you are searching for the minimum
def bee_search(obj_func,
               minimize=False,
               n_bees=10,
               n_workers=None,
               n_scouts=1,
               max_iter=1000,
               limit=5):
    # The minimize parameter indicates whether the objective function should be minimized,
    # in which case it should maximize the opposite, or not.
    if minimize:
        def fitness(roll):
            return -1 * obj_func(roll)
    else:
        def fitness(roll):
            return obj_func(roll)

    # initializing the number of worker bees, if None
    if n_workers is None:
        n_workers = n_bees // 2

    # Each worker should be assigned a food source
    # So the number of food source is equal to the number of workers
    n_foods = n_workers

    # initialize the hive
    hive = Hive({
        'scouts': [Scout(fitness, name=rng.choice(names)) for _ in range(0, n_scouts)],
        'onlookers':
            [Onlooker(fitness, name=rng.choice(names)) for _ in range(0, n_bees - n_workers)],
        'workers': [Worker(fitness, name=rng.choice(names)) for _ in range(0, n_workers)]
    })

    # generate an array of random coordinates in the search space
    # of shape [[...] * food_sources_initial]
    initial_foods = generate_new_food(n_foods, food_quantity=limit)

    # Send all workers at the initial food
    for worker, food in zip(hive.get_workers(), initial_foods):
        worker.go_to_food(food)
        worker.dance()

    # Get the initial best food
    best_quality_food = max(hive.get_workers(), key=lambda worker_bee: worker_bee.food.quality).food

    # Algorithm loop
    for i in range(max_iter):
        """Workers phase"""

        for worker in hive.get_workers():
            # We first check if the source has been depleted by the onlookers
            # Indeed we gave the ability for onlooker to bring food to the hive, 
            # so the food source gets depleted by both type of bees.
            # Because of the loop, if we have a food source of quantity value 0,
            # the worker bee has to leave and join the scouts to search for a new food source.
            if worker.should_leave():
                new_scout = worker.leave_food_point()
                hive.get_scouts().append(new_scout)
                hive.get_workers().remove(worker)
                continue

            worker.dance()  # Workers register their food source and give them a food source quality value

            # Search for a better food source around the current food source
            new_solution = worker.look_around()
            # Evaluate food source
            new_solution_evaluation = worker.calculate_nectar(new_solution)
            # If food source is better, discard old food source and select new open
            # Else bring food to the hive, or leave if no more food is available
            if new_solution_evaluation > worker.food.quality:
                worker.food = new_solution
                worker.dance()
                if new_solution_evaluation > best_quality_food.quality:
                    best_quality_food = new_solution
            else:
                worker.bring_food()
                if worker.should_leave():
                    new_scout = worker.leave_food_point()
                    hive.get_scouts().append(new_scout)
                    hive.get_workers().remove(worker)

        """Onlookers phase"""
        # Onlookers choose a food source, among the worker ones.
        # This choice is made by probabilities, 
        # otherwise they'd just choose the best one and never explore around the other ones.

        # Calculate the probability value of the sources
        # with which they are preferred by the onlooker bees
        # First they watch the bees dance
        # choreography is of type (worker, worker.food, food.quality)
        choreography = np.array([worker.dance() for worker in hive.get_workers()])
        # print([c.quality for c in choreography[:, 0]])
        choreography[:, 1] = np.array([dance if dance > float('-inf') else 0 for dance in choreography[:, 1]])
        # convert -inf to 0
        choreography[:, 1] = np.abs(np.nan_to_num(choreography[:, 1]))
        # calculate the sum of all the qualities
        sum_dances = np.sum(choreography[:, 1])
        # for functions that are flat on most of their definition space, sum could be zero
        # we have to check for that condition to prevent having nan values in the probabilities list
        if sum_dances == 0.0:
            probabilities = None
        else:
            # divide each value to get the probability for the onlooker to choose that food source
            probabilities = np.divide(choreography[:, 1], sum_dances).astype('float64')
            # In that case, every food source has the same probability of being chosen which is not optimal.
            # We want to have most likeliness for the most promising source

        for onlooker in hive.get_onlookers():
            # Onlookers choose a food source, then dance.
            onlooker.choose_preferred_source(choreography[:, 0], probabilities)
            onlooker.dance()
            # Onlookers search for a new food source
            new_solution = onlooker.look_around()
            # Evaluate food source
            new_solution_evaluation = onlooker.calculate_nectar(new_solution)
            # If food source is better, discard old food source and select new food source
            if new_solution_evaluation > onlooker.food.quality:
                onlooker.food = new_solution
                onlooker.dance()
                if new_solution_evaluation > best_quality_food.quality:
                    best_quality_food = new_solution
            # Else increase limit counter
            else:
                if onlooker.food.has_food():
                    onlooker.bring_food()
                # If the food is exhausted, leave the food source
                if onlooker.should_leave():
                    onlooker.leave_food_point()

        """Scouts phase"""
        # Scouts search for a new food source around the search space. 
        for scout in hive.get_scouts():
            # Find a new food source
            scout.find_new_food(quantity=limit)
            # Convert back to worker and go on that food source
            new_worker = scout.convert_worker(fitness)
            hive.get_scouts().remove(scout)
            hive.get_workers().append(new_worker)

    return best_quality_food


class Hive:

    def __init__(self, bees):
        self.bees = bees

    def get_workers(self):
        return self.bees['workers']

    def get_onlookers(self):
        return self.bees['onlookers']

    def get_scouts(self):
        return self.bees['scouts']

    def get_unemployed(self):
        return self.bees['scouts'] + self.bees['onlookers']


class Bee:
    # job is the bee's job, either onlooker, employee, or scout
    # evaluate is the value of the food location by the objective function of the alg, see the
    # food_source is the food source coordinates on which the flower is located
    # it is the possible solution it represents
    def __init__(self, evaluate, food=None, name=None):
        self.food = food
        self.name = name
        self._evaluate = evaluate

    def go_to_food(self, food):
        self.food = food

    def calculate_nectar(self, food=None):
        if food is None:
            return self._evaluate(self.food.location)
        else:
            return self._evaluate(food.location)


class EmployedBee(Bee):

    def should_leave(self):
        return self.food.is_exhausted()

    def bring_food(self):
        self.food.quantity -= 1

    def look_around(self):
        return single_axis_change(self.food)

    def dance(self):
        if self.food.quality is None:
            quality = self.calculate_nectar(self.food)
            self.food.quality = quality
        return self.food, self.food.quality


class Worker(EmployedBee):

    def leave_food_point(self):
        self.food = None
        return Scout(self._evaluate, name=self.name)


class Onlooker(EmployedBee):

    def leave_food_point(self):
        self.food = None

    def choose_preferred_source(self, choreography, probabilities=None):
        self.go_to_food(rng.choice(choreography, p=probabilities))


class Scout(Bee):

    def find_new_food(self, quantity=1):
        new_food = generate_new_food(1, quantity)
        self.food = new_food

    def convert_worker(self, evaluate):
        return Worker(evaluate, food=self.food, name=self.name)


# generate an array of random coordinates in the search space of shape  (*,food_sources_initial)
def generate_new_food(number_of_food_sources, food_quantity=5):
    if number_of_food_sources == 1:
        new_roll = Roll(500)
        new_roll.fill_roll_random()
        return Food(new_roll, quantity=food_quantity)

    foods = []
    for i in range(number_of_food_sources):
        new_roll = Roll(500)
        new_roll.fill_roll_random()
        foods.append(Food(new_roll, quantity=food_quantity))

    return foods


def single_axis_change(original_food, quantity=5):
    old_roll = original_food.location
    number_of_biscuits = old_roll.number_of_biscuits()
    swap_index = rng.integers(number_of_biscuits)
    new_roll = old_roll
    new_roll.get_biscuits().pop(swap_index)
    new_biscuit = rng.choice(biscuit_types)
    new_roll.insert_biscuits(swap_index, new_biscuit)
    new_food = Food(new_roll, quantity=quantity)
    return new_food


class Food:

    def __init__(self, location, quality=None, quantity=0.0):
        self.location = location
        # quality will be determined upon dancing
        self.quality = quality
        self.quantity = quantity

    def has_food(self):
        return self.quantity > 0

    def is_exhausted(self):
        return self.quantity == 0


if __name__ == '__main__':
    best_food = bee_search(evaluate_roll,
                           minimize=False,
                           n_bees=50,
                           n_scouts=1,
                           max_iter=100,
                           limit=1)
    print(f'Best price is : {best_food.location.total_price()}, best number of biscuits is :{best_food.location.number_of_biscuits()}')
    print(f'Best food biscuit counts is : {best_food.location.biscuit_type_count()}')
