from numpy import linspace, repeat, zeros, eye
from numpy.random import RandomState
from jbgp import K_se, conditioned_mu, sample
from jbutils import jbunpickle, jbpickle

## EXAMPLE PARAMS
DEMO = {}
DEMO['nObsPool'] = [2, 3, 4, 5, 6]
DEMO_ND2 = 5  # number of dists bt 2 points when 2 sams shown
DEMO['d2Pool'] = [1./2.**(n+1) for n in xrange(DEMO_ND2)]  # dists bt 2 sams when 2 shown
DEMO['nTrial'] = 200  # n round in experiment
DEMO['rngseed'] = 4245342523
DEMO_NX = 1028
DEMO['x'] = linspace(0, 1, DEMO_NX)
DEMO['lenscale'] = 0.05
DEMO['sigvar'] = 1.
DEMO['noisevar2'] = 1e-7
DEMO['edgeBuf'] = 0.05
# get demo experiment with:
# demoExp = gpExperiment.make_experiment(**gpExperiment.DEMO)
## END EXAMPLE PARAMS

def make_experiment(domain, xSam_bounds, lenscale, sigvar, noisevar2, rng,\
                    nTrial, nObsPool, edgeBuf, distType, lenscalepool, nToTest,\
                    dir_sam3=None, fnameTemplate_sam3=None, rngseed=None):

    assert bool(dir_sam3) == bool(fnameTemplate_sam3)  == bool(rngseed)  # all or nothing
    save_sam3 = bool(dir_sam3)
    assert nTrial % len(nObsPool) == 0
    nPerNObs = nTrial / len(nObsPool)

    ## try loading sam3Queues
    try:
        obs_sam3Queue = jbunpickle(''.join([dir_sam3,
                                       fnameTemplate_sam3,
                                       str(rngseed),
                                       '.pkl']))
    ## if not saved for this condition yet, build and save
    except:
        from generate_fardists import generate_fardists
        obs_sam3Queue = generate_fardists(distType, nPerNObs, 3, lenscalepool,\
                                     domain, xSam_bounds, edgeBuf,\
                                     sigvar, noisevar2, nToTest, rng)
        if save_sam3:
            fname = ''.join([dir_sam3,
                             fnameTemplate_sam3,
                             str(rngseed),
                             '.pkl'])
            jbpickle(obs_sam3Queue, fname)

    # load or make sam3 queues
    nObsQueue = make_nObsQueue(nObsPool, nTrial, rng)

    # get all obs tuples for experiment
    return {'nObsQueue': nObsQueue,
            'xObs_sam3Queue': obs_sam3Queue['xObs'],
            'yObs_sam3Queue': obs_sam3Queue['yObs']}

    # cmPrior = K_se(domain, domain, lenscale, sigvar)
    # muPrior = zeros_like(domain)


def make_trial(nObs, domain,\
               lenscale, sigvar, noisevar2,\
               xSam_bounds, xObs_sam3, yObs_sam3, rng):

    assert bool(xObs_sam3) == bool(yObs_sam3)
    assert bool(nObs==3) == bool(xObs_sam3)

    cardDomain = domain.shape[0]
    kDomain = K_se(domain, domain, lenscale, sigvar)
    if nObs == 3:  # draw random function passing through (xObs, yObs)
        xObs = sam3locsX
        yObs = sam3locsY
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
            xObs = X[iObs]
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
    nI = X.shape[0]
    covmat += eye(nI) * noisevar2
    sample = rng.multivariate_normal(mu, covmat)
    return sample