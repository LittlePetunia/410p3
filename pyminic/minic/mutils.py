# Because Python3 returns a map for map, and python2.7 a list.
def lmap(f, l):
    return [f(x) for x in l]