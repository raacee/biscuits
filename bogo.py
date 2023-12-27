from biscuits_racel import Roll


def bogo(max_iter):
    best_roll = None
    best_score = float('-inf')
    for _ in range(max_iter):
        roll = Roll(500)
        roll.fill_roll_random(check_biscuit_valid=True)
        v = roll.total_price()
        if v > best_score:
            best_roll = roll
            best_score = v

    return best_roll, best_score


if __name__ == '__main__':
    best_r, best_s = bogo(500)
    print(f'Best price is : {best_s}, best number of biscuits is :{best_r.number_of_biscuits()}')
