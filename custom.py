# this file imports custom routes into the experiment server
from flask import Blueprint, render_template, request, jsonify, Response, abort, current_app
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
from numpy import linspace, array

# load the configuration options
config = PsiturkConfig()
config.load_config()
config.SECREY_KEY = 'my_secret_key'
myauth = PsiTurkAuthorization(config)  # if you want to add a password protect route use this

# explore the Blueprint
custom_code = Blueprint('custom_code', __name__, template_folder='templates', static_folder='static')

import gpExperiment as gpe

## LOAD GP STUFF INTO WORKSPACE
@custom_code.route('/init_experiment', methods=['GET'])
def init_experiment():
    if not request.args.has_key('condition'):
        raise ExperimentError('improper_inputs')  # i don't like returning HTML to JSON requests...  maybe should change this

    CONDITION = int(request.args['condition'])
    COUNTERBALANCE = int(request.args['counterbalance'])

    ## FREE VARS
    # experiment params
    NROUND = 200
    COST2SAMPLE = 5
    COST2DRILL = 30
    STARTPOINTS = 0
    # gp params
    nX = 1028
    X = linspace(0, 1, nX)
    SIGVAR = 1.
    NOISEVAR2 = 1e-7
    NROUND = 200
    NOBSPOOL = [2, 3, 4, 5, 6]
    ND2 = 4
    EDGEBUF = 0.05 # samples for 2sams wont be closer than EDGEBUF from screen edge
    D2POOL = [(1.-(EDGEBUF*2.))/(2.**(n+1)) for n in xrange(ND2)]
    # made with numpy.random.randint(4294967295, size=20)  # (number is max allowed on amazon linux)
    RNGSEEDPOOL =\
        array([1903799985, 1543581047, 1218602148,  764353219, 1906699770,
                951675775, 2101131205, 1792109879,  781776608, 2388543424,
            2154736893, 2773127409, 3304953852,  678883645, 3097437001,
            3696226994,  242457524,  991216532, 2747458246, 2432174005])
    LENSCALEPOWSOF2 = [2., 4., 6.]
    LENSCALEPOOL = [1./2.**n for n in LENSCALEPOWSOF2]
    ## END FREE VARS
    LENSCALE = LENSCALEPOOL[CONDITION]
    RNGSEED = RNGSEEDPOOL[COUNTERBALANCE]
    # LENSCALE = LENSCALEPOOL[CONDITION % len(LENSCALEPOOL)]
    # RNGSEED = RNGSEEDPOOL[CONDITION % len(RNGSEEDPOOL)]

    experParams = {'x': X,
                   'lenscale': LENSCALE,
                   'sigvar': SIGVAR,
                   'noisevar2': NOISEVAR2,
                   'rngseed': RNGSEED,
                   'nRound': NROUND,
                   'nObsPool': NOBSPOOL,
                   'd2Pool': D2POOL,
                   'edgeBuf': EDGEBUF}

    subParams = gpe.make_experiment(**experParams)
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
    resp['d2i'] = -1
    resp['nRound'] = NROUND
    resp['cost2sample'] = COST2SAMPLE
    resp['cost2drill'] = COST2DRILL
    resp['startPoints'] = STARTPOINTS

    return jsonify(**resp)


@custom_code.route('/get_nextTrial', methods=['GET'])
def get_nextTrial():
    # args:
    #   lenscale
    #   nObs
    #   d2locsX
    #   d2locsY
    args = request.args
    lenscale = float(args['lenscale'])
    nObs = float(args['nObs'])
    if nObs==2:
        d2locsX = args['d2locsX']
        d2locsY = args['d2locsY']
        d2locsX = loads(d2locsX)
        d2locsY = loads(d2locsY)
        d2locsX = map(float, d2locsX)
        d2locsY = map(float, d2locsY)
        d2locsX = array(d2locsX)
        d2locsY = array(d2locsY)
    else:
        d2locsX = None
        d2locsY = None

    nX = 1028
    X = linspace(0, 1, nX)
    SIGVAR = 1.
    NOISEVAR2 = 1e-7

    thisTri = gpe.make_trial(nObs, X, lenscale, SIGVAR, NOISEVAR2, d2locsX, d2locsY)

    resp = {'sample': thisTri['sample'].tolist(),
            'xObs': thisTri['xObs'].tolist(),
            'yObs': thisTri['yObs'].tolist()}

    return jsonify(**resp)


###########################################################
#  serving warm, fresh, & sweet custom, user-provided routes
#  add them here
###########################################################

#----------------------------------------------
# example custom route
#----------------------------------------------
@custom_code.route('/my_custom_view')
def my_custom_view():
        try:
                return render_template('custom.html')
        except TemplateNotFound:
                abort(404)


#  # set the secret key.  keep this really secret:
#  current_app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'
