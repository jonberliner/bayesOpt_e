import numpy as np
from numpy.random import RandomState, randint
from jbgp import K_se, condition, sample

isInt = lambda x: x == round(x)

## EXAMPLE PARAMS
DEMO = {}
DEMO['nObsPool'] = [2, 3, 4, 5, 6]
DEMO_ND2 = 5  # number of dists bt 2 points when 2 sams shown
DEMO['d2Pool'] = [1./2.**(n+1) for n in xrange(DEMO_ND2)]  # dists bt 2 sams when 2 shown
DEMO['nRound'] = 200  # n round in experiment
DEMO['rngseed'] = 4245342523
DEMO_NX = 1028
DEMO['x'] = np.linspace(0, 1, DEMO_NX)
DEMO['lenscale'] = 0.05
DEMO['sigvar'] = 1.
DEMO['noisevar2'] = 1e-7
DEMO['edgeBuf'] = 0.05
# get demo experiment with:
# demoExp = gpExperiment.make_experiment(**gpExperiment.DEMO)
## END EXAMPLE PARAMS


# BEGIN DEFS
def _make_nObsQueue(nObsPool, nRound, rng):
    """returns a nRound long list of ints, with nRound/nObsPool of each entry
    in nObsPool"""
    nPerNsam = nRound / len(nObsPool)
    assert isInt(nPerNsam)
    nObs_pool = np.repeat(nObsPool, nPerNsam)
    nObs_order = rng.permutation(range(nRound))
    nObs_queue = nObs_pool[nObs_order]

    return nObs_queue


def _make_d3locsQueue(edgeBuf, nPerD3)

def _make_d2locsQueue(d2pool, edgeBuf, nPerD2, nPerNSam, rng):
    nD2 = len(d2pool)
    L1rawpool = np.linspace(0+edgeBuf, 1-edgeBuf, nPerD2)  # linspace of loc1 (will be scale in the for-loop)

    D2inds = np.repeat(range(nD2), nPerD2)  # indices of dists bt two points used in experiment
    assert len(D2inds) == nPerNSam
    L1inds = np.tile(range(nPerD2), nD2)  # indices of location one of two points
    D2L1inds = np.vstack([D2inds, L1inds]).T
    rng.shuffle(D2L1inds)

    d2locs_queueX = np.ones([len(D2inds), 2])*np.nan  # init
    d2locs_queueY = np.ones([len(D2inds), 2])*np.nan  # init
    for iv, ii in enumerate(D2L1inds):
        id2 = ii[0]  # get IND OF dist bt 2 points for this trial
        il1 = ii[1]  # get IND OF location of point 1 for this trial
        d0 = d2pool[id2]  # get dist bt 2 points
        loc1 = L1rawpool[il1] * (1.-d0)  # get loc 1
        d2locs_queueX[iv, 0] = loc1
        d2locs_queueX[iv, 1] = loc1 + d0  # get location 2
        d2locs_queueY[iv, :] = rng.randn(2)  # get y-vals for these locations

    return {'d2locs_queueX': d2locs_queueX,
            'd2locs_queueY': d2locs_queueY,
            'D2L1inds': D2L1inds}


def make_trial(nObs, X, lenscale, sigvar, noisevar2, d2locsX, d2locsY):
    nX = len(X)
    if nObs == 2:
        xObs = d2locsX
        yObs = d2locsY
        post_gp = condition(X, xObs, yObs, lenscale, sigvar, noisevar2)
        sam = sample(X, post_gp['mu'], post_gp['covmat'], noisevar2)
        iObs = None
    else:
        # mu_prior will always be assumed to be the zero-mean prior
        mu_prior = np.zeros_like(X)
        # covmat_prior is sqexp kernel w lenscale LENSCALE and signal variance SIGVAR)
        covmat_prior = K_se(X, X, lenscale, sigvar)  # get covmat for prior
        sam = sample(X, mu_prior, covmat_prior, noisevar2)
        iObs = randint(nX, size=nObs)
        xObs = X[iObs]
        yObs = sam[iObs]

    return {'sample': sam,
            'xObs': xObs,
            'yObs': yObs,
            'iObs': iObs}


def make_experiment(nRound, nObsPool, d2Pool, edgeBuf, x, lenscale, sigvar, noisevar2, rngseed):
    rng = RandomState(rngseed)
    nPerNSam = nRound / len(nObsPool)
    assert isInt(nPerNSam)
    nD2 = len(d2Pool)
    nPerD2 = nPerNSam / nD2
    assert isInt(nPerD2)

    nObsQueue = _make_nObsQueue(nObsPool, nRound, rng)
    dist2stuff = _make_d2locsQueue(d2Pool, edgeBuf, nPerD2, nPerNSam, rng)
    d2locsQueueX = dist2stuff['d2locs_queueX']
    d2locsQueueY = dist2stuff['d2locs_queueY']
    D2L1Inds = dist2stuff['D2L1inds']

    return {'nObsQueue': nObsQueue,
            'd2locsQueueX': d2locsQueueX,
            'd2locsQueueY': d2locsQueueY,
            'D2L1Inds': D2L1Inds}


from jbfunctions import jbgp
import pandas as pd
import numpy as np
from numpy.random import RandomState
rng = RandomState()
from matplotlib import pyplot as plt

def rank(array):
    order = array.argsort()[::-1]
    ranks = order.argsort()
    return ranks

NSAM = 3
NTRIES = 10000

X = np.linspace(0, 1, 1028)
LENSCALEPOOL = [2**n for n in [-2, -4, -6]]
NCOND = len(LENSCALEPOOL)
SIGVAR = 1.
NOISEVAR2 = 1e-7

PRIOR_COVMATS = [jbgp.K_se(X,X,lenscale, SIGVAR) for lenscale in LENSCALEPOOL]
PRIOR_MUS = [np.zeros_like(X) for _ in range(len(LENSCALEPOOL))]

donesofar = 0
def compare_mus(xObs, yObs):
    conditioned_mus = [jbgp.conditioned_mu(X, xObs, yObs,
                                           lenscale, SIGVAR, NOISEVAR2)
                       for lenscale in LENSCALEPOOL]
    imaxes = [mu.argmax() for mu in conditioned_mus]
    xmaxes = [X[imax] for imax in imaxes]
    ymaxes = [conditioned_mus[ils][imax] for ils, imax in enumerate(imaxes)]
    ptpxhat = np.ptp(xmaxes)
    return {'xObs': xObs,
            'yObs': yObs,
            'ihat': imaxes,
            'xhat': xmaxes,
            'yhat': ymaxes,
            'ptpxhat': ptpxhat}

out = []
while donesofar < NTRIES:
    good = False
    xObs = rng.rand(NSAM)
    while not good:
        yObs = rng.randn(NSAM)
        if yObs.max() > 0: good = True

    out.append(compare_mus(xObs, yObs))
    donesofar += 1

out = pd.DataFrame(out)
out['rank_ptpxhat'] = rank(out.ptpxhat.values)
out.set_index(out.rank_ptpxhat, inplace=True)
