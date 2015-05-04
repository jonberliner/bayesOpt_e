# this file imports custom routes into the experiment server
from flask import Blueprint, render_template, request, jsonify, Response, abort, current_app #, session
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

import bayesOptExperiment as boe
from jbutils import make_domain_grid, jsonToNpa, unpack_rngstate, pack_rngstate
from time import time
# with open('secretkey', 'r') as f: SECRETKEY = f.read().splitlines()[0]

## EXPERIMENT FREE VARS
NTRIAL = 200
COSTTODRILL = 30
INITSCORE = 0
# gp params
SIGVAR = 1.
NOISEVAR2 = 1e-7
NPASSIVEPOOL = [2, 3, 4, 5, 6]  # how many obs you start with
NACTIVEPOOL = [2, 3, 4, 5, 6]  # how many more samples subj takes before interrogation
# params for making sam3 queue
NTRIALTYPE = NACTIVEPOOL * NPASSIVEPOOL
assert NTRIAL % len(NTRIALTYPE) == 0  # assert equal amount of every trial type
LENSCALEPOWSOF2 = [2., 4., 6.]
LENSCALEPOOL = [1./2.**n for n in LENSCALEPOWSOF2]

DOMAINBOUNDS = [[0., 1.]]
DOMAINRES = 1028
DOMAIN = make_domain_grid(DOMAINBOUNDS, DOMAINRES).flatten()
EDGEBUF = 0.05 # samples for 2sams wont be closer than EDGEBUF from screen edge
# how close to domain edges passive observations can occur
XSAM_BOUNDS = [dim[:] for dim in DOMAINBOUNDS]  # deep copy of DOMAINBOUNDS
XSAM_BOUNDS[0][0] = EDGEBUF
XSAM_BOUNDS[0][1] -= EDGEBUF

NPERNOBS = NTRIAL / len(NOBSPOOL)
NTOTEST = NPERNOBS * 100
# made with numpy.random.randint(4294967295, size=20)  # (number is max allowed on amazon linux)
RNGSEEDPOOL =\
    npa([1903799985, 1543581047, 1218602148,  764353219, 1906699770,
         951675775, 2101131205, 1792109879,  781776608, 2388543424,
         2154736893, 2773127409, 3304953852,  678883645, 3097437001,
         3696226994,  242457524,  991216532, 2747458246, 2432174005])

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

    experParams = {
                   'nTrial': NTRIAL,
                   'nPassivePool': NPASSIVEPOOL,
                   'nActivePool': NACTIVEPOOL,
                   'rng': rng
                   }

    subParams = boe.make_experiment(**experParams)

    # bundle response to send
    resp = {}
    for f in subParams:
            try:
                resp[f] = subParams[f].tolist()
            except:
                resp[f] = subParams[f]

    for f in experParams:
        if f is not 'rng':
            try:  # convet numpy array to list if possible
                resp[f] = experParams[f].tolist()
            except:
                resp[f] = experParams[f]

    resp['itrial'] = -1
    resp['isam3'] = -1
    resp['nTrial'] = NTRIAL
    resp['costToDrill'] = COSTTODRILL
    resp['initscore'] = INITSCORE
    resp['lenscale'] = lenscale
    resp['sigvar'] = SIGVAR
    resp['distype'] = DISTTYPE
    resp['domainbounds'] = DOMAINBOUNDS
    resp['domainres'] = DOMAINRES
    resp['edgebuf'] = EDGEBUF

    resp['rngstate'] = pack_rngstate(rng.get_state())

    return jsonify(**resp)


@custom_code.route('/make_trial', methods=['POST'])
def make_trial():
    try:
        # t0 = time()
        # args:
        #   lenscale
        #   nObs
        #   xObs_sam3
        #   yObs_sam3
        #   rngstate

        params = request.json  # works when ajax request contentType specified as "applications/json"
        # unpack random number generator
        rng = RandomState()
        rngstate = unpack_rngstate(params['rngstate'])
        rng.set_state(rngstate)

        lenscale = float(params['lenscale'])
        nPassiveObs = int(params['nPassiveObs'])

        thisTri = boe.make_trial(nPassiveObs, DOMAIN, lenscale, SIGVAR, NOISEVAR2, XSAM_BOUNDS, rng)

        resp = {'sample': thisTri['sample'].tolist(),
                'xObs': thisTri['xObs'].flatten().tolist(),
                'yObs': thisTri['yObs'].tolist(),
                'iObs': thisTri['iObs'],
                'rngstate': pack_rngstate(rng.get_state())}

    except:
        raise ExperimentError('improper_inputs')  # i don't like returning HTML to JSON requests...  maybe should change this

    return jsonify(**resp)
