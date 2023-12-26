from biscuits import Roll


def bogo(max_iter):
    best_roll = None
    best_score = float('-inf')
    for _ in range(max_iter):
        roll = Roll(500)
        roll.fill_roll_random(check_biscuit_valid=True)
        v = roll.total_price(check_biscuit_valid=False)
        if v > best_score:
            best_roll = roll
            best_score = v

    return best_roll, best_score


print(bogo(1000))
