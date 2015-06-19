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


    //////// STYLE SHEETS FOR THE GAME
    var STYLE = {};

    // background.  should be purely cosmetic
    STYLE.background = {};

    STYLE.background.sky = {};
    STYLE.background.sky.strokeSize = 5;
    STYLE.background.sky.strokeColor = '#33CCCC';
    STYLE.background.sky.fillColor = '#33CCCC';

    STYLE.background.ground = {};
    STYLE.background.ground.strokeSize = 5;
    STYLE.background.ground.strokeColor = '#A0522D';
    STYLE.background.ground.fillColor = '#A0522D';

    // choiceSet is the abstract term for whatever objects you can click to make
    // a choice.  in this case, we have a single arc, but can be arbitrary
    STYLE.choiceSet = {};
    STYLE.choiceSet.groundline = {};
    STYLE.choiceSet.groundline.strokeColor = '#D9BAAB';
    STYLE.choiceSet.groundline.fillColor = null;
    STYLE.choiceSet.groundline.strokeSize = 10;

    STYLE.choiceSet.groundline_glow = {};
    STYLE.choiceSet.groundline_glow.strokeColor = '#EACDDC';
    STYLE.choiceSet.groundline_glow.ratioGlowBigger = 2.;

    STYLE.hidfcn = {};
    STYLE.hidfcn.fillColor = null;
    STYLE.hidfcn.strokeColor = 'black';
    STYLE.hidfcn.strokeSize = 3;

    STYLE.ulbutton = {}
    STYLE.ulbutton.ulbutton = {};
    STYLE.ulbutton.ulbutton.strokeColor = 'gray';
    STYLE.ulbutton.ulbutton.fillColor = 'blue';
    STYLE.ulbutton.ulbutton.strokeSize = 5;
    STYLE.ulbutton.ulbutton.radius = 30;
    STYLE.ulbutton.ulbutton.x = STYLE.ulbutton.ulbutton.radius + 10;
    STYLE.ulbutton.ulbutton.y = YGROUNDLINE / 2. - 4;

    STYLE.ulbutton.ulbutton_glow = {};
    STYLE.ulbutton.ulbutton_glow.strokeColor = 'green';
    STYLE.ulbutton.ulbutton_glow.fillColor = 'green';
    STYLE.ulbutton.ulbutton_glow.radius = 30;
    STYLE.ulbutton.ulbutton_glow.ratioGlowBigger = 3;
    STYLE.ulbutton.ulbutton_glow.x = STYLE.ulbutton.ulbutton.x;
    STYLE.ulbutton.ulbutton_glow.y = STYLE.ulbutton.ulbutton.y;

    // feedback objects
    STYLE.obs = {};
    // STYLE.obs.drill = {};
    // STYLE.obs.drill.strokeColor = 'red';
    // STYLE.obs.drill.fillColor = null;
    // STYLE.obs.drill.strokeSize = 4;
    // STYLE.obs.drill.radius = 12;

    STYLE.obs.best = {};
    STYLE.obs.best.strokeColor = 'red';
    STYLE.obs.best.fillColor = null;
    STYLE.obs.best.strokeSize = 6;
    STYLE.obs.best.radius = 16;

    STYLE.obs.passive = {};
    STYLE.obs.passive.strokeColor = 'white';
    STYLE.obs.passive.fillColor = null;
    STYLE.obs.passive.strokeSize = 3;
    STYLE.obs.passive.radius = 8;

    STYLE.obs.active = {};
    for(var key in STYLE.obs.passive){
        STYLE.obs.active[key] = STYLE.obs.passive[key];
    }

//     TODO: figure out oop.  it's about freaking time
//     // messages shown throughout game
//     function message(){
//         this.style = {};
//         this.style.color = 'black';
//         this.style.font = '2em Helvetica';
//         this.style.textAlign = 'center';
//         this.style.x = 0;
//         this.style.y = 0;
//         this.shape =
//         for(var field in style){

//         }
//     }
//     message.prototype.update(text){
//         this.
//     }

    STYLE.msgs = {};


    STYLE.msgs.makeChoice = {};
    STYLE.msgs.makeChoice.text = 'click ground line to sample';
    STYLE.msgs.makeChoice.color = '#666';
    STYLE.msgs.makeChoice.font = '1.4em Helvetica';
    STYLE.msgs.makeChoice.textAlign = 'center';
    STYLE.msgs.makeChoice.x = WCANVAS / 2.;
    STYLE.msgs.makeChoice.y = YGROUNDLINE / 3.;

    STYLE.msgs.clickulbutton = {};
    STYLE.msgs.clickulbutton.text = 'click ignition button to move to next area';
    STYLE.msgs.clickulbutton.color = '#666';
    STYLE.msgs.clickulbutton.font = '1.4em Helvetica';
    STYLE.msgs.clickulbutton.textAlign = 'center';
    STYLE.msgs.clickulbutton.x = WCANVAS / 2.;
    STYLE.msgs.clickulbutton.y = YGROUNDLINE / 3.;

    STYLE.msgs.expSummary = {};
    STYLE.msgs.expSummary.text = 'click ignition button to move to next area';
    STYLE.msgs.expSummary.color = '#666';
    STYLE.msgs.expSummary.font = '1.4em Helvetica';
    STYLE.msgs.expSummary.textAlign = 'center';
    STYLE.msgs.expSummary.x = WCANVAS / 2.;
    STYLE.msgs.expSummary.y = YGROUNDLINE / 3.;

    STYLE.msgs.totalScore = {};
    STYLE.msgs.totalScore.color = '#666';
    STYLE.msgs.totalScore.font = '2em Helvetica';
    STYLE.msgs.totalScore.regX = 0.;
    STYLE.msgs.totalScore.regY = 0.;
    STYLE.msgs.totalScore.textAlign = 'right';
    STYLE.msgs.totalScore.x = WCANVAS - 10.;
    STYLE.msgs.totalScore.y = YGROUNDLINE / 4.;

    STYLE.msgs.trialFeedback = {};
    STYLE.msgs.trialFeedback.x = WCANVAS/2.;
    function percentGROUNDLINE2BOTTOM_to_py(percent){
        assert(percent >= 0 && percent <= 1, 'percent must be between 0 and 1');
        return (percent * GROUNDLINE2BOTTOM) + YGROUNDLINE;
    }
    STYLE.msgs.trialFeedback.y = percentGROUNDLINE2BOTTOM_to_py(0.4) ;
    STYLE.msgs.trialFeedback.color = '#DEDEDE';
    STYLE.msgs.trialFeedback.font = 'bold 2em Helvetica';
    STYLE.msgs.trialFeedback.textAlign = 'center';
    STYLE.msgs.trialFeedback.visible = false;

    STYLE.msgs.trialFeedback_outline = {};
    for(var field in STYLE.msgs.trialFeedback){
        STYLE.msgs.trialFeedback_outline[field] = STYLE.msgs.trialFeedback[field];
    }
    STYLE.msgs.trialFeedback.font = 'bold 2em Helvetica';
    STYLE.msgs.trialFeedback_outline.color = '#000000';
    STYLE.msgs.trialFeedback_outline.outline = 2;

    STYLE.msgs.loading = {};
    STYLE.msgs.loading.text = 'LOADING EXPERIMENT.\n\nPLEASE WAIT...';
    STYLE.msgs.loading.x = WCANVAS/2.;
    STYLE.msgs.loading.y = HCANVAS/2. - 20;
    STYLE.msgs.loading.color = '#AEAEAE';
    STYLE.msgs.loading.font = '4em Helvetica';
    STYLE.msgs.loading.textAlign = 'center';
    STYLE.msgs.loading.visible = false;

    //////// INITIATE GAME
    var EP = {};  // params that stay constant through experiment
    var tp = {};  // params that change trial by trial
    var wp = {};  // params that can change within a trial
    var tsub = {}; // trial responses from subject that change trial by trial
    // containers that make up easeljs objects - objects are for easily
    // accessing shapes by name
    var background, choiceSet, ulbutton, msgs;
    var a_background, a_choiceSet, a_ulbutton;  // to guarantee order
    var obs_arrays;
    var hidfcn; // visual display of the hidden function
    var ulbutton;
    var QUEUES = {};  // queues containing trial params for each trial of experiment
    var LONOSAVE = ['yHidfcn', 'pyHidfcn', 'XHIDFCN', 'PXHIDFCN', 'rngstate'];

    msgs = make_messages(STYLE.msgs);
    msgs.loading.visible = true;
    stage.addChild(msgs.loading);
    stage.update();

    get_customRoute('init_experiment',  // call init_experiment in custom.py...
                {'condition': condition,  // w params condition adn counter...
                 'counterbalance': counterbalance},
                 function(resp){  // once to get back resp from custom.py...
                    EP.CONDITION = condition;
                    EP.COUNTERBALANCE = counterbalance;
                    EP.RNGSEED = resp['rngseed'];
                    EP.INITSCORE = resp['initscore'];
                    EP.MINDOMAIN = resp['domainbounds'][0][0];
                    EP.MAXDOMAIN = resp['domainbounds'][0][1];
                    EP.BOUNDSX = [EP.MINDOMAIN, EP.MAXDOMAIN];
                    EP.BOUNDSPX = [0, WCANVAS-1];
                    EP.NTRIAL = resp['nTrial'];
                    EP.LENSCALE = resp['lenscale'];
                    EP.SIGVAR = resp['sigvar'];
                    EP.MAXY = EP.SIGVAR * 3.;
                    EP.MINY = EP.SIGVAR * -3.;
                    EP.BOUNDSY = [EP.MINY, EP.MAXY];
                    EP.BOUNDSPY = [YGROUNDLINE, HCANVAS];
                    EP.NOISEVAR2 = resp['noisevar2'];
                    EP.EDGEBUF = resp['edgebuf'];
                    EP.DISTTYPE = resp['disttype'];
                    EP.COSTTODRILL = resp['costToDrill'];
                    EP.COSTTOSAMPLE = resp['costToSample'];
                    EP.DOMAINRES = resp['domainres'];
                    EP.DDOMAIN = (EP.MAXDOMAIN - EP.MINDOMAIN) / EP.DOMAINRES;
                    // make x domain locations
                    EP.XHIDFCN = [EP.MINDOMAIN];
                    for(var i=1; i<EP.DOMAINRES; i++){
                        EP.XHIDFCN.push(EP.XHIDFCN[i-1] + EP.DDOMAIN);
                    }
                    EP.PXHIDFCN = normalize(EP.XHIDFCN, EP.BOUNDSPX, EP.BOUNDSX);

                    QUEUES.NACTIVEOBS = resp['nActiveObsQueue'];
                    QUEUES.NPASSIVEOBS = resp['nPassiveObsQueue'];

                    tp.itrial = resp['itrial'];  // should start at -1
                    tp.rngstate = resp['rngstate'];
                    hidfcn = new createjs.Shape();

                    tsub.totalScore = EP.INITSCORE;
                    // init drill arrays
                    tsub.xActiveObs = [];
                    tsub.yActiveObs = [];
                    tsub.pxActiveObs = [];
                    tsub.pyActiveObs = [];

                    obs_arrays = {};  // for all observations
                    obs_arrays.passive = [];
                    obs_arrays.active = [];
                    // obs_arrays.drill = [];
                    obs_arrays.best = [];

                    background = make_background(STYLE.background, WCANVAS, HCANVAS, YGROUNDLINE);
                    a_background = [background.ground, background.sky];
                    choiceSet = make_choiceSet(STYLE.choiceSet, WCANVAS, YGROUNDLINE);
                    a_choiceSet = [choiceSet.groundline_glow, choiceSet.groundline];
                    ulbutton = make_ulbutton(STYLE.ulbutton);
                    a_ulbutton = [ulbutton.ulbutton_glow, ulbutton.ulbutton];
                    // msgs = make_messages(STYLE.msgs);

                    update_totalScore(tsub.totalScore);
                    msgs.totalScore.visible = true; // visible through whole game

                    stageArray(a_background);
                    stageArray(a_choiceSet);
                    stage.addChild(hidfcn);
                    stageObject(msgs, false);
                    stageArray(a_ulbutton, false);
                    msgs.totalScore.visible = true;  // totalScore always visible
                    msgs.loading.visible = false;  // totalScore always visible

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

        ulbutton.ulbutton_glow.visible = false;
        ulbutton.ulbutton.visible = false;

        // update messages
        msgs.trialFeedback.visible = false;
        msgs.trialFeedback_outline.visible = false;
        msgs.clickulbutton.visible = false;
        msgs.makeChoice.visible = true;

        stage.update();
        wp.tChoiceStarted = getTime();  // start choice timer
    }



    function setup_showFeedback(){
        wp.trialSection = 'showFeedback';
        wp.tFeedbackOn = getTime();

        // update messages
        msgs.makeChoice.visible = false;

        msgs.trialFeedback = update_msg_trialFeedback(msgs.trialFeedback, tsub.trialGross, EP.COSTTODRILL, EP.COSTTOSAMPLE);
        msgs.trialFeedback_outline = update_msg_trialFeedback(msgs.trialFeedback_outline, tsub.trialGross, EP.COSTTODRILL, EP.COSTTOSAMPLE);

        // show hidden function
        hidfcn.visible = true;
        // show drill choice
        // stageArray(obs_arrays.drill);
        stageArray(obs_arrays.best);

        msgs.trialFeedback.visible = true;
        msgs.trialFeedback_outline.visible = true;
        msgs.clickulbutton.visible = true;
        stage.addChild(msgs.trialFeedback);
        stage.addChild(msgs.trialFeedback_outline);

        var posnulb = valid_rand_ulbutton_posn();
        ulbutton.ulbutton.x = posnulb['x'];
        ulbutton.ulbutton.y = posnulb['y'];
        ulbutton.ulbutton_glow.x = posnulb['x'];
        ulbutton.ulbutton_glow.y = posnulb['y'];
        ulbutton.ulbutton.visible = true;
        var zulb = stage.getNumChildren() - 1;
        var zulb_glow = zulb - 1;
        stage.setChildIndex(ulbutton.ulbutton, zulb);
        stage.setChildIndex(ulbutton.ulbutton_glow, zulb_glow);

        choiceSet.groundline_glow.visible = false;

        stage.update();
    }


    function setup_expSummary(){
        wp.trialSection = 'expSummary';

        // update messages
        msgs.makeChoice.visible = false;

        msgs.expSummary = update_msg_expSummary(msgs.expSummary, tsub.totalScore, EP.NTRIAL);

        msgs.expSummary.visible = true;
        stage.addChild(msgs.expSummary);

        ulbutton.ulbutton.visible = true;

        stage.update();
    }


    function update_hidfcn(hidfcn, pxHidfcn, pyHidfcn, stylehf){
        var ghf, px0, py0, prevx, prevy;

        ghf = new createjs.Graphics();
        ghf.f(stylehf.fillColor).
            s(stylehf.strokeColor).
            ss(stylehf.strokeSize, 0, 0);

        // TODO: START FIXING HERE!!
        for(var i=0;i<pxHidfcn.length;i++){

            // scale for drawing
            px0 = pxHidfcn[i];
            py0 = pyHidfcn[i];

            if (i>0){ // if not first point ...
                ghf.mt(prevx, prevy).lt(px0, py0); // draw line from prev point to this point
            }
            prevx = px0;
            prevy = py0;
        }
        hidfcn.graphics = ghf; // set hidden function graphics
        hidfcn.visible = false;
    }


    function update_msg_trialFeedback(msg, trialGross, costToDrill, costToSample){
        var trialNet = trialGross - costToDrill;
        if(costToSample <= 0){  
            msg.text = 'You\'re drilling crew has arrived!\n\n' +
                       '        ' +
                        monify(trialGross) +
                        ' earned drilling\n \n' +
                        '      - ' +
                        monify(costToDrill) +
                        ' spent drilling\n' +
                        '__________________\n \n     '+
                        monify(trialNet) +
                        ' earned this round';
        }
        else{  // show sample cost if sample cost
            var spentSampling = wp.iActiveObs * EP.COSTTOSAMPLE;
            msg.text = 'You\'re drilling crew has arrived!\n\n' +
                '        ' +
                monify(trialGross) +
                ' earned drilling\n \n' +
                '      - ' +
                monify(costToSample) +
                ' spent sampling\n \n' +
                '      - ' +
                monify(costToDrill) +
                ' spent drilling\n \n' +
                '__________________\n'+
                monify(trialNet) +
                ' earned this round';
        }
        return msg;
    }


    function update_msg_expSummary(msg, totalScore, nTrial){
        // show total feedback
            msg.text = 'You explored ' +
                nTrial.toString() +
                ' areas\n\n and earned ' +
                monify(totalScore) +
                '\n\n' +
                'Please click the ignition button to finish.';
        return msg;
    }


    //// functions for setting up a trial
    function setup_nextTrial(){
        // increment tp.itrial and setup the next trial
        tp.itrial += 1;
        if(tp.itrial < EP.NTRIAL){
            
            // clear previous trial's decisions
            for(var field in tsub){
                if(field !== 'totalScore'){
                    tsub[field] = null;    
                }
            }

            // set up this trial
            setup_trial(tp.itrial, tp, QUEUES, STYLE.choiceSet);
        }
        else {
            setup_expSummary(tp.totalScore, EP.NTRIAL);

        }  // end if <NROUND
    }


    function setup_trial(itrial, tp, queues, stylecs){
        // set up things for trial itrial
        set_itrialParams(itrial, tp, queues, 
            function(){
                tsub.pxActiveObs = [];
                tsub.pyActiveObs = [];
                tsub.xActiveObs = [];
                tsub.yActiveObs = [];
                // remove obs from stage and empty obs arrays
                for(var obstype in obs_arrays){
                    unstageArray(obs_arrays[obstype]);
                    obs_arrays[obstype] = [];
                }


                // make hidden function shape for this round
                update_hidfcn(hidfcn, EP.PXHIDFCN, tp.pyHidfcn, STYLE.hidfcn);

                // add new starting observations
                for (var iobs=0; iobs<tp.nPassiveObs; iobs++){
                    add_obs(obs_arrays.passive, tp.pxPassiveObs[iobs], tp.pyPassiveObs[iobs], STYLE.obs.passive);
                }
                stageArray(obs_arrays.passive);

                // restart activeObs counter
                tp.trialNet = 0;
                wp.iActiveObs = 0;

                setup_makeChoice();
            }  // end callback function
        );  // end set_itrialParams
    }  // end setup_trial


    function set_itrialParams(itrial, tp, queues, callback){
        // extract trial params for itrial itrial from the queues in queues
        // var tp = {};  // init trial params

        // see if this is a sam3 trial
        tp.nActiveObs = queues.NACTIVEOBS[itrial];
        tp.nPassiveObs = queues.NACTIVEOBS[itrial];
        
        // generate hidden function and obs server side
        post_customRoute('make_trial',
                    {'lenscale': EP.LENSCALE,
                     'nPassiveObs': tp.nPassiveObs,
                     'rngstate': tp.rngstate
                     },
                    function(resp){
                        console.log('make_trial callback was called');
                        // set trial params
                        tp.yHidfcn = resp['sample'];
                        tp.xPassiveObs = resp['xObs'];
                        tp.yPassiveObs = resp['yObs'];
                        tp.iPassiveObs = resp['iObs'];
                        tp.rngstate = resp['rngstate'];
                        tp.pyHidfcn = normalize(tp.yHidfcn, EP.BOUNDSPY, EP.BOUNDSY);
                        tp.pxPassiveObs = normalize(tp.xPassiveObs, EP.BOUNDSPX, EP.BOUNDSX);
                        tp.pyPassiveObs = normalize(tp.yPassiveObs, EP.BOUNDSPY, EP.BOUNDSY);
                        tp.itrial = itrial;

                        callback();
                    });
    }


    //// functions for saving and tearing down a trial
    function add_obs(array, px, py, style){
        // adds obs as loc (px,py) to array array with style style
        var obs = make_obs(px, py, style);
        array.push(obs);
    }


    function activeObs_made(px){
        // what happens after an active obs is made
        tsub.choiceRT = getTime() - wp.tActiveObsStarted;
        px = min([px, tp.yHidfcn.length-1]);
        var pxActiveObs = px;
        // JBEDIT: this only works when the choice set is a horizontal line spanning the whole canvas.
        //         This is not an abstracted way to map choice -> value
        var yActiveObs = tp.yHidfcn[px];
        var xActiveObs = normalize(px, EP.BOUNDSX, EP.BOUNDSPX);
        var pyActiveObs = normalize(yActiveObs, EP.BOUNDSPY, EP.BOUNDSY);

        // add obs to drill array
        tsub.pxActiveObs.push(pxActiveObs);
        tsub.pyActiveObs.push(pyActiveObs);
        tsub.xActiveObs.push(xActiveObs);
        tsub.yActiveObs.push(yActiveObs);


        // subtract sample cost
        tsub.trialNet -= EP.SAMPLECOST;

        // add obs to canvas
        add_obs(obs_arrays.active, pxActiveObs, pyActiveObs, STYLE.obs.active);
        stageArray(obs_arrays.active);

//         // add new starting observations
//         for (var iobs=0; iobs<tp.nPassiveObs; iobs++){
//             add_obs(obs_arrays.passive, tp.pxPassiveObs[iobs], tp.pyPassiveObs[iobs], STYLE.obs.passive);
//         }
//         stageArray(obs_arrays.passive);

        // update score
        tsub.trialNet -= EP.COSTTOSAMPLE;
        tsub.totalScore -= EP.COSTTOSAMPLE;
        update_totalScore(tsub.totalScore);

        wp.iActiveObs += 1;  // inc activeObs counter

        // if time to collect best discovered this round
        if (wp.iActiveObs === tp.nActiveObs){  

            // maintain list of all samples on screen
            tsub.xAllObs = tsub.xActiveObs.concat(tp.xPassiveObs);  // get score
            tsub.yAllObs = tsub.yActiveObs.concat(tp.yPassiveObs);  // get score
            tsub.pxAllObs = tsub.pxActiveObs.concat(tp.pxPassiveObs);  // get score
            tsub.pyAllObs = tsub.pyActiveObs.concat(tp.pyPassiveObs);  // get score

            var iBest = argmax(tsub.yAllObs);
            tsub.xBest = tsub.xAllObs[iBest];
            tsub.pxBest = tsub.pxAllObs[iBest];
            tsub.yBest = tsub.yAllObs[iBest];
            tsub.pyBest = tsub.pyAllObs[iBest];

            tsub.trialGross = yToScore(tsub.yBest, EP.BOUNDSY);

            // add best obs to canvas
            add_obs(obs_arrays.best, tsub.pxBest, tsub.pyBest, STYLE.obs.best);

            tsub.totalScore += tsub.trialGross;
            tsub.totalScore -= EP.COSTTODRILL;
            update_totalScore(tsub.totalScore);

            //TODO: figure out if earned should be xDrill or not
            tsub.trialNet += tsub.trialGross;
            tsub.trialNet -= EP.COSTTODRILL;
            store_thisTrial(setup_showFeedback);
        }
    }


    function yToScore(y, boundsY){
        var score = Math.ceil(normalize(y, [0., 100.], boundsY));
        score = min([score, 100.])
        score = max([score, 0.])
        return score;
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
        jsb_recordTurkData([EP, tp, tsub], LONOSAVE, callback);
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
        var background_objs = {};
        var ground = new createjs.Shape();
        var groundline2bottom = canvasH - yGroundline;

        ground.graphics.s(stylebg.ground.strokeColor).
                    f(stylebg.ground.fillColor).
                    ss(stylebg.ground.strokeSize, 0, 0).
                    r(0, yGroundline, canvasW, groundline2bottom);
        ground.visible = true;

        // sky Graphics
        var sky = new createjs.Shape();
        sky.graphics.s(stylebg.sky.strokeColor).
                        f(stylebg.sky.fillColor).
                        ss(stylebg.sky.strokeSize, 0, 0).
                        r(0, 0, canvasW, yGroundline);
        sky.visible = true;


        // add to background array
        background_objs.ground = ground;
        background_objs.sky = sky;

        return background_objs;
    }


    function make_ulbutton(styleulb, yGroundline){
        "use strict"
        var ulbutton_objs = {};

        var ulbutton = new createjs.Shape();
        var ulbutton_glow = new createjs.Shape();
        var sbutton = styleulb.ulbutton;
        var sglow = styleulb.ulbutton_glow;

        // ululbutton Style
        ulbutton.graphics.s(sbutton.strokeColor).
                          f(sbutton.fillColor).
                          ss(sbutton.strokeSize, 0, 0).
                          dc(0, 0, sbutton.radius);
        ulbutton.x = sbutton.x;
        ulbutton.y = sbutton.y;
        ulbutton.visible = false;

        var ulbutton_glow = new createjs.Shape();
        var sglow_ss = sbutton.strokeSize * sglow.ratioGlowBigger;
        // ululbutton Style
        ulbutton_glow.graphics.s(sglow.strokeColor).
                          f(sglow.fillColor).
                          ss(sglow_ss, 0, 0).
                          mt(0, yGroundline). // GROUNDLINE HEIGHT
                          dc(0, 0, sglow.radius);
        ulbutton_glow.x = sglow.x;
        ulbutton_glow.y = sglow.y;
        ulbutton_glow.visible = false;

        // ulbutton Actions
        ulbutton.addEventListener('mouseover', function(){
            if(['showFeedback', 'expSummary'].indexOf(wp.trialSection) > -1){
                ulbutton_glow.visible = true;
                stage.update();
            }

        });

        ulbutton.addEventListener('mouseout', function(){
            if(['showFeedback', 'expSummary'].indexOf(wp.trialSection) > -1){
                ulbutton_glow.visible = false;
                stage.update();
            }
        });

        ulbutton.addEventListener('click', function(){
            if(wp.trialSection === 'showFeedback'){
                setup_nextTrial();
            }
            else if(wp.trialSection === 'expSummary'){
                endExp();
            }
        });

        ulbutton_objs.ulbutton = ulbutton;
        ulbutton_objs.ulbutton_glow = ulbutton_glow;

        return ulbutton_objs;
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
        var groundline_glow_ss = stylecs.groundline.strokeSize * stylecs.groundline_glow.ratioGlowBigger;
        groundline_glow.graphics.s(stylecs.groundline_glow.strokeColor).
                            ss(groundline_glow_ss, 0, 0).
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
                var pxActiveObs = stage.mouseX;
                activeObs_made(pxActiveObs);
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

    function argmin(array) {
        var argmin = 0;
        var bestSoFar = array[0];
        for(var i=0; i<array.length; i++){
            if (min([array[i], bestSoFar]) < bestSoFar){
                bestSoFar = array[i];
                argmin = i;
            }
        }
        return argmin;
    }

    function argmax(array) {
        var argmax = 0;
        var bestSoFar = array[0];
        for(var i=0; i<array.length; i++){
            if (max([array[i], bestSoFar]) > bestSoFar){
                bestSoFar = array[i];
                argmax = i;
            }
        }
        return argmax;
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
        // takes a, which lives in interval frombounds, and maps to interval tobounds
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

        if (a instanceof Array){  // a is an array
            a = a.map(function(elt){return elt-fromlo;});
            a = a.map(function(elt){return elt/fromrange;}); // now in 0, 1
            a = a.map(function(elt){return elt*torange});
            a = a.map(function(elt){return elt+tolo});
        }
        else {  // a is a scalar
            a -= fromlo;
            a /=fromrange; // now in 0, 1
            a *= torange;
            a += tolo;
        }

        return a;
    }

    // logical XOR
    function xor(a,b){
        return ( a ? !b : b);
    }


    // use instead of % b.c. javascript can't do negative mod
    function mod(a, b){return ((a%b)+b)%b;}

    function rand(min, max){
        min = typeof min !== 'undefined' ? min : 0; // default
        max = typeof max !== 'undefined' ? max : 1; // default
        assert(max - min >= 0., 'min must be <= max');
        var range = max - min;
        return Math.random() * range  + min;
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


    function valid_rand_ulbutton_posn(){
        // returns a posn to randomly place start button that won't intersect feedback message
            var good = false;
            while(!good){
                var x = rand(20, WCANVAS - 20);
                var y = rand(YGROUNDLINE + 20, HCANVAS - 20);
                var xpercent = x / WCANVAS;
                var ypercent = (y - YGROUNDLINE) / GROUNDLINE2BOTTOM;
                good = xor((xpercent < 1./4 || xpercent > 3./4),
                           (ypercent < 1./4 || ypercent > 3./4));
            }
            return {'x': x,
                    'y': y};
        }


    function jsb_recordTurkData(loObj, loNoSave, callback){
        loNoSave = typeof loNoSave !== 'undefined' ? loNoSave : []; // default sorted

        var toSave = {};
        loObj.map(function(obj){  // for every obj in loObj...
            for(var field in obj){
                toSave[field] = obj[field];  // add to dict toSave
            }
        });

        // remove fields specified to not save
        loNoSave.map(function(field){
            delete toSave[field];
        })

        psiTurk.recordTrialData(toSave);  // store on client side
        psiTurk.saveData();  // save to server side
        callback();
    }
};
