from numpy import linspace, repeat, zeros, eye
from numpy.random import RandomState
from jbgp_1d import K_se, conditioned_mu, conditioned_covmat, sample
from jbutils import jbunpickle
from os.path import isfile

from time import time


def make_experiment(nTrial, nObsPool, rng, dir_sam3, fnameTemplate_sam3, rngseed):
    assert nTrial % len(nObsPool) == 0
    nPerNObs = nTrial / len(nObsPool)

    ## load sam3Queues make with prep_sam3_queues.py
    fname = ''.join([dir_sam3, fnameTemplate_sam3, str(rngseed), '.pkl'])
    assert isfile(fname)
    obs_sam3Queue = jbunpickle(fname)

    # get queue of how many obs per round
    nObsQueue = make_nObsQueue(nObsPool, nTrial, rng)

    # shuffle sam3 queues
    order = rng.permutation(nPerNObs)
    obs_sam3Queue['xObs'][:] = obs_sam3Queue['xObs'][order]
    obs_sam3Queue['yObs'][:] = obs_sam3Queue['yObs'][order]

    # get all obs tuples for experiment
    return {'nObsQueue': nObsQueue,
            'xObs_sam3Queue': obs_sam3Queue['xObs'],
            'yObs_sam3Queue': obs_sam3Queue['yObs']}


def make_trial(nObs, domain,\
               lenscale, sigvar, noisevar2,\
               xSam_bounds, xObs_sam3, yObs_sam3, rng):

    assert len(domain.shape) == 1, 'domain must be 1d'
    if xObs_sam3 is not None:
        assert len(xObs_sam3.shape) == 1, 'xObs_sam3 must be 1d or None'
    assert bool(xObs_sam3 is None) == bool(yObs_sam3 is None)
    assert bool(nObs==3) == bool(xObs_sam3 is not None)

    cardDomain = len(domain)
    # t0 = time()
    kDomain = K_se(domain, domain, lenscale, sigvar)
    # print domain.shape
    # print 'tkDomain: ' + str(time()-t0)
    if nObs == 3:  # draw random function passing through (xObs, yObs)
        xObs = xObs_sam3
        yObs = yObs_sam3
        # t0 = time()
        muPost = conditioned_mu(domain, xObs, yObs, lenscale, sigvar, noisevar2)
        # tmu = time() - t0
        cmPost = conditioned_covmat(domain, kDomain, xObs, lenscale, sigvar, noisevar2)
        # tcm = time() - t0 - tmu
        sam = sample(domain, muPost, cmPost, noisevar2)
        # tsam = time() - t0 - tmu - tcm
        # print 'tmu: ' + str(tmu)
        # print 'tcm: ' + str(tcm)
        # print 'tsam: ' + str(tsam)
        iObs = None
    else:  # draw random sample from prior and take random locations
        muPrior = zeros(cardDomain)
        sam = sample(domain, muPrior, kDomain, noisevar2)
        # get valid samples
        good = False
        while not good:
            iObs = rng.randint(cardDomain, size=nObs)
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
    nObs_pool = repeat(nObsPool, nPerNsam)
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
