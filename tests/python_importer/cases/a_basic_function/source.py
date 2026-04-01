def clamp_nonneg(x):
    y = x
    if y < 0:
        y = 0
    return y
