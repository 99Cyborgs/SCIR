def guard(may_fail, x):
    try:
        return may_fail(x)
    except ValueError:
        return 0
