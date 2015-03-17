from numpy import asarray, prod, zeros, repeat


def ndm(*args):
    """generates a sparse mesh from a list of numpy vecs.

    from:
    http://stackoverflow.com/questions/22774726/numpy-evaluate-function-on-a-grid-of-points
    """
    return [x[(None,)*i+(slice(None),)+(None,)*(len(args)-i-1)] for i, x in enumerate(args)]


def cartesian(arrays, out=None):
    """
    Generate a cartesian product of input arrays.

    Parameters
    ----------
    arrays : list of array-like
        1-D arrays to form the cartesian product of.
    out : ndarray
        Array to place the cartesian product in.

    Returns
    -------
    out : ndarray
        2-D array of shape (M, len(arrays)) containing cartesian products
        formed of input arrays.

    Examples
    --------
    >>> cartesian(([1, 2, 3], [4, 5], [6, 7]))
    array([[1, 4, 6],
           [1, 4, 7],
           [1, 5, 6],
           [1, 5, 7],
           [2, 4, 6],
           [2, 4, 7],
           [2, 5, 6],
           [2, 5, 7],
           [3, 4, 6],
           [3, 4, 7],
           [3, 5, 6],
           [3, 5, 7]])

    from:
    http://stackoverflow.com/questions/1208118/using-numpy-to-build-an-array-of-all-combinations-of-two-arrays
    """
    arrays = [asarray(x) for x in arrays]
    dtype = arrays[0].dtype

    n = prod([x.size for x in arrays])
    if out is None:
        out = zeros([n, len(arrays)], dtype=dtype)

    m = n / arrays[0].size
    out[:,0] = repeat(arrays[0], m)
    if arrays[1:]:
        cartesian(arrays[1:], out=out[0:m,1:])
        for j in xrange(1, arrays[0].size):
            out[j*m:(j+1)*m,1:] = out[0:m,1:]
    return out


def rank(array, descending=True):
    order = array.argsort()
    if descending: order = order[::-1]  # reverse array
    ranks = order.argsort()
    return ranks
