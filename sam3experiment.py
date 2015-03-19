import numpy as np
from numpy.random import RandomState, randint
from jbgp import K_se, conditioned_mu, sample
from jbutils import jbunpickle, jbpickle

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

def make_experiment(domain, xSam_bounds,\
                    lenscale, sigvar, noisevar2,\
                    rngseed, nRound, nObsPool, edgeBuf,\
                    distType, lenscalepool, nToTest,\
                    dir_sam3=None, fnameTemplate_sam3=None):

    assert bool(dir_sam3) == bool(fnameTemplate_sam3)  # all or nothing
    assert nRound % len(nObsPool) == 0
    nPerNObs = nRound / len(nObsPool)
    save_sam3 = bool(dir_sam3)

    rng = RandomState(rngseed)

    try:
        obs_sam3 = jbunpickle(''.join([dir_sam3,
                                       fnameTemplate_sam3,
                                       str(rngseed),
                                       '.pkl']))
    except:
        from generate_fardists import generate_fardists
        obs_sam3 = generate_fardists(distType, nPerNObs, 3, lenscalepool,\
                                     domain, xSam_bounds, edgeBuf,\
                                     sigvar, noisevar2, nToTest, rngseed)
        if save_sam3:
            fname = ''.join([dir_sam3,
                             fnameTemplate_sam3,
                             str(rngseed),
                             '.pkl'])
            jbpickle(obs_sam3, fname)

    # load or make sam3 queues
    nObsQueue = _make_nObsQueue(nObsPool, nRound, rng)
    xObs_sam3 = obs_sam3['xObs']
    yObs_sam3 = obs_sam3['yObs']

    return {'nObsQueue': nObsQueue,
            'd2locsQueueX': d2locsQueueX,
            'd2locsQueueY': d2locsQueueY,
            'D2L1Inds': D2L1Inds}

# BEGIN DEFS
def _make_nObsQueue(nObsPool, nRound, rng):
    """returns a nRound long list of ints, with nRound/nObsPool of each entry
    in nObsPool"""
    assert nRound % len(nObsPool) == 0
    nPerNsam = nRound / len(nObsPool)
    nObs_pool = np.repeat(nObsPool, nPerNsam)
    nObs_order = rng.permutation(range(nRound))
    nObs_queue = nObs_pool[nObs_order]

    return nObs_queue


def make_trial(nObs, domain, xSam_bounds, lenscale, sigvar, noisevar2, xObs_sam3, sam3locsY):
    nX = len(domain)
    # cm_prior is sqexp kernel with lengthscale lenscale and signal variance sigvar)
    cm_prior = K_se(domain, domain, lenscale, sigvar)
    if nObs == 3:
        xObs = sam3locsX
        yObs = sam3locsY
        mu = conditioned_mu(domain, xObs, yObs, lenscale, sigvar, noisevar2)
        cm = conditioned_covmat(domain, cm_prior, xObs, lenscale, sigvar, noisevar2)
        sam = sample(domain, mu, cm, noisevar2)
        iObs = None
    else:
        # mu_prior will always be assumed to be the zero-mean prior
        mu_prior = np.zeros_like(domain)
        sam = sample(domain, mu_prior, cm_prior, noisevar2)
        # get valid samples
        good = False
        while not good:
            iObs = randint(nX, size=nObs)
            xObs = X[iObs]
            if (xObs > xSam_bounds[0][0] and xObs < xSam_bounds[0][1]):
                good = True
        yObs = sam[iObs]

    return {'sample': sam,
            'xObs': xObs,
            'yObs': yObs,
            'iObs': iObs}