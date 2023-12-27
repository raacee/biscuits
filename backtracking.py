from biscuits import biscuit_types, defects_list, Roll


# Backtracking algorithm
def place_biscuits(roll, biscuits, position=0):
    if position >= roll.roll_size:  # Reached the end of the roll
        return roll.total_price(), roll.get_biscuits().copy()

    max_value = 0
    best_arrangement = None

    for biscuit in biscuits:
        possible_defects = Roll.get_defects_between(position, position + biscuit.size)
        if biscuit.is_valid(possible_defects):
            # Place the biscuit
            roll.append_biscuits(biscuit)  # Now passing a dict object
            # Recurse to the next position
            value, arrangement = place_biscuits(roll, biscuits, position + biscuit.size)
        else:
            # Consider not placing a biscuit at this position
            value, arrangement = place_biscuits(roll, biscuits, position + 1)

        if value > max_value:
            max_value = value
            best_arrangement = arrangement

    return max_value, best_arrangement


if __name__ == '__main__':
    # Instantiate a Roll object
    r = Roll(roll_size=8)

    # Find the best arrangement
    total_value, arrangement = place_biscuits(r, biscuit_types)

    # Now you can access the total value and other properties of the best_roll
    print(f"The total value of the best roll is: {r.total_price()}")
