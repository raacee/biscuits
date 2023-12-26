from biscuits import biscuit_types, defects_list, Roll


# Helper function to check if a biscuit can be placed considering defects and overlapping
def is_valid_position(start, biscuit, roll, defects_list):
    # Check for overlap
    for other in roll.get_biscuits():
        if start < other['end'] and other['start'] < start + biscuit.size:
            return False  # Overlap detected

    # Check defects within the biscuit's range
    defects_in_range = [defect for defect in defects_list if start <= defect['x'] < start + biscuit.size]
    defect_counts = {defect_class: 0 for defect_class in biscuit.tolerance.keys()}
    for defect in defects_in_range:
        defect_class = defect['class']
        defect_counts[defect_class] += 1
    
    return biscuit.is_valid(defect_counts)


# Backtracking algorithm
def place_biscuits(roll, biscuits, defects_list, position=0):
    if position >= roll.roll_size:  # Reached the end of the roll
        return roll.total_value(), roll.get_biscuits().copy()

    max_value = 0
    best_arrangement = None

    for biscuit in biscuits:
        if is_valid_position(position, biscuit, roll, defects_list):
            # Create a new biscuit dict to represent the placed biscuit
            biscuit_dict = {'start': position, 'end': position + biscuit.size, 'biscuit': biscuit}
            # Place the biscuit
            roll.append_biscuits(biscuit_dict)  # Now passing a dict object
            # Recurse to the next position
            value, arrangement = place_biscuits(roll, biscuits, defects_list, position + biscuit.size)
        else:
            # Consider not placing a biscuit at this position
            value, arrangement = place_biscuits(roll, biscuits, defects_list, position + 1)

        if value > max_value:
            max_value = value
            best_arrangement = arrangement

    return max_value, best_arrangement


# Instantiate a Roll object
roll = Roll(roll_size=500)
# Sort biscuits by value, descending (as a heuristic)
sorted_biscuits = sorted(biscuit_types, key=lambda b: -b.value)

# Find the best arrangement
total_value, arrangement = place_biscuits(roll, sorted_biscuits, defects_list)

# Create a new Roll object with the best arrangement
best_roll = Roll(roll_size=500)
best_roll._biscuits = arrangement  # Directly setting the best arrangement

# Now you can access the total value and other properties of the best_roll
print(f"The total value of the best roll is: {best_roll.total_value()}")

# To get the number of each biscuit type in the best arrangement
biscuit_count = {}
for biscuit_info in best_roll._biscuits:
    biscuit_type = type(biscuit_info['biscuit'])
    biscuit_count[biscuit_type] = biscuit_count.get(biscuit_type, 0) + 1

print("Number of each biscuit type in the best arrangement:")
for biscuit_type, count in biscuit_count.items():
    print(f"{biscuit_type}: {count}")
