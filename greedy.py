from biscuits import biscuit_types, defects_list, Roll
from constraint import Problem


# Global access within this module for defects_list
def get_defects_between(start, end, defects_list):
    return [defect for defect in defects_list if start <= defect['x'] < end]

# Constraint to ensure no overlapping biscuits
def no_overlap_constraint(*positions):
    sizes = [b.size for b in biscuit_types]  # Access the global biscuit_types
    for i, pos in enumerate(positions[:-1]):
        if pos + sizes[i] > positions[i + 1]:
            return False
    return True

# Constraint to ensure defects are within tolerance
def defects_within_tolerance(*positions):
    for i, pos in enumerate(positions):
        biscuit = biscuit_types[i]  # Access the global biscuit_types
        defects_in_range = get_defects_between(pos, pos + biscuit.size, defects_list)
        defect_counts = {defect_class: 0 for defect_class in biscuit.tolerance.keys()}
        for defect in defects_in_range:
            defect_class = defect['class']
            defect_counts[defect_class] += 1
        if not biscuit.is_valid(defect_counts):
            return False
    return True

# Function to calculate the total value of biscuits on the roll
def calculate_total_value(*positions):
    total_value = 0
    for i, pos in enumerate(positions):
        total_value += biscuit_types[i].value
    return total_value

# Create the problem instance
problem = Problem()

# Variables for the positions of each biscuit type on the roll
roll_size = 500

# Assuming that biscuit_types are sorted by value with the most valuable first
biscuit_types.sort(key=lambda b: -b.value)
for i, biscuit in enumerate(biscuit_types):
    problem.addVariable(f"Biscuit_{i}", range(roll_size - biscuit.size + 1))

# Add constraints to the problem
problem.addConstraint(no_overlap_constraint, [f"Biscuit_{i}" for i in range(len(biscuit_types))])
problem.addConstraint(defects_within_tolerance, [f"Biscuit_{i}" for i in range(len(biscuit_types))])

# Heuristic approach
def greedy_heuristic():
    roll = Roll(roll_size=500)
    positions_filled = [False] * 500  # A simple way to track filled positions

    for biscuit in sorted(biscuit_types, key=lambda b: -b.value):  # Sort by value as a heuristic
        for position in range(roll.roll_size - biscuit.size + 1):
            if not any(positions_filled[position:position + biscuit.size]):  # Check if space is free
                defects_in_range = get_defects_between(position, position + biscuit.size, defects_list)
                defect_counts = {defect_class: 0 for defect_class in biscuit.tolerance.keys()}
                for defect in defects_in_range:
                    defect_class = defect['class']
                    defect_counts[defect_class] += 1

                if biscuit.is_valid(defect_counts):
                    # Fill the positions and add the biscuit to the roll
                    for i in range(position, position + biscuit.size):
                        positions_filled[i] = True  # Mark positions as filled
                    biscuit_dict = {'start': position, 'end': position + biscuit.size, 'biscuit': biscuit}
                    roll.append_biscuits(biscuit_dict)

    return roll

# Run the heuristic and get the Roll object with the best arrangement
best_roll = greedy_heuristic()

# Now you can access the total value and other properties of the best_roll
print(f"The total value of the best roll is: {best_roll.total_value()}")

# To get the number of each biscuit type in the best roll
biscuit_count = {}
for biscuit_info in best_roll._biscuits:
    biscuit_type = type(biscuit_info['biscuit'])
    biscuit_count[biscuit_type] = biscuit_count.get(biscuit_type, 0) + 1

print("Number of each biscuit type in the best roll:")
for biscuit_type, count in biscuit_count.items():
    print(f"{biscuit_type}: {count}")