from scipy.spatial.distance import pdist
from pandas import DataFrame, concat
from numpy import array as npa
from numpy import repeat, isscalar, atleast_2d, mean, linspace, concatenate,\
                  empty, diag
from numpy.random import RandomState
from GPy.kern import RBF
from GPy.models import GPRegression
from jbutils import cartesian, rank, cmap_discrete, jbpickle, jbunpickle,\
                    make_domain_grid
from jbgp import K_se, conditioned_mu, conditioned_covmat
from matplotlib import pyplot as plt
import pdb

def demo():
    DISTTYPE = 'xXf'
    NEXP = 200
    NOBS = 3
    LENSCALEPOOL = [2.**-n for n in [2., 4., 6.]]
    DOMAINBOUNDS = [[0., 1.]]
    DOMAINRES = [100]
    SIGVAR = 1.
    NOISEVAR = 1e-7
    NTOTEST = 10000
    RNGSEED = None

    out = generate_fardists(DISTTYPE, NEXP, NOBS, LENSCALEPOOL, DOMAINBOUNDS,\
                            DOMAINRES, SIGVAR, NOISEVAR, NTOTEST, RNGSEED)
    return out


def generate_fardists(distType, nExp, nObs, lenscalepool, domain, xSam_bounds,\
                      sigvar=None, noisevar=None, nToTest=None, rngseed=None):

    if not sigvar: sigvar = 1.
    if not noisevar: noisevar = 1e-7
    if not nToTest: nToTest = nExp*100

    # generate random valid loc-val pairs for experiments

    obs = generate_rand_obs(nToTest, nObs, xSam_bounds, rngseed)
    xObs = obs['x']
    yObs = obs['y']

    # create domain
    domain = make_domain_grid(domainBounds, domainRes)

    # get loc-val of maxev for each lengthscale for each experiment
    evmaxes = [get_evmax(xObs, yObs, domain, lenscale, sigvar, noisevar)
               for lenscale in lenscalepool]

    # get average distance between maxes for each lenscale
    iExp_rankedByDist = get_ranked_dists(evmaxes, distType)

    # take only the top n ranked dists
    obs_fardists = get_obsNTopFar(nExp, evmaxes, iExp_rankedByDist)

    return obs_fardists


def generate_rand_obs(nExp, nObs, domainBounds, sigvar=None, rngseed=None):
    # create random sets of observations for each experiment
    if not sigvar: sigvar = 1.
    if not rngseed:
        rng = RandomState()
    else:
        rng = RandomState(rngseed)

    domainBounds = npa(domainBounds)
    dimX = domainBounds.shape[0]
    minX = domainBounds[:, 0]
    maxX = domainBounds[:, 1]
    rangeX = maxX - minX
    xObs = rng.uniform(size=(nExp, nObs, dimX))
    xObs *= rangeX
    xObs += minX
    yObs = empty(shape=(nExp, nObs))
    for iexp in xrange(nExp):
        good = False
        while not good:
            yObs0 = rng.normal(size=(nObs))
            if yObs0.max() > 0: good = True
        yObs[iexp, :] = yObs0
    # yObs = rng.normal(size=(nExp, nObs, 1))
    yObs *= sigvar

    return {'x': xObs,
            'y': yObs}


def get_evmax(xObs, yObs, domain, lenscale, sigvar=None, noisevar=None):
    """currently, nObs needs to be constant (i.e. xObs and yObs need to be
        rectangulat 3-tensors of shape (nExp x nObs x nDim) )"""
    if not sigvar: sigvar=1.
    if not noisevar: noisevar=1e-7  # default noiseless
    dimX = domain.shape[-1]

    if len(xObs.shape)==2:  # need rank3 tensor of shape (nExp x nObs x nDim)
        xObs = npa([xObs])
        yObs = npa([yObs])

    nExp, nObs, dimX0 = xObs.shape
    assert dimX0 == dimX
    kDomain = K_se(domain, domain, lenscale, sigvar)
    out = [run_exp_i(iexp, xObs, yObs, domain, kDomain, lenscale, sigvar, noisevar)
           for iexp in xrange(nExp)]

    return out


def run_exp_i(iExp, xObs, yObs, domain, kDomain,\
              lenscale, sigvar, noisevar):
    if iExp % 1000 == 0: print iExp
    xObs0 = xObs[iExp]
    yObs0 = yObs[iExp]
    postmu = conditioned_mu(domain, xObs0, yObs0, lenscale, sigvar, noisevar)
    imax = postmu.argmax()
    return {'xmax': domain[imax],
            'fmax': postmu[imax],
            'imax': imax,
            'lenscale': lenscale,
            'xObs': xObs0,
            'yObs': yObs0,
            'iExp': iExp}


def get_ranked_dists(evmaxes, distType):
    """evmaxes is a lolodicts generated with get_evmaxes.
    each evmaxes[i][j] must have keys [xmax, fmax, iExp].
    Returns dict with iExp and dist rank for iExp for each experimetn iExp,
    with distance metric determined by param distType in ['x', 'f', 'xXf']"""

    assert distType in ['x', 'f', 'xXf']

    # put into dataframe format
    evmaxes = [DataFrame(lsevmax) for lsevmax in evmaxes]  # make each ls dataframe
    evmaxes = concat(evmaxes)  # combine dataframes

    # make distance function based on param distType
    if distType=='x':
        dfcn = lambda df0: mu_lnnorm(concatenate(df0.xmax.values))
    elif distType=='f':
        dfcn = lambda df0: mu_lnnorm(concatenate(df0.fmax.values))
    elif distType=='xXf':
        dfcn = lambda df0: mu_lnnorm(concatenate(df0.fmax.values)) *\
                           mu_lnnorm(concatenate(df0.xmax.values))

    # get dist bt lenscale conds for each experiment iExp
    dfDists = evmaxes.groupby('iExp').apply(dfcn).reset_index()
    dfDists.rename(columns={0:'dist'}, inplace=True)
    dfDists['rank'] = rank(dfDists['dist'].values, descending=True)  # rank by dist
    dfDists['distType'] = distType

    # return as dict, not df
    usedFields = ['iExp', 'dist', 'rank', 'distType']
    iExps, dists, ranks, distTypes = [dfDists[f].values for f in usedFields]
    out = {iExp: {'dist': dists[ii], 'rank': ranks[ii], 'distType':distTypes[ii]}
           for ii, iExp in enumerate(iExps)}

    # out = {}
    # for ii, iExp in enumerate(iExps):
    #     out[iExp] = {'dist': dists[ii],
    #                  'rank': ranks[ii],
    #                  'distType': distTypes[ii]}
    return out


def get_obsNTopFar(N, evmaxes, iExp_rankedByDist):
    # filter to top N experiments with farthest distanced
    usedExps = [iexp for iexp in iExp_rankedByDist
                if iExp_rankedByDist[iexp]['rank'] < N]

    evmax = evmaxes[0]  # pick arbitrary lenscale from which to take obs
    # function to extract only obs from an experiment
    get_obs = lambda elt: {'xObs': elt['xObs'], 'yObs': elt['yObs']}
    # get the obss from exps that had highest mean dist for max bt lenscales
    out = [get_obs(exp) for exp in evmax if exp['iExp'] in usedExps]
    return out


def mu_lnnorm(v, n=2):
    """v is a 1d array_like.  gives the average pair-wise l_n-norm distance
    between all elts in v"""
    assert type(v) is list or len(v.shape) == 1
    pairwise_dists = pdist(zip(v), p=n)
    return mean(pairwise_dists)


def plot_fardists(domain, xObs, yObs, lenscalepool, sigvar=1., noisevar=1e-7, cmap='autumn'):
    plt.plot(xObs, yObs,\
            marker='o', color='black', mec='None', ls='None', alpha=0.3, markersize=10)
    nls = len(lenscalepool)
    cols = cmap_discrete(nls+2, cmap)
    for ils in xrange(nls):
        ls = lenscalepool[ils]
        postmu = conditioned_mu(domain, xObs, yObs, ls, sigvar, noisevar)
        kDomain = K_se(domain, domain, ls, sigvar)
        postcv = conditioned_covmat(domain, kDomain, xObs, ls, sigvar, noisevar)
        postsd = diag(postcv)
        col = cols[ils+1]
        plt.fill_between(domain.flatten(), postmu+postsd, postmu-postsd,\
                         facecolor=col, edgecolor='None', alpha=0.1)
        plt.plot(domain.flatten(), postmu, color=col)
        imax = postmu.argmax()
        xmax = domain[imax]
        ymax = postmu[imax]
        plt.plot(xmax, ymax,\
                 marker='o', color=col, mec='None', alpha=0.5, markersize=8)
    plt.show()

# def prep_for_gpy(x, dimX):
#     """def prep_for_gpy(x, dimX)

#     ensures obs matrix x, with expected input dim dimX, is properly
#     formatted to work with GPy"""

#     # prep observations if 1d
#     if dimX == 1:
#         x = atleast_2d(x)
#     assert len(x.shape)==2
#     if x.shape[1] != dimX: x = x.T
#     assert x.shape[1] == dimX
#     return x
