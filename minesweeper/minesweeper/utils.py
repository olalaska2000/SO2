from math import floor, log10


def is_boolean(x):
    choices = {"true": True, "false": False}

    if x not in choices.keys():
        raise ValueError("%s not in %s" % (x, choices.keys()))

    return choices[x]


def digits(n):
    """
    :param n: a real number, cast to integer
    :return: the number of digits of the integer part of n
    """
    n = abs(int(n))

    if n == 0:
        return 1

    return floor(log10(n)) + 1