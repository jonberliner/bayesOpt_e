from numpy import linspace, repeat, zeros, eye
from numpy.random import RandomState
from jbgp import K_se, conditioned_mu, conditioned_covmat, sample
from jbutils import jbunpickle
from os.path import isfile


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

    assert bool(xObs_sam3 is None) == bool(yObs_sam3 is None)
    assert bool(nObs==3) == bool(xObs_sam3 is not None)

    cardDomain = domain.shape[0]
    kDomain = K_se(domain, domain, lenscale, sigvar)
    if nObs == 3:  # draw random function passing through (xObs, yObs)
        xObs = xObs_sam3
        yObs = yObs_sam3
        muPost = conditioned_mu(domain, xObs, yObs, lenscale, sigvar, noisevar2)
        cmPost = conditioned_covmat(domain, kDomain, xObs, lenscale, sigvar, noisevar2)
        sam = sample_gp(domain, muPost, cmPost, noisevar2, rng)
        iObs = None
    else:  # draw random sample from prior and take random locations
        muPrior = zeros(cardDomain)
        sam = sample_gp(domain, muPrior, kDomain, noisevar2, rng)
        # get valid samples
        good = False
        while not good:
            iObs = rng.randint(nX, size=nObs)
            xObs = domain[iObs]
            if (xObs > xSam_bounds[0][0] and xObs < xSam_bounds[0][1]):
                good = True
        yObs = sam[iObs]

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


def sample_gp(domain, mu, covmat, noisevar2, rng=None):
    """sample over domain given mean mu and covmat covmat"""
    if not rng: rng = RandomState()
    nI = domain.shape[0]
    covmat += eye(nI) * noisevar2
    sample = rng.multivariate_normal(mu, covmat)
    return sample
