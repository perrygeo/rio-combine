import math

"""
Known issues:
This only works with positive integers up to 27-bits
Limit to positive 16 bit integers just to be safe
"""


def pair(k1, k2):
    """
    Cantor pairing function
    http://en.wikipedia.org/wiki/Pairing_function#Cantor_pairing_function
    """
    return long(0.5 * (k1 + k2) * (k1 + k2 + 1) + k2)


def depair(z):
    """
    Inverse of Cantor pairing function
    http://en.wikipedia.org/wiki/Pairing_function#Inverting_the_Cantor_pairing_function
    """
    w = math.floor((math.sqrt(8 * z + 1) - 1)/2)
    t = (w**2 + w) / 2
    y = z - t
    x = w - y
    return int(x), int(y)


if __name__ == '__main__':
    import random
    for b in [0] + [random.randint(0, 2 ** 16) for x in range(200)]:
        for a in [0] + [random.randint(0, 2 ** 16) for x in range(200)]:
            z = pair(a, b)
            print("pair({}, {}) => {}\t\tdepair({}) => {}".format(a, b, z, z, depair(z)))
            assert depair(z) == (a, b)
