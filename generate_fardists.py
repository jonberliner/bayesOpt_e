from jbfunctions import jbgp
import pandas as pd
import numpy as np
from numpy.random import RandomState
rng = RandomState()
from matplotlib import pyplot as plt
from numpy import mean, linspace
from scipy.spatial.distance import pdist
import pdb


def mu_lnnorm(v, n=2):
    """v is a 1d array.  gives the average pair-wise l-n-norm distance between
    all elts in v"""
    assert type(v) is list or len(v.shape) == 1
    pairwise_dists = pdist(zip(v), p=n)
    pairwise_dists = pairwise_dists ** n
    return mean(pairwise_dists)


def get_and_compare_mus(xObs, yObs, lenscalepool):
    X = linspace(0, 1, 1028)
    SIGVAR = 1.
    NOISEVAR2 = 1e-7
    conditioned_mus = [jbgp.conditioned_mu(X, xObs, yObs,
                                           lenscale, SIGVAR, NOISEVAR2)
                       for lenscale in lenscalepool]
    imaxes = [mu.argmax() for mu in conditioned_mus]
    xmaxes = [X[imax] for imax in imaxes]
    ymaxes = [conditioned_mus[ils][imax] for ils, imax in enumerate(imaxes)]
    mu_l2norm = mu_lnnorm(xmaxes, 2)
    return {'xObs': xObs,
            'yObs': yObs,
            'ihat': imaxes,
            'xhat': xmaxes,
            'yhat': ymaxes,
            'mu_l2norm': mu_l2norm}


def rank(array):
    order = array.argsort()[::-1]
    ranks = order.argsort()
    return ranks


def nsam_far(nsam, lenscalepool, ntries=10000):
    ncond = len(lenscalepool)
    # get valid x-y pairs to condition on
    xylenscalemu = []
    donesofar = 0
    while donesofar < ntries:
        good = False
        xObs = rng.rand(nsam)
        # assert that all yvals are positive (to assure max is not 0)
        while not good:
            yObs = rng.randn(nsam)
            if yObs.max() > 0: good = True
        # get the x-loc with best EV for all lss in lenscalepool
        xylenscalemu.append(get_and_compare_mus(xObs, yObs, lenscalepool))
        donesofar += 1

    xylenscalemu = pd.DataFrame(xylenscalemu)  # convert to df
    # rank how far the dists are
    xylenscalemu['rank_mu_l2norm'] = rank(xylenscalemu.mu_l2norm.values)
    xylenscalemu.set_index(xylenscalemu.rank_mu_l2norm, inplace=True)  # reindex
    # top = xylenscalemu[xylenscalemu.rank_mu_l2norm < ntop]  # get max dists
    return xylenscalemu


def plot_nsam_far(df, lenscalepool, i):
    """plot a test one"""
    dfi = df.loc[i]
    X = linspace(0, 1, 1028)
    ncond = len(lenscalepool)
    SIGVAR = 1.
    NOISEVAR2 = 1e-7
    conditioned_mus = [jbgp.conditioned_mu(X, dfi.xObs, dfi.yObs,
                                            lenscale, SIGVAR, NOISEVAR2)
                        for lenscale in lenscalepool]
    [plt.plot(X, mu) for mu in conditioned_mus]
    [plt.plot(dfi.xhat[i], dfi.yhat[i], 'ro', markersize=10, alpha=0.5)
            for i in range(ncond)]
    plt.plot(dfi.xObs, dfi.yObs, 'ko', markersize=5, alpha=0.3)
    plt.show()

