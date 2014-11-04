from numpy import zeros, linspace, atleast_2d, dot, ones, eye, nan
from numpy.random import randn, RandomState, randint
from timeit import timeit
from numpy.linalg import cholesky, pinv
from sys import maxint
from jsbgp_cy import K_se
import pdb

rng = RandomState()

def sample(nX, mu, covmat):
    """sample over X given mean mu and covmat covmat"""
    nI = X.shape[0]
    Lun = cholesky(covmat)
    # draw samples with our shiny new posterior!
    seeds = rng.randn(nI)
    sample = (mu + dot(Lun, seeds))
    return sample


def condition(X, xObs, yObs, lenscale, sigvar, noisevar2):
    """condition on observations yObs at locations xObs,
    with prior defined by kf and mf, returning new mu and covmat over locs X"""
    nI = X.shape[0]
    nJ = xObs.shape[0]

    # get covarmat for observed points
    Kobs = K_se(xObs, xObs, lenscale, sigvar) + eye(nJ) * noisevar2
    invKobs = pinv(Kobs)  # invert

    Kun = K_se(X, X, lenscale, sigvar)  # covmat for unobs points (that will make up function)
    k = K_se(xObs, X, lenscale, sigvar)  # covmat for unobs points (that will make up function)

    mu = dot(dot(k.T, invKobs), yObs)  # exp val for points given obs
    covmat = Kun - dot(dot(k.T, invKobs), k)  # certainty of vals | obs

    return {'mu': mu,
            'covmat': covmat}
