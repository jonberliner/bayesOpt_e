from numpy import linspace, repeat, zeros, eye
from numpy import array as npa
from numpy.random import RandomState
from jbgp_1d import K_se, conditioned_mu, conditioned_covmat, sample
from jbutils import cartesian
from os.path import isfile

from time import time
import pdb


def make_experiment(nTrial, nPassivePool, nActivePool, rng):
    nTrialType = len(nPassivePool) * len(nActivePool)
    assert nTrial % nTrialType == 0
    nPerNPassive = nTrial / len(nPassivePool)
    nPerNActive = nTrial / len(nActivePool)
    nPerTrialType = nTrial / nTrialType

    # col 0 is nPassive, col 1 is nActive
    # pdb.set_trace()
    trialTypeTuples = cartesian([nPassivePool, nActivePool])

    # get queue of how many obs per round
    trialParamsQueue = npa(make_nObsQueue(trialTypeTuples, nTrial, rng))
    nPassiveQueue = trialParamsQueue[:, 0]
    nActiveQueue = trialParamsQueue[:, 1]

    return {'nPassiveObsQueue': nPassiveQueue,
            'nActiveObsQueue': nActiveQueue}


def make_trial(nPassiveObs, domain, lenscale, sigvar, noisevar2, xSam_bounds, rng):

    assert len(domain.shape) == 1, 'domain must be 1d'
    cardDomain = len(domain)
    kDomain = K_se(domain, domain, lenscale, sigvar)
    muPrior = zeros(cardDomain)
    sam = sample(domain, muPrior, kDomain, noisevar2)
    # get valid samples
    good = False
    while not good:
        iObs = rng.randint(cardDomain, size=nPassiveObs)
        xObs = domain[iObs]
        if (xObs > xSam_bounds[0][0]).all() and (xObs < xSam_bounds[0][1]).all():
            yObs = sam[iObs]
            if (yObs.max() < (sigvar * 3.)) and (yObs.min() > (-sigvar * 3.)):
                good = True

    return {'sample': sam,
            'xObs': xObs,
            'yObs': yObs,
            'iObs': iObs}


def make_nObsQueue(nObsPool, nTrial, rng):
    """returns a nTrial long list of ints, with nTrial/nObsPool of each entry
    in nObsPool"""
    assert nTrial % len(nObsPool) == 0
    nPerNsam = nTrial / len(nObsPool)
    nObs_pool = repeat(nObsPool, nPerNsam, axis=0)
    nObs_order = rng.permutation(range(nTrial))
    nObs_queue = nObs_pool[nObs_order]

    return nObs_queue


# def sample_gp(domain, mu, covmat, noisevar2, rng=None):
#     """sample over domain given mean mu and covmat covmat"""
#     if not rng: rng = RandomState()
#     nI = domain.shape[0]
#     covmat += eye(nI) * noisevar2
#     sample = rng.multivariate_normal(mu, covmat)
#     return sample
