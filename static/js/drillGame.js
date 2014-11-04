/********************
*    DRILLING GAME             *
********************/
var drillGame = function(){
    "use strict";
    // var njs = numeric;
    var canvas = document.getElementById('easel');
    var W = canvas.width;
    var H = canvas.height;
    var GROUNDLINEY = H - H*0.9;
    var GROUNDLINE2BOTTOM = H - GROUNDLINEY;
    var stage = new createjs.Stage(canvas);
    stage.enableMouseOver(10); // check for mouseovers 5x per sec

    //////// STYLE SHEETS FOR THE GAME
    var STYLE = [];
    STYLE.ulButton = [];
    STYLE.groundLine = [];
    STYLE.hidFcn = [];
    STYLE.samArray = [];
    STYLE.drillArray = [];
    STYLE.ground = [];
    STYLE.sky = [];
    STYLE.groundLine_glow = [];
    STYLE.ulButton_glow = [];
    STYLE.ulButton_text = [];
    STYLE.score_text = [];
    STYLE.roundSummary_text = [];


    STYLE.ulButton.STROKECOLOR = 'gray';
    STYLE.ulButton.FILLCOLOR = 'blue';
    STYLE.ulButton.STROKESIZE = 5;
    STYLE.ulButton.CIRCRADIUS = 20;

    STYLE.groundLine.STROKECOLOR = '#D9BAAB';
    STYLE.groundLine.FILLCOLOR = null;
    STYLE.groundLine.STROKESIZE = 10;

    STYLE.hidFcn.FILLCOLOR = null;
    STYLE.hidFcn.STROKECOLOR = 'black';
    STYLE.hidFcn.STROKESIZE = 3;

    STYLE.samArray.STROKECOLOR = 'white';
    STYLE.samArray.FILLCOLOR = null;
    STYLE.samArray.STROKESIZE = 3;
    STYLE.samArray.CIRCRADIUS = 8;

    STYLE.drillArray.STROKECOLOR = 'red';
    STYLE.drillArray.FILLCOLOR = null;
    STYLE.drillArray.STROKESIZE = 4;
    STYLE.drillArray.CIRCRADIUS = 12;

    STYLE.ground.STROKESIZE = 5;
    STYLE.ground.STROKECOLOR = '#A0522D';
    STYLE.ground.FILLCOLOR = '#A0522D';

    STYLE.sky.STROKESIZE = 5;
    STYLE.sky.STROKECOLOR = '#33CCCC';
    STYLE.sky.FILLCOLOR = '#33CCCC';

    STYLE.groundLine_glow.STROKECOLOR = '#EACDDC';
    STYLE.groundLine_glow.STROKESIZE = 15;

    STYLE.ulButton_glow.STROKECOLOR = 'green';
    STYLE.ulButton_glow.FILLCOLOR = 'green';
    STYLE.ulButton_glow.STROKESIZE = 20;
    STYLE.ulButton_glow.CIRCRADIUS = 20;

    STYLE.ulButton_text.TEXTSTYLE = '1.5em Helvetica';
    STYLE.ulButton_text.COLOR = 'black';

    STYLE.score_text.TEXTSTYLE = '2em Helvetica';
    STYLE.score_text.COLOR = 'black';

    STYLE.roundSummary_text.TEXTSTYLE = '1.5em Helvetica';
    STYLE.roundSummary_text.COLOR = 'white';



    //////// GAME OBJECTS
    // ulButton Graphics
    var ulButton = new createjs.Shape();
    ulButton.graphics.s(STYLE.ulButton.STROKECOLOR).
                    f(STYLE.ulButton.FILLCOLOR).
                    ss(STYLE.ulButton.STROKESIZE, 0, 0).
                    dc(0, 0, STYLE.ulButton.CIRCRADIUS);
    ulButton.x = 40;
    ulButton.y = 35;
    ulButton.visible = false;

    // ulButton Actions
    ulButton.addEventListener('mouseover', function(){
            ulButton_glow.visible = true;
            stage.update();
    });

    ulButton.addEventListener('mouseout', function(){
            ulButton_glow.visible = false;
            stage.update();
    });

    ulButton.addEventListener('click', function(){
        switch(roundSection){
            case 'roundSummary':
                roundSection = 'newRound';
                setup_newRound();
                break;
            case 'expSummary':
                endExp();
                break;
        }
    });


    // ulButton_glow Graphics
    var ulButton_glow = new createjs.Shape();
    ulButton_glow.graphics.s(STYLE.ulButton_glow.STROKECOLOR).
                    f(STYLE.ulButton_glow.FILLCOLOR).
                    ss(STYLE.ulButton_glow.STROKESIZE, 0, 0).
                    dc(0, 0, STYLE.ulButton_glow.CIRCRADIUS);
    ulButton_glow.x = 40;
    ulButton_glow.y = 35;
    ulButton_glow.visible = false;

    // groundLine Graphics
    var groundLine = new createjs.Shape();
    groundLine.graphics.s(STYLE.groundLine.STROKECOLOR).
                        ss(STYLE.groundLine.STROKESIZE, 0, 0).
                        mt(0, GROUNDLINEY). // GROUNDLINE HEIGHT
                        lt(W, GROUNDLINEY);
    groundLine.visible = true;

    // groundLine Actions
    groundLine.addEventListener('mouseover', function(){
        groundLine_glow.visible = true;
        stage.update();
    });

    groundLine.addEventListener('mouseout', function(){
        groundLine_glow.visible = false;
        stage.update();
    });

    groundLine.addEventListener('click', function(){
        if(roundSection == 'drilling'){
            pdrillX = stage.mouseX;
            pdrillY = pY[pdrillX];
            show_roundSummary(pdrillX, pdrillY);
        }
    });


    // groundLine_glow Graphics
    var groundLine_glow = new createjs.Shape();
    groundLine_glow.graphics.s(STYLE.groundLine_glow.STROKECOLOR).
                                ss(STYLE.groundLine_glow.STROKESIZE, 0, 0).
                                mt(0, GROUNDLINEY). // GROUNDLINE HEIGHT
                                lt(W, GROUNDLINEY);
    groundLine_glow.visible = false;



    // ground Graphics
    var ground = new createjs.Shape();
    ground.graphics.s(STYLE.ground.STROKECOLOR).
                    f(STYLE.ground.FILLCOLOR).
                    ss(STYLE.ground.STROKESIZE, 0, 0).
                    r(0, GROUNDLINEY, W, GROUNDLINE2BOTTOM);
    ground.visible = true;


    // sky Graphics
    var sky = new createjs.Shape();
    sky.graphics.s(STYLE.sky.STROKECOLOR).
                    f(STYLE.sky.FILLCOLOR).
                    ss(STYLE.sky.STROKESIZE, 0, 0).
                    r(0, 0, W, GROUNDLINEY);
    sky.visible = true;


    // observation prototype
    function Obs(x, y){
        var obs = new createjs.Shape();
        obs.graphics.s(STYLE.samArray.STROKECOLOR).
                    f(STYLE.samArray.FILLCOLOR).
                    ss(STYLE.samArray.STROKESIZE, 0, 0).
                    dc(0, 0, STYLE.samArray.CIRCRADIUS);
        obs.x = x;
        obs.y = y;
        obs.visible = true;
        return obs;
    }

    // drill prototype
    function Drill(x, y){
        var drill = new createjs.Shape();
        drill.graphics.s(STYLE.drillArray.STROKECOLOR).
                    f(STYLE.drillArray.FILLCOLOR).
                    ss(STYLE.drillArray.STROKESIZE, 0, 0).
                    dc(0, 0, STYLE.drillArray.CIRCRADIUS);
        drill.x = x;
        drill.y = y;
        drill.visible = false;
        return drill;
    }


    // ulButton_text Graphics
    var ulButton_text = new createjs.Text('', STYLE.ulButton_text.TEXTSTYLE,
                                        STYLE.ulButton_text.COLOR);
    ulButton_text.x = 70;
    ulButton_text.y = 35 - 10;
    ulButton_text.visible = false;


    // score_text Graphics
    var score_text = new createjs.Text('', STYLE.score_text.TEXTSTYLE,
                                        STYLE.score_text.COLOR);
    score_text.x = W - 120;
    score_text.y = 35 - 10;
    score_text.visible = true;


    // roundSummary_text Graphics
    var roundSummary_text = new createjs.Text('', STYLE.roundSummary_text.TEXTSTYLE,
                                        STYLE.roundSummary_text.COLOR);
    roundSummary_text.x = W/2 - 150;
    roundSummary_text.y = H/2;
    roundSummary_text.visible = false;



    //////// GAME LOGIC
    var X, Y, pX, pY, xObs, yObs, pxObs, pyObs, nX;
    var YMAX = 3;
    var YMIN = -YMAX;
    var YRANGE = YMAX - YMIN;
    var NROUND, COST2DRILL, STARTPOINTS, W2T, T2W;
    var drill, drillX, drillY, pdrillX, pdrillY;
    var samArray, hidFcn;
    var expScore, roundNet, roundGross, roundScore;
    var round, roundSection, d2i;

    // statics (LENSCALE may vary in future)
    var LENSCALE, SIGVAR, NOISEVAR2, RNGSEED;
    var D2LOCS_QUEUEX, D2LOCS_QUEUEY, NOBSQUEUE, D2L1INDS;

    var nObs, d2locsX, d2locsY;  // change every round

    customRoute('init_experiment',
                {'condition': condition,
                 'counterbalance': counterbalance},
                 function(resp){
                    NROUND = resp['nRound'];
                    X = resp['x'];
                    nX = X.length;
                    W2T = nX/W;
                    T2W = W/nX;
                    pX = math2pixX(X);
                    COST2DRILL = resp['cost2drill'];
                    STARTPOINTS = resp['startPoints'];
                    LENSCALE = resp['lenscale'];
                    SIGVAR = resp['sigvar'];
                    NOISEVAR2 = resp['noisevar2'];
                    RNGSEED = resp['rngseed'];

                    round = resp['round'];
                    d2i = resp['d2i'];
                    D2LOCS_QUEUEX = resp['d2locsQueueX'];
                    D2LOCS_QUEUEY = resp['d2locsQueueY'];
                    NOBSQUEUE = resp['nObsQueue'];
                    D2L1INDS = resp['D2L1Inds'];

                    expScore = STARTPOINTS;
                    score_text.text = monify(expScore);
                    roundNet = NaN;
                    roundGross = NaN;

                    drill = Drill(pdrillX, pdrillY);
                    drill.visible = false;
                    samArray = [];
                    hidFcn = new createjs.Shape();

                    // add all objects to the stage
                    stage.addChild(ground);
                    stage.addChild(sky);
                    stage.addChild(groundLine_glow);
                    stage.addChild(groundLine);
                    stage.addChild(hidFcn);
                    stage.addChild(drill);
                    stage.addChild(roundSummary_text);
                    stage.addChild(score_text);
                    stage.addChild(ulButton_glow);
                    stage.addChild(ulButton);
                    stage.addChild(ulButton_text);

                    var tmp = new createjs.Shape();
                    //var tmpy = math2pixY([0])[0];
                    var tmpy = H;
                    tmp.graphics.s('black').ss(5,0,0).mt(0, tmpy).lt(W, tmpy);
                    tmp.visible = true;
                    stage.addChild(tmp);


                    setup_newRound();
                });


    function setup_newRound(X, Y, xObs, yObs){
        round += 1;
        jsb_recordTurkData(function(){
            // if have more rounds to go...
            console.log('round '+round.toString()+' saved successfully.');
            if (round < NROUND){
                nObs = NOBSQUEUE[round];
                if (nObs===2){
                    d2i += 1;
                    d2locsX = D2LOCS_QUEUEX[d2i];
                    d2locsY = D2LOCS_QUEUEY[d2i];
                }
                else {
                    d2locsX = 'None';
                    d2locsY = 'None';
                }

                customRoute('get_nextTrial',
                            {'lenscale': LENSCALE,
                                'nObs': nObs,
                                'd2locsX': JSON.stringify(d2locsX),
                                'd2locsY': JSON.stringify(d2locsY)
                            },
                    function(resp){  // SETUP NEW ROUND
                        // get this round's fcn info
                        Y = resp['sample'];
                        pY = math2pixY(Y);
                        xObs = resp['xObs'];
                        yObs = resp['yObs'];

                        // remove previous round's obs
                        unstageArray(samArray);
                        samArray = [];

                        // remove prev round summary and drill loc
                        drill.visible = false;
                        roundSummary_text.visible = false;

                        // draw new hidden function
                        update_hidFcn(pX, pY);

                        // add this round's obs
                        pxObs = math2pixX(xObs);
                        pyObs = math2pixY(yObs);
                        addSams(pxObs, pyObs);
                        stageArray(samArray);

                        roundSection = 'drilling';
                        stage.update();
                    }  // end round setup
                );  // end custom route
            }
            else {

                // TODO: endgame goes here
                roundSection = 'expSummary';
                // show total feedback
                roundSummary_text.text = 'You played ' +
                    NROUND.toString() +
                    ' rounds\n\n and earned ' +
                    monify(expScore) +
                    '\n\n' +
                    'Please click the ignition button to finish.';

                roundSummary_text.visible = true;
                ulButton.visible = true; // enable click-to-leave
                ulButton_text.visible = false; // enable click-to-leave

            }  // end if <NROUND
        });  // end jsb_record
    } // end setup_newRound


    function show_roundSummary(pdrillX, pdrillY){
        // show drill location
        drillX = pix2mathX([pdrillX])[0];
        drillY = pix2mathY([pdrillY])[0];
        drill.x = pdrillX;
        drill.y = pdrillY;
        drill.visible = true;

        // show hidFcn
        hidFcn.visible = true;

        // show score
        roundGross = getRoundGross(drillY, YMIN, YRANGE);
        roundNet = roundGross - COST2DRILL;
        roundScore = roundNet; // same here bc no cost2sam

        // increment experiment score
        expScore += roundScore;
        score_text.text = monify(expScore);

        roundSummary_text.text = '        ' + monify(roundGross) + ' earned drilling\n \n' +
        '      - ' + monify(COST2DRILL) + ' spent drilling\n \n' +
        '__________________\n \n     '+
        monify(roundNet) + ' earned this round';
        roundSummary_text.visible = true;

        // show upper left button
        ulButton.visible = true;
        ulButton_text.text = 'Click button to move to next round';
        ulButton_text.visible = true;

        roundSection = 'roundSummary';
        stage.update();
    }


    function getRoundGross(drillY, ymin, yrange){
        var gross = ((drillY - ymin) / yrange) * 100;
        if (gross > 100){gross = 100;}
        if (gross < 0){gross = 0;}

        return gross;
    }


    function addSams(pxObs, pyObs){
        var nStart = samArray.length;
        for(var i=0; i<pxObs.length; i++){
            var obs0 = Obs(pxObs[i], pyObs[i]);
            samArray.push(obs0);
            samArray[nStart + i].visible = false;
        }
    }


    function stageArray(shapeArray){
        for (var i=0; i<shapeArray.length; i++){
            stage.addChild(shapeArray[i]);
            shapeArray[i].visible = true;
        }
        stage.update();
    }


    function unstageArray(shapeArray){
        for (var i=0; i<shapeArray.length; i++){
            shapeArray[i].visible = false;
            stage.removeChild(shapeArray[i]);
        }
    }


    function update_hidFcn(pX, pY){
        var ghf, px0, py0, prevx, prevy;

        ghf = new createjs.Graphics();
        ghf.f(STYLE.hidFcn.FILLCOLOR).
            s(STYLE.hidFcn.STROKECOLOR).
            ss(STYLE.hidFcn.STROKESIZE, 0, 0);

        // TODO: START FIXING HERE!!
        for(var i=0;i<pX.length;i++){

            // scale for drawing
            px0 = pX[i];
            py0 = pY[i];

            if (i>0){ // if not first point ...
                ghf.mt(prevx, prevy).lt(px0, py0); // draw line from prev point to this point
            }
            prevx = px0;
            prevy = py0;
        }
        hidFcn.graphics = ghf; // set hidden function graphics
        hidFcn.visible = false;
    }

    function endExp(){
        psiTurk.showPage('debriefing.html');
    }



    //////// HELPER FUNCTIONS
    function math2pixX(A){
        var a = A.slice(0); // copy array
        for(var i=0; i<a.length; i++){
            a[i] *= W;
        }
        return a;
    }


    function pix2mathX(A){
        var a = A.slice(0); // copy array
        for (var i=0; i<a.length; i++){
            a[i] /= W;
        }
        return a;
    }


    function math2pixY(A){
        var a = A.slice(0);
        for(var i=0; i<a.length; i++){
            a[i] -= YMIN;  // shift range to (0,1)
            a[i] /= YRANGE;
            a[i] *= GROUNDLINE2BOTTOM;  // shift to range (0,groundline2bottom)
            a[i] += GROUNDLINEY;  // shift 0 to groundline

        }
        return a;
    }


    function pix2mathY(A){
        var a = A.slice(0); // copy array
        for (var i=0; i<a.length; i++){
            a[i] -= GROUNDLINEY;
            a[i] /= GROUNDLINE2BOTTOM;
            a[i] *= YRANGE;
            a[i] += YMIN;
        }
        return a;
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


    function jsb_recordTurkData(callback){
        psiTurk.recordTrialData({
            'round': round,
            'expScore': expScore,
            'roundNet': roundNet,
            'roundGross': roundGross,
            'nObs': nObs,
            'drillX': drillX,
            'drillY': drillY,
            'pdrillX': pdrillX,
            'pdrillY': pdrillY,
            'xObs': xObs,
            'yObs': yObs,
            'd2locsX': d2locsX,
            'd2locsY': d2locsY,
            'pxObs': pxObs,
            'pyObs': pyObs,
            'RNGSEED': RNGSEED,
            'LENSCALE': LENSCALE,
            'SIGVAR': SIGVAR,
            'NOISEVAR2': NOISEVAR2,
            'condition': condition,
            'counterbalance': counterbalance
        });
        psiTurk.saveData();
        callback();
    }
};
