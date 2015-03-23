# for basic experiment setup
from numpy import linspace, fromstring
from numpy import array as npa
from numpy.random import RandomState
from generate_fardists import generate_fardists
from jbutils import make_domain_grid, jbpickle


# WILL MAKE FARDIST QUEUES FOR ALL RNGSEEDS IN RNGSEEDPOOL
# made with numpy.random.randint(4294967295, size=20)  # (number is max allowed on amazon linux)
## run the sucker
RNGSEEDPOOL =\
    npa([1903799985, 1543581047, 1218602148,  764353219, 1906699770,
         951675775, 2101131205, 1792109879,  781776608, 2388543424,
         2154736893, 2773127409, 3304953852,  678883645, 3097437001,
         3696226994,  242457524,  991216532, 2747458246, 2432174005])
# # for testing
# RNGSEEDPOOL = npa([1903799985])

# where to save the pickled results
DIR_SAM3 = 'static/sam3queues/'
FNAMETEMPLATE_SAM3 = 'sam3queue_rngseed_'


def prep_sam3_queues(rngseedpool, dir_sam3, fnameTemplate_sam3):
    ## EXPERIMENT FREE VARS
    NTRIAL = 200
    COST2DRILL = 30
    STARTPOINTS = 0
    # gp params
    SIGVAR = 1.
    NOISEVAR2 = 1e-7
    NOBSPOOL = [2, 3, 4, 5, 6]
    # params for making sam3 queue
    assert NTRIAL % len(NOBSPOOL) == 0
    LENSCALEPOWSOF2 = [2., 4., 6.]
    LENSCALEPOOL = [1./2.**n for n in LENSCALEPOWSOF2]
    # params for generating sam3 locs for far maxes for different lenscales
    DISTTYPE = 'x'  # must be in ['x', 'f', 'xXf']

    DOMAINBOUNDS = [[0., 1.]]
    DOMAINRES = 1028
    DOMAIN = make_domain_grid(DOMAINBOUNDS, DOMAINRES)
    EDGEBUF = 0.05 # samples for 2sams wont be closer than EDGEBUF from screen edge
    XSAM_BOUNDS = DOMAINBOUNDS
    XSAM_BOUNDS[0][0] = EDGEBUF
    XSAM_BOUNDS[0][1] -= EDGEBUF

    NPERNOBS = NTRIAL / len(NOBSPOOL)
    NTOTEST = NPERNOBS * 100

    nrngseed = len(rngseedpool)
    for irs, rngseed in enumerate(rngseedpool):
        print 'rngseed ' + str(irs+1) + ' of ' + str(nrngseed)
        rng = RandomState(rngseed)

        fname = ''.join([dir_sam3, fnameTemplate_sam3, str(rngseed), '.pkl'])

        experParams = {
                       'distType': DISTTYPE,
                       'nToKeep': NPERNOBS,
                       'nObs': 3,
                       'lenscalepool': LENSCALEPOOL,
                       'domain': DOMAIN,
                       'xSam_bounds': XSAM_BOUNDS,
                       'sigvar': SIGVAR,
                       'noisevar2': NOISEVAR2,
                       'nToTest': NTOTEST,
                       'rng': rng
                       }
        # generate fardists
        obs_sam3Queue = generate_fardists(**experParams)
        # save
        jbpickle(obs_sam3Queue, fname)


prep_sam3_queues(RNGSEEDPOOL, DIR_SAM3, FNAMETEMPLATE_SAM3)
