# this file imports custom routes into the experiment server
from flask import Blueprint, render_template, request, jsonify, Response, abort, current_app, session
from jinja2 import TemplateNotFound
from functools import wraps
from sqlalchemy import or_

from psiturk.psiturk_config import PsiturkConfig
from psiturk.experiment_errors import ExperimentError
from psiturk.user_utils import PsiTurkAuthorization, nocache

# # Database setup
from psiturk.db import db_session, init_db
from psiturk.models import Participant
from json import dumps, loads

# for basic experiment setup
from numpy import linspace, fromstring
from numpy import array as npa
from numpy.random import RandomState

# load the configuration options
config = PsiturkConfig()
config.load_config()
myauth = PsiTurkAuthorization(config)  # if you want to add a password protect route use this

# explore the Blueprint
custom_code = Blueprint('custom_code', __name__, template_folder='templates', static_folder='static')

import sam3experiment as s3e
from jbutils import make_domain_grid, jsonToNpa, unpack_rngstate, pack_rngstate

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
NTOTEST = NTRIAL * 100

DOMAINBOUNDS = [[0., 1.]]
DOMAINRES = 1028
DOMAIN = make_domain_grid(DOMAINBOUNDS, DOMAINRES)
EDGEBUF = 0.05 # samples for 2sams wont be closer than EDGEBUF from screen edge
XSAM_BOUNDS = DOMAINBOUNDS
XSAM_BOUNDS[0][0] = EDGEBUF
XSAM_BOUNDS[0][1] -= EDGEBUF

NPERNOBS = NTRIAL / len(NOBSPOOL)
# made with numpy.random.randint(4294967295, size=20)  # (number is max allowed on amazon linux)
RNGSEEDPOOL =\
    npa([1903799985, 1543581047, 1218602148,  764353219, 1906699770,
         951675775, 2101131205, 1792109879,  781776608, 2388543424,
         2154736893, 2773127409, 3304953852,  678883645, 3097437001,
         3696226994,  242457524,  991216532, 2747458246, 2432174005])

DIR_SAM3 = 'static/sam3queues/'
FNAMETEMPLATE_SAM3 = 'sam3queue_rngseed_'

## LOAD GP STUFF INTO WORKSPACE
@custom_code.route('/init_experiment', methods=['GET'])
def init_experiment():
    if not request.args.has_key('condition'):
        raise ExperimentError('improper_inputs')  # i don't like returning HTML to JSON requests...  maybe should change this

    condition = int(request.args['condition'])
    counterbalance = int(request.args['counterbalance'])

    ## END FREE VARS
    lenscale = LENSCALEPOOL[condition]
    rngseed = RNGSEEDPOOL[counterbalance]
    rng = RandomState(rngseed)

    experParams = {'domain': DOMAIN,
                   'xSam_bounds': XSAM_BOUNDS,
                   'sigvar': SIGVAR,
                   'noisevar2': NOISEVAR2,
                   'rng': rng,
                   'nTrial': NTRIAL,
                   'nObsPool': NOBSPOOL,
                   'edgeBuf': EDGEBUF,
                   'distType': DISTTYPE,
                   'lenscalepool': LENSCALEPOOL,
                   'nToTest': NTOTEST,
                   'dir_sam3': DIR_SAM3,
                   'fnameTemplate_sam3': FNAMETEMPLATE_SAM3,
                   'rngseed': rngseed}

    subParams = s3e.make_experiment(**experParams)
    # bundle response to send
    resp = {}
    for f in subParams:
        try:
            resp[f] = subParams[f].tolist()
        except:
            resp[f] = subParams[f]

    for f in experParams:
        try:  # convet numpy array to list if possible
            resp[f] = experParams[f].tolist()
        except:
            resp[f] = experParams[f]

    resp['round'] = -1
    resp['i_sam3'] = -1
    resp['nTrial'] = NTRIAL
    resp['cost2sample'] = COST2SAMPLE
    resp['cost2drill'] = COST2DRILL
    resp['startPoints'] = STARTPOINTS
    resp['lenscale'] = lenscale

    session['rngstate'] = pack_rngstate(rng.get_state())

    return jsonify(**resp)


@custom_code.route('/get_nextTrial', methods=['GET'])
def get_nextTrial():
    # args:
    #   lenscale
    #   nObs
    #   x_sam3
    #   y_sam3

    # load random number generator
    assert 'rngstate' in session
    rng = RandomState()
    rng.set_state(unpack_rngstate([session['rgnstate']]))


    args = request.args
    lenscale = float(args['lenscale'])
    nObs = float(args['nObs'])
    if nObs==3:  # json to nparray
        x_sam3 = jsonToNpa(args['x_sam3'], float)
        y_sam3 = jsonToNpa(args['y_sam3'], float)
    else:
        x_sam3 = None
        y_sam3 = None

    thisTri = s3e.make_trial(nObs, DOMAIN, lenscale, SIGVAR, NOISEVAR2,\
                             XSAM_BOUNDS, x_sam3, y_sam3, rng)

    # save random number generator for next call
    session['rngstate'] = pack_rngstate(rng.get_state())

    resp = {'sample': thisTri['sample'].tolist(),
            'xObs': thisTri['xObs'].tolist(),
            'yObs': thisTri['yObs'].tolist()}

    return jsonify(**resp)


#  # set the secret key.  keep this really secret:
custom_code.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'
