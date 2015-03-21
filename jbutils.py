from numpy import asarray, prod, zeros, repeat, linspace, isscalar, fromstring, uint32
from matplotlib.pyplot import get_cmap
import cPickle
from numpy import array as npa
from json import loads, dumps


def jbpickle(obj, fname):
    """obj is the session object you're saving.  fname is the file name"""
    with open(fname, 'wb') as f:
        cPickle.dump(obj, f)

def jbunpickle(fname):
    """fname is the file name.  you have to assign to an object.
    e.g. unpickle('fname.py'), where file was saved as pickle(obj, 'fname.py')
    will not put the object obj in your environment.  you need to do
    obj = unpickle('fname.py')"""
    with open(fname) as f:
        obj = cPickle.load(f)

    return obj

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


def cmap_discrete(N, cmap):
    cm = get_cmap(cmap)
    return [cm(1.*i/N) for i in xrange(N)]


def make_domain_grid(domainBounds, domainRes):
    """takes domainBounds and domainRes for each dim of input space and grids
    accordingly"""
    #TODO: add sparse version with ndm

    domainBounds = npa(domainBounds)
    # get domain from bounds and res
    dimX = domainBounds.shape[0]
    if isscalar(domainRes):
        # equal res if scalar
        domainRes = repeat(domainRes, dimX)
    else:
        assert len(domainRes) == dimX

    domainRes = npa(domainRes)

    domain = npa([linspace(domainBounds[dim][0],
                           domainBounds[dim][1],
                           domainRes[dim])
                  for dim in xrange(dimX)])

    domain = cartesian(domain)
    return domain


def jsonToNpa(jstr, npa_type=float):
    array = loads(jstr)
    array = map(npa_type, array)
    return npa(array)


def pack_rngstate(rngstate):
    json_rngstate = [rngstate[0],  # string
                     rngstate[1].tolist(),  # npa(uint32) -> str
                     rngstate[2],  # int
                     rngstate[3],  # int
                     rngstate[4]]  # float
    json_rngstate = dumps(json_rngstate)
    return json_rngstate


def unpack_rngstate(json_rngstate):
    jrs = loads(json_rngstate)
    p0 = jrs[0].encode('ascii')  # numpy plays nice with ascii
    p1 = npa(jrs[1], dtype=uint32)  # unpack into numpy uint32 array
    p2 = int(jrs[2])
    p3 = int(jrs[3])
    p4 = float(jrs[4])
    return (p0, p1, p2, p3, p4)  # rngstate
