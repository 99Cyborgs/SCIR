def step_with_escape(step, x):
    while x < 0:
        if x == -1:
            break
        x = step(x)
        continue
    return x
