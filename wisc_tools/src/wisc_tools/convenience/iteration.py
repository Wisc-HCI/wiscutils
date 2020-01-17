try:
    from itertools import tee, izip

    def pairwise(iterable):
        a, b = tee(iterable)
        next(b, None)
        return izip(a, b)
except:
    from more_itertools import pairwise
