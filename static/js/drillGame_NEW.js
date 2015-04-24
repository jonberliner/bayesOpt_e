/********************
*    DRILL GAME             *
********************/
var drillGame = function(){
    "use strict";
    var canvas = document.getElementById('easel');
    var WCANVAS = canvas.width;
    var HCANVAS = canvas.height;
    var YGROUNDLINE = HCANVAS - HCANVAS*0.9;
    var GROUNDLINE2BOTTOM = HCANVAS - YGROUNDLINE;

    var stage = new createjs.Stage(canvas);  // objects will go on stage

    var CHECKMOUSEFREQ = 10;  // check for mouseover CHECKMOUSEFREQ times per sec
    stage.enableMouseOver(CHECKMOUSEFREQ);

    // var MSTICK = 100;  // run checkOnTick every MSTICK ms
    // createjs.Ticker.setInterval(MSTICK);
    // createjs.Ticker.addEventListener("tick", function(event){
    //     checkOnTick(event, tp, wp, EP, STYLE.startPoint.sp.radius);
    // });

    //////// INITIATE GAME
    var EP = {};  // params that stay constant through experiment
    var tp = {};  // params that change trial by trial
    var wp = {};  // params that can change within a trial
    var tsub = {}; // trial responses from subject that change trial by trial
    // containers that make up easeljs objects - objects are for easily
    // accessing shapes by name
    var background, choiceSet, msgs;
    var a_background, a_startPoint, a_choiceSet; // arrays for ordered staging
    var obs_arrays;
    var QUEUES = {};  // queues containing trial params for each trial of experiment
    get_customRoute('init_experiment',  // call init_experiment in custom.py...
                {'condition': condition,  // w params condition adn counter...
                 'counterbalance': counterbalance},
                 function(resp){  // once to get back resp from custom.py...
                    EP.RNGSEED = resp['rngseed'];
                    EP.INITSCORE = resp['initscore'];
                    EP.MINDOMAIN = resp['domainbounds'][0];
                    EP.MAXDOMAIN = resp['domainbounds'][1];
                    EP.BOUNDSX = [EP.MINDOMAIN, EP.MAXDOMAIN];
                    EP.BOUNDSPX = [0, WCANVAS];
                    EP.NTRIAL = resp['ntrial'];
                    EP.LENSCALE = resp['lenscale'];
                    EP.SIGVAR = resp['sigvar'];
                    EP.MINY = EP.SIGVAR * 3.;
                    EP.MAXY = EP.SIGVAR * -3.;
                    EP.BOUNDSY = [EP.MINY, EP.MAXY];
                    EP.BOUNDSPY = [YGROUNDLINE, HCANVAS];
                    EP.NOISEVAR2 = resp['noisevar2'];
                    EP.EDGEBUF = resp['edgebuf'];
                    EP.DISTTYPE = resp['disttype'];
                    EP.COST2DRILL = resp['cost2drill'];
                    EP.DOMAINRES = resp['domainres'];

                    QUEUES.XOBS_SAM3 = resp['xObs_sam3Queue'];
                    QUEUES.YOBS_SAM3 = resp['yObs_sam3Queue'];
                    QUEUES.NOBS = resp['nObsQueue'];

                    tp.itrial = resp['inititrial'];
                    tp.isam3 = resp['isam3'];
                    tp.rngstate = resp['rngstate'];
                    // tp.rngstate0 = resp['rngstate0'];
                    // tp.rngstate1 = resp['rngstate1'];
                    // tp.rngstate2 = resp['rngstate2'];
                    // tp.rngstate3 = resp['rngstate3'];


                    tp = set_itrialParams(tp.itrial, tp, QUEUES);
                    tsub.totalScore = EP.INITSCORE;

                    obs_arrays = [];  // for all observations
                    obs_arrays.passive = [];
                    obs_arrays.active = [];
                    obs_arrays.drill = [];

                    background = make_background(STYLE.background, WCANVAS, HCANVAS, YGROUNDLINE);
                    a_background = [background.background];
                    choiceSet = make_choiceSet(STYLE.choiceSet, WCANVAS, YGROUNDLINE);
                    a_choiceSet = [choiceSet.arc_glow, choiceSet.arc];
                    msgs = make_messages(STYLE.msgs);

                    update_totalScore(tsub.totalScore);
                    msgs.totalScore.visible = true; // visible through whole game

                    stageArray(a_background);
                    stageArray(a_choiceSet);
                    stageObject(msgs, false);
                    msgs.totalScore.visible = true;  // totalScore always visible


                    // let's get it started!
                    setup_nextTrial();
                }  // end callback
    );  // end init_experiment


    //////// GAME LOGIC (besides createjs shape event handlers)
    //// setups for various parts of a trial
    function setup_makeChoice(){
        // what happens when we move to 'makeChoice' section of a trial
        wp.trialSection = 'makeChoice';
        // fb only shown during reach in this condition

        // update objects
        choiceSet.groundline_glow.visible = false;
        choiceSet.groundline.visible = true;

        // update messages
        msgs.trialFeedback.visible = false;
        msgs.makeChoice.visible = true;

        stage.update();
        wp.tChoiceStarted = getTime();  // start choice timer
    }


    function update_msg_trialFeedback(msg, trialGross, cost2drill){
        var trialNet = trialGross - cost2drill;
        msg.text = '        ' +
                                 monify(trialGross) +
                                 ' earned drilling\n \n' +
                                '      - ' +
                                monify(cost2drill) +
                                ' spent drilling\n \n' +
                                '__________________\n \n     '+
                                monify(trialNet) +
                                ' earned this round';
    }


    function setup_showFeedback(){
        wp.trialSection = 'showFeedback';
        wp.tFeedbackOn = getTime();

        // update messages
        msgs.makeChoice.visible = false;

        msgs.trialFeedback = make_msg_trialFeeback(tp, tsub)
        // show feedback
        unstageArray(fb_array);
        if(EP.FEEDBACKTYPE==='aboveStartPoint'){
            fb_array = make_aboveStartPoint_scalar_array(tp.pxStart, tp.pyStart,
                                                         tp.pradArc, tp.degFB,
                                                         EP.PERCENTBETWEENSPANDARC,
                                                         EP.SDPERCENTRADWIGGLEFB,
                                                         EP.SDPERCENTDEGWIGGLEFB,
                                                         EP.RANGEDEG);
        }
        else if(EP.FEEDBACKTYPE==='clickLocation'){
            // show scores from last NLASTTOSHOW trials
            fb_array = make_clickloc_scalar_array(drill_history, tp.mindegArc,
                        function(elt){return nlast(elt, tp.itrial, EP.NLASTTOSHOW)},
                        STYLE.scalar_obs);
        }
        stageArray(fb_array);
        stage.update();
    }


    //// functions for setting up a trial
    function setup_nextTrial(){
        // increment tp.itrial and setup the next trial
        tp.itrial += 1;
        console.log('itrial ' + tp.itrial.toString());
        setup_trial(tp.itrial, tp, QUEUES, STYLE.choiceSet);
    }


    function setup_trial(itrial, tp, queues, stylecs){
        // set up things for trial itrial
        tp = set_itrialParams(itrial, tp, queues);
        // remove obs from stage and empty obs arrays
        for(var obstype in obs_arrays){
            unstageArray(obs_arrays[obstype]);
            obs_arrays[obstype] = [];
        }
        // add new starting observations
        for (var iobs=0; iobs<tp.nObs; iobs++){
            add_obs(obs_arrays.passive, tp.pxObs[iobs], tp.pyObs, STYLE.obs.passive);
        }
        stageArray(obs_arrays.passive);

        setup_makeChoice();
    }


    function set_itrialParams(itrial, tp, queues){
        // extract trial params for itrial itrial from the queues in queues
        // var tp = {};  // init trial params

        // see if this is a sam3 trial
        tp.nObs = queues.NOBS[itrial];
        if(tp.nObs===3){
            tp.xObs = queues.XOBS_SAM3[tp.isam3]
            tp.yObs = queues.YOBS_SAM3[tp.isam3]
            tp.isam3 += 1;
        }
        else {
            tp.xObs_sam3 = 'None';
            tp.yObs_sam3 = 'None';
        }
        // generate hidden function and obs server side
        post_customRoute('make_trial',
                    {'lenscale': EP.LENSCALE,
                     'nObs': tp.nObs,
                     'xObs_sam3': tp.xObs,
                     'yObs_sam3': tp.yObs,
                     'rngstate': tp.rngstate
                     // 'rngstate0': tp.rngstate0,
                     // 'rngstate1': tp.rngstate1,
                     // 'rngstate2': tp.rngstate2,
                     // 'rngstate3': tp.rngstate3
                     },
                    function(resp){
                        console.log(resp);
                        tp.yHidfcn = resp['sample'];
                        tp.xObs = resp['xObs'];
                        tp.yObs = resp['yObs'];
                        tp.pyHidfcn = normalize(tp.yHidfcn, EP.BOUNDSPY, EP.BOUNDSY);
                        tp.pxObs = normalize(tp.xObs, EP.BOUNDSPX, EP.BOUNDSX);
                        tp.pyObs = normalize(tp.yObs, EP.BOUNDSPY, EP.BOUNDSY);
                    });

        tp.itrial = itrial;

        return tp;
    }


    function scale(array, frommusd, tomusd){
        array.map(function(elt){

        })
    }

    function yToPy(array){

    }


    function update_choiceSet(pxStart, pyStart, pradArc,
                              minthetaArc, maxthetaArc, stylecs){
        // update the graphics of choiceSet wrt incoming args
        // negatives come from >0 being down screen.  huge PITA
        choiceSet.arc.graphics.clear();
        choiceSet.arc_glow.graphics.clear();
        choiceSet.arc.graphics.s(stylecs.arc.strokeColor).
                               ss(stylecs.arc.strokeSize, 0, 0).
                               arc(pxStart, pyStart, pradArc,
                                   -minthetaArc, -maxthetaArc, true);

        var arc_glow_size = stylecs.arc.strokeSize *
                            stylecs.arc_glow.ratioGlowBigger;
                        stylecs.arc_glow.ratioGlowBigger;
        choiceSet.arc_glow.graphics.s(stylecs.arc_glow.strokeColor).
                                ss(arc_glow_size, 0, 0).
                                arc(pxStart, pyStart, pradArc,
                                    -minthetaArc, -maxthetaArc, true);
    }


    //// functions for saving and tearing down a trial
    function add_obs(px, py, array, style){
        // adds obs as loc (px,py) to array array with style style
        var obs = make_obs(px, py, style);
        array.push(obs);
    }


    function choice_made(px, py){
        // what happens after a choice is made
        console.log('choice_made called');
        tsub.choiceRT = getTime() - wp.tChoiceStarted;
        tsub.pxDrill = pxDrill;
        tsub.pyDrill = pyDrill;
        tsub.xDrill = normalize(pxDrill, EP.BOUNDSPX, EP.BOUNDSX);
        tsub.yDrill = normalize(pyDrill, EP.pYBOUNDS, EP.BOUNDSY);
        tsub.trialScore = yToScore(pyDrill); // get the reward

        add_obs(pxDrill, pyDrill, drill_array, STYLE.drillObs);

        tsub.totalScore += tsub.trialScore;
        update_totalScore(tsub.totalScore);

        store_thisTrial(setup_showFeedback);
    }


    function make_obs(px, py, style){
        var obs = new createjs.Shape();
        obs.graphics.s(style.strokeColor).
                     ss(style.strokeSize).
                     f(style.fillColor).
                     dc(px, py, style.radius);
        return obs;
    }


    function update_totalScore(totalScore){
        msgs.totalScore.text = 'score: ' + totalScore.toString();
    }


    function store_thisTrial(callback){
        // store things from this trial and then run callback
        drill_history.push({'px': tsub.pxDrill,
                            'py': tsub.pyDrill,
                            'degDrill': tsub.degDrill,
                            'mindegArc': tp.mindegArc,
                            'f': tsub.trialScore,
                            'itrial': tp.itrial});
        jsb_recordTurkData([EP, tp, tsub], callback);
    }


    //////// GAME OBJECTS AND OBJECT CONSTRUCTORS
    function make_messages(stylemsgs){
        var msgs = {};
        for(var msg in stylemsgs){
                msgs[msg] = new createjs.Text();
            for(var prop in stylemsgs[msg]){
                msgs[msg][prop] = stylemsgs[msg][prop]
            }
        }
        return msgs;
    }


    function make_background(stylebg, canvasW, canvasH, yGroundline){
        var background_objs = [];
        var ground = new createjs.Shape();
        var groundline2bottom = canvasH - yGroundline;

        ground.graphics.s(stylebg.ground.STROKECOLOR).
                    f(stylebg.ground.FILLCOLOR).
                    ss(stylebg.ground.STROKESIZE, 0, 0).
                    r(0, yGroundline, canvasW, groundline2bottom);
        ground.visible = true;

        // sky Graphics
        var sky = new createjs.Shape();
        sky.graphics.s(stylebg.sky.STROKECOLOR).
                        f(stylebg.sky.FILLCOLOR).
                        ss(stylebg.sky.STROKESIZE, 0, 0).
                        r(0, 0, canvasW, yGroundline);
        sky.visible = true;


        // add to background array
        background_objs.background = background;

        return background_objs;
    }


    function make_choiceSet(stylecs, canvasW, yGroundline){
        var choiceSet = {};

        var groundline = new createjs.Shape();
        var groundline_glow = new createjs.Shape();

        // groundline Style
        var groundline = new createjs.Shape();
        groundline.graphics.s(stylecs.groundline.strokeColor).
                            ss(stylecs.groundline.strokeSize, 0, 0).
                            mt(0, yGroundline). // GROUNDLINE HEIGHT
                            lt(canvasW, yGroundline);
        groundline.visible = true;

        var groundline_glow = new createjs.Shape();
        groundline_glow.graphics.s(stylecs.groundline_glow.strokeColor).
                            ss(stylecs.groundline_glow.strokeSize, 0, 0).
                            mt(0, yGroundline). // GROUNDLINE HEIGHT
                            lt(canvasW, yGroundline);
        groundline_glow.visible = false;


        // groundline Actions
        groundline.addEventListener('mouseover', function(){
            if(wp.trialSection==='makeChoice'){
                groundline_glow.visible = true;
                stage.update();
            }

        });

        groundline.addEventListener('mouseout', function(){
            if(wp.trialSection==='makeChoice'){
                groundline_glow.visible = false;
                stage.update();
            }
        });

        groundline.addEventListener('click', function(){
            if(wp.trialSection==='makeChoice'){
                var pxDrill = stage.mouseX;
                var pyDrill = stage.mouseY;
                choice_made(pxDrill, pyDrill);
            }
        });

        choiceSet.groundline = groundline;
        choiceSet.groundline_glow = groundline_glow;
        return choiceSet;
    }


    ////////////  HELPERS  ////////////
    function pToDegDrill(pxDrill, pyDrill, pxStart, pyStart){
        // ALWAYS ASSUMES mindegArc IS 0!!!!!
        // * pyDrill-pyStart is negative b.c. >y is lower in pixel space
        var theta = Math.atan2(-(pyDrill-pyStart), pxDrill-pxStart);
        var deg = mod(radToDeg(theta), 360.);
        return deg;
    }

    function degDrillToP(degDrill, prad, pxStart, pyStart){
        // ALWAYS ASSUMES mindegArc IS 0!!!!!
        var theta = degToRad(degDrill);
        var px = prad * Math.cos(theta);
        var py = - (prad * Math.sin(theta));  // negative b.c of reflection in pixel space
        px += pxStart;
        py += pyStart;
        return {'x': px, 'y': py};
    }


    function get_signederror(degDrill, degOpt, mindegArc){
        var ccwerr = degDrill - mod(degOpt + mindegArc, 360.);  // e.g. 270-0 = 270
        var cwerr = degDrill-360. - mod(degOpt + mindegArc, 360.);  // e.g. -90-0 = -90 (correct)
        var signederror = Math.abs(ccwerr) < Math.abs(cwerr) ? ccwerr : cwerr;
        return signederror;
    }


//// HELPER FUNCTIONS
    function nlast(elt, currtrial, n) {
        // says yes if this elt's trial was one of the n last trials
        var good = currtrial - elt.itrial < n;
        return good;
    }


    function stageArray(shapeArray, visible){
        // add all elements in shapeArray to the canvas
        visible = typeof visible !== 'undefined' ? visible : true;
        shapeArray.map(function(elt){
            stage.addChild(elt);
            elt.visible = visible;
        });
        stage.update();
    }


    function stageObject(object, visible){
        // add all fields of object to the canvas
        visible = typeof visible !== 'undefined' ? visible : true;
        for (var field in object){
            stage.addChild(object[field]);
            object[field].visible = visible;
        }
        stage.update();
    }


    function unstageArray(shapeArray){
        // remove all elements in shapeArray from the canvas
        shapeArray.map(function(elt){
            elt.visible = false;
            stage.removeChild(elt);
        });
    }


    function unstageObject(object){
        // remove all fields of object from the canvas
        for (var field in object){
            object[field].visible = true;
            stage.removeChild(object[field]);
        }
        stage.update();
    }


    function errorToScore(unsignederror, degrange) {
        return Math.round((1 - (unsignederror/degrange)) * 100);
    }


    function endExp(){
        psiTurk.showPage('debriefing.html');
    }


    function monify(n){
        n = Math.round(n);
        if (n<0){
            return '-$' + (-n).toString();
        }
        else{
            return '$' + n.toString();
        }
    }


    function max(array) {
        return Math.max.apply(Math, array);
    }


    function min(array) {
        return Math.min.apply(Math, array);
    }


    function getTime(){
        return new Date().getTime();
    }


    function mean(array){
        var N = array.length;
        var sum = 0.;
        for(var i=0; i<N; i++){
            sum += array[i];
        }
        return sum / N;
    }


    function std(array){
        var N = array.length;
        var sig2 = 0.;
        var mu = mean(array);
        for(var i=0; i<N; i++){
            sig2 += Math.pow(array[i]-mu, 2.);
        }
        sig2 *= 1./N;
        return sig2;
    }

    function normalize(a, tobounds, frombounds){
        // takes aa, which lives in interval frombounds, and maps to interval tobounds
        // default tobounds = [0,1]
        tobounds = typeof tobounds !== 'undefined' ? tobounds : [0., 1.];
        // default frombounds are the min and max of a
        frombounds = typeof frombounds !== 'undefined' ? frombounds : [min(a), max(a)];

        var fromlo = frombounds[0];
        var fromhi = frombounds[1];
        var tolo = tobounds[0];
        var tohi = tobounds[1];
        var fromrange = fromhi-fromlo;
        var torange = tohi-tolo;

        a = a.map(function(elt){return elt-fromlo;});
        a = a.map(function(elt){return elt/fromrange;}); // now in 0, 1
        a = a.map(function(elt){return elt*torange});
        a = a.map(function(elt){return elt+tolo});

        return a;
    }


    function rescale(a, tomusd, frommusd){
        // takes aa, which lives in interval frombounds, and maps to interval tobounds
        // default tobounds = [0,1]
        tomusd = typeof tomusd !== 'undefined' ? tomusd : [0., 1.];
        // default frombounds are the min and max of a
        frommusd = typeof frommusd !== 'undefined' ? frommusd : [min(a), max(a)];

        var fromlo = frombounds[0];
        var fromhi = frombounds[1];
        var tolo = tobounds[0];
        var tohi = tobounds[1];
        var fromrange = fromhi-fromlo;
        var torange = tohi-tolo;

        a = a.map(function(elt){return elt-fromlo;});
        a = a.map(function(elt){return elt/fromrange;}); // now in 0, 1
        a = a.map(function(elt){return elt*torange});
        a = a.map(function(elt){return elt+tolo});

        return a;
    }


    function get_dist(p1, p2){
        return Math.sqrt(Math.pow(p1[0]-p2[0], 2.) +
                         Math.pow(p1[1]-p2[1], 2.));
    }

    function withinRad(x, y, xOrigin, yOrigin, rad){
        return get_dist([x, y], [xOrigin, yOrigin]) < rad;
    }


    function radToDeg(theta){
        return mod(theta * (180./Math.PI), 360.);
    }


    function degToRad(deg){
        return mod(deg, 360.) * (Math.PI/180.);
    }


    // use instead of % b.c. javascript can't do negative mod
    function mod(a, b){return ((a%b)+b)%b;}


    function rand(min, max){
        min = typeof min !== 'undefined' ? min : 0;
        max = typeof max !== 'undefined' ? max : 1;

        var range = max - min;
        return Math.random() * range + min;
    }

    function randn(mu, sd){
        // generate gaussian rand fcns using box-mueller method
        mu = typeof mu !== 'undefined' ? mu : 0;
        sd = typeof sd !== 'undefined' ? sd : 1;

        var x1, x2;
        var w = 99.;
        while(w >= 1.){
            x1 = 2. * rand() - 1.;
            x2 = 2 * rand() - 1;
            w = x1*x1 + x2*x2;
        }
        return mu + (x1 * w * sd);
    }


    function keys(obj, sorted){
        // gets object keys
        sorted = typeof tobounds !== 'undefined' ? tobounds : true; // default sorted
        var keys = [];
        for(var key in obj){
            if(obj.hasOwnProperty(key)){
                keys.push(key);
            }
        }
        return keys;
    }


    function objToArray(obj){
        return keys(obj).map(function(k){return obj[k]});
    }


    function jsb_recordTurkData(loObj, callback){
        var toSave = {};
        loObj.map(function(obj){  // for every obj in loObj...
            for(var field in obj){
                toSave[field] = obj[field];  // add to dict toSave
            }
        });

        psiTurk.recordTrialData(toSave);  // store on client side
        psiTurk.saveData();  // save to server side
        callback();
    }


    //////// STYLE SHEETS FOR THE GAME
    var STYLE = [];

    // background.  should be purely cosmetic
    STYLE.background = [];

    STYLE.background.sky = [];
    STYLE.background.sky.strokeSize = 5;
    STYLE.background.sky.strokeColor = '#33CCCC';
    STYLE.background.sky.fillColor = '#33CCCC';

    STYLE.background.ground = [];
    STYLE.background.ground.strokeSize = 5;
    STYLE.background.ground.strokeColor = '#A0522D';
    STYLE.background.ground.fillColor = '#A0522D';

    // choiceSet is the abstract term for whatever objects you can click to make
    // a choice.  in this case, we have a single arc, but can be arbitrary
    STYLE.choiceSet = [];
    STYLE.choiceSet.groundline = [];
    STYLE.choiceSet.groundline.strokeColor = '#8B8B8B';
    STYLE.choiceSet.groundline.fillColor = null;
    STYLE.choiceSet.groundline.strokeSize = 10;

    STYLE.choiceSet.groundline_glow = [];
    STYLE.choiceSet.groundline_glow.strokeColor = '#AEAEAE';
    STYLE.choiceSet.groundline_glow.ratioGlowBigger = 1.5;

    // feedback objects
    STYLE.obs = [];
    STYLE.obs.drill = [];
    STYLE.obs.drill.strokeColor = 'red';
    STYLE.obs.drill.fillColor = null;
    STYLE.obs.drill.strokeSize = 4;
    STYLE.obs.drill.radius = 12;

    STYLE.obs.passive = [];
    STYLE.obs.passive.strokeColor = '#8B8B8B';
    STYLE.obs.passive.fillColor = '#8B8B8B';
    STYLE.obs.passive.strokeSize = 2;
    STYLE.obs.passive.radius = 20;

    STYLE.obs.active = [];
    for(var key in STYLE.obs.passive){
        STYLE.obs.active[key] = STYLE.obs.passive[key];
    }

    // messages shown throughout game
    STYLE.msgs = [];

    STYLE.msgs.goToStart = [];
    STYLE.msgs.goToStart.text = 'GO TO START';
    STYLE.msgs.goToStart.color = '#AEAEAE';
    STYLE.msgs.goToStart.font = '2em Helvetica';
    STYLE.msgs.goToStart.textAlign = 'center';
    STYLE.msgs.goToStart.x = WCANVAS / 2.;
    STYLE.msgs.goToStart.y = HCANVAS / 20.;

    STYLE.msgs.makeChoice = [];
    STYLE.msgs.makeChoice.text = 'CLICK RING TO MAKE CHOICE';
    STYLE.msgs.makeChoice.color = '#AEAEAE';
    STYLE.msgs.makeChoice.font = '2em Helvetica';
    STYLE.msgs.makeChoice.textAlign = 'center';
    STYLE.msgs.makeChoice.x = WCANVAS / 2.;
    STYLE.msgs.makeChoice.y = HCANVAS / 20.;

    STYLE.msgs.tooSlow = [];
    STYLE.msgs.tooSlow.text = 'TOO SLOW';
    STYLE.msgs.tooSlow.color = '#AEAEAE';
    STYLE.msgs.tooSlow.font = '10em Helvetica';

    STYLE.msgs.totalScore = [];
    STYLE.msgs.totalScore.color = '#AEAEAE';
    STYLE.msgs.totalScore.font = '2em Helvetica';
    STYLE.msgs.totalScore.regX = 0.;
    STYLE.msgs.totalScore.regY = 0.;
    STYLE.msgs.totalScore.textAlign = 'left';
    STYLE.msgs.totalScore.x = 10.;
    STYLE.msgs.totalScore.y = HCANVAS - 40.;

    STYLE.msgs.trialFeedback = [];
    STYLE.msgs.trialFeedback.x = WCANVAS/2.;
    STYLE.msgs.trialFeedback.y = HCANVAS/2.;
    STYLE.msgs.trialFeedback.color = '#AEAEAE';
    STYLE.msgs.trialFeedback.font = '2em Helvetica';
    STYLE.msgs.trialFeedback.textAlign = 'center';
    STYLE.msgs.trialFeedback.visible = false;

};
