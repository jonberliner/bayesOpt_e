from scipy.spatial.distance import pdist
from pandas import DataFrame, concat
from numpy import array as npa
from numpy import repeat, isscalar, atleast_2d, mean, linspace, concatenate
from numpy.random import RandomState
rng = RandomState()
from GPy.kern import RBF
from GPy.models import GPRegression
from jbutils import cartesian, rank

import pdb

def demo():
    DISTTYPE = 'x'
    NEXP = 200
    NOBS = 3
    LENSCALEPOOL = [2.**-n for n in [2., 4., 6.]]
    DOMAINBOUNDS = [[0., 1.]]
    DOMAINRES = [100]
    SIGVAR = 1.
    NOISEVAR = 1e-7
    NTOTEST = 10000

    out = generate_fardists(DISTTYPE, NEXP, NOBS, LENSCALEPOOL, DOMAINBOUNDS,\
                            DOMAINRES, SIGVAR, NOISEVAR, NTOTEST)
    return out


def generate_fardists(distType, nExp, nObs, lenscalepool, domainBounds, domainRes,\
                      sigvar=None, noisevar=None, nToTest=None):
    if not nToTest: nToTest = nExp*100

    # generate random valid loc-val pairs for experiments
    obs = generate_rand_obs(nToTest, nObs, domainBounds)
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
    fardist_obs = get_obsNTopFar(nExp, evmaxes, iExp_rankedByDist)
    return fardist_obs


def generate_rand_obs(nExp, nObs, domainBounds, sigvar=None):
    # create random sets of observations for each experiment
    if not sigvar: sigvar = 1.

    domainBounds = npa(domainBounds)
    dimX = domainBounds.shape[0]
    minX = domainBounds[:, 0]
    maxX = domainBounds[:, 1]
    rangeX = maxX - minX
    xObs = rng.uniform(size=(nExp, nObs, dimX))
    xObs *= rangeX
    xObs += minX

    yObs = rng.normal(size=(nExp, nObs, 1))
    yObs *= sigvar

    return {'x': xObs,
            'y': yObs}


def make_domain_grid(domainBounds, domainRes):
    """takes domainBounds and domainRes for each dim of input space and grids
    accordingly"""
    #TODO: add sparse version with ndm

    domainBounds = npa(domainBounds)
    # get domain from bounds and res
    dimX = domainBounds.shape[0]
    if isscalar(domainRes):
        # equal res if scalar
        domainRes = repeat(domainRes, dimX)
    else: assert len(domainRes) == dimX
    domainRes = npa(domainRes)

    domain = npa([linspace(domainBounds[dim][0],
                           domainBounds[dim][1],
                           domainRes[dim])
                  for dim in xrange(dimX)])

    domain = cartesian(domain)
    return domain


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
    # pdb.set_trace()
    assert dimX0 == dimX
    kDomain = K_se(domain, domain, lenscale, sigvar)
    less_params_runner = lambda iexp: run_exp_i(iexp, xObs, yObs, domain, kDomain\
                                                lenscale, sigvar, noisevar)

    out = [run_exp_i(iexp, xObs, yObs, domain, kDomain, lenscale, sigvar, noisevar)
           for iexp in xrange(nExp)]
    # for iExp in xrange(nExp):
    #     if iExp % 100 == 0: print iExp
    #     xObs0 = prep_for_gpy(xObs[iExp], dimX)
    #     yObs0 = prep_for_gpy(yObs[iExp], 1)

    #     postmu = conditioned_mu(domain, xObs0, yObs0,\
    #                             lenscale, sigvar, noisevar)
    #     imax = postmu.argmax()
    #     out.append({'xmax': domain[imax],
    #                 'fmax': postmu[imax],
    #                 'imax': imax,
    #                 'lenscale': lenscale,
    #                 'xObs': xObs0,
    #                 'yObs': yObs0,
    #                 'iExp': iExp})
    return out


def run_exp_i(iExp, xObs, yObs, domain, kDomain,\
              lenscale, sigvar, noisevar):
    dimX = xObs.shape[-1]
    xObs0 = prep_for_gpy(xObs[iExp], dimX)
    yObs0 = prep_for_gpy(yObs[iExp], 1)

    postmu = conditioned_mu(domain, xObs0, yObs0,\
                            lenscale, sigvar, noisevar)
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
    out = {}
    for ii, iExp in enumerate(iExps):
        out[iExp] = {'dist': dists[ii],
                     'rank': ranks[ii],
                     'distType': distTypes[ii]}
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
    """v is a 1d array.  gives the average pair-wise l_n-norm distance between
    all elts in v"""
    assert type(v) is list or len(v.shape) == 1
    pairwise_dists = pdist(zip(v), p=n)
    return mean(pairwise_dists)


def prep_for_gpy(x, dimX):
    """def prep_for_gpy(x, dimX)

    ensures obs matrix x, with expected input dim dimX, is properly
    formatted to work with GPy"""

    # prep observations if 1d
    if dimX == 1:
        x = atleast_2d(x)
    assert len(x.shape)==2
    if x.shape[1] != dimX: x = x.T
    assert x.shape[1] == dimX
    return x


# def distsBtMaxWrtLenscale(domainBounds, xObs, yObs, lenscalepool,\
#                           domainRes=100, SIGVAR=1., NOISEVAR2=1e-7):
#     """returns how far maxes of a domain are given gps w lenscales in
#     lenscalepool and same obs xObs and yObs."""
#     dimX = len(domainBounds.shape)
#     # get domain from bounds and res
#     if isscalar(domainRes):
#         # equal res if scalar
#         domainRes = repeat(domainRes, dimX)
#     else: assert len(domainRes) == dimX

#     domain = npa([linspace(domainBounds[dim][0],
#                            domainBounds[dim][1],
#                            domainRes[dim])
#                   for dim in xrange(xDim)])

#     # prep observations if 1d
#     if dimX = 1:
#         xObs = atleast_2d(xObs)
#         yObs = atleast_2d(yObs)
#         if xObs.shape[1] != dimX: xObs = xObs.T
#         if yObs.shape[1] != 1: yObs = yObs.T

#     assert xObs.shape[1] == dimX
#     assert yObs.shape[1] == 1

#     kern = kern.RBF(input_dim=dimX,
#                     lengthscale=lenscale,
#                     variance=sigvar)

#     model = GPRegression(kern, xObs, yObs)
#     mupost = model.predict(domain)

#     return {'mu': mupost[0],
#             'var': mupost[1]}




    # conditioned_mus = [jbgp.conditioned_mu(X, xObs, yObs,
    #                                        lenscale, SIGVAR, NOISEVAR2)
    #                    for lenscale in lenscalepool]
    # imaxes = [mu.argmax() for mu in conditioned_mus]
    # xmaxes = [X[imax] for imax in imaxes]
    # ymaxes = [conditioned_mus[ils][imax] for ils, imax in enumerate(imaxes)]
    # mud_x = mu_lnnorm(xmaxes, 2)
    # mud_y = mu_lnnorm(ymaxes, 2)
    # mud_xXy = mud_x * mud_y

    # return {'xObs': xObs,
    #         'yObs': yObs,
    #         'ihat': imaxes,
    #         'xhat': xmaxes,
    #         'yhat': ymaxes,
    #         'mud_x': mud_x,
    #         'mud_y': mud_y,
    #         'mu_xXy': mu_xXy}


# def nsam_far(nsam, lenscalepool, ntries=10000):
#     ncond = len(lenscalepool)
#     # get valid x-y pairs to condition on
#     xylenscalemu = []
#     donesofar = 0
#     while donesofar < ntries:
#         good = False
#         xObs = rng.rand(nsam)
#         # assert that all yvals are positive (to assure max is not 0)
#         while not good:
#             yObs = rng.randn(nsam)
#             if yObs.max() > 0: good = True
#         # get the x-loc with best EV for all lss in lenscalepool
#         xylenscalemu.append(get_and_compare_mus(xObs, yObs, lenscalepool))
#         donesofar += 1

#     xylenscalemu = pd.DataFrame(xylenscalemu)  # convert to df
#     # rank how far the dists are
#     xylenscalemu['rank_mu_l2norm'] = rank(xylenscalemu.mu_l2norm.values)
#     xylenscalemu.set_index(xylenscalemu.rank_mu_l2norm, inplace=True)  # reindex
#     # top = xylenscalemu[xylenscalemu.rank_mu_l2norm < ntop]  # get max dists
#     return xylenscalemu


# def plot_nsam_far(df, lenscalepool, i):
#     """plot a test one"""
#     dfi = df.loc[i]
#     X = linspace(0, 1, 1028)
#     ncond = len(lenscalepool)
#     SIGVAR = 1.
#     NOISEVAR2 = 1e-7
#     conditioned_mus = [jbgp.conditioned_mu(X, dfi.xObs, dfi.yObs,
#                                             lenscale, SIGVAR, NOISEVAR2)
#                         for lenscale in lenscalepool]
#     [plt.plot(X, mu) for mu in conditioned_mus]
#     [plt.plot(dfi.xhat[i], dfi.yhat[i], 'ro', markersize=10, alpha=0.5)
#             for i in range(ncond)]
#     plt.plot(dfi.xObs, dfi.yObs, 'ko', markersize=8, alpha=0.4)
#     plt.show()

