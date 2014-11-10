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
    nPerNsam = nRound / len(nObsPool)
    assert isInt(nPerNsam)
    nObs_pool = np.repeat(nObsPool, nPerNsam)
    nObs_order = rng.permutation(range(nRound))
    nObs_queue = nObs_pool[nObs_order]

    return nObs_queue


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

