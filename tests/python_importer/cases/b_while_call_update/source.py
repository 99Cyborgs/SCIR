def step_until_nonneg(step, x):
    while x < 0:
        x = step(x)
    return x
