/*
 * Requires:
 *     psiturk.js
 *     utils.js
 */

// Initalize psiturk object
var psiTurk = JSBPsiTurk(uniqueId, adServerLoc);

var mycondition = condition;  // these two variables are passed by the psiturk server process
var mycounterbalance = counterbalance;  // they tell you which condition you have been assigned to
// they are not used in the stroop code but may be useful to you

var INS_FOLDER = 'instructions';

var pages = [ // add as a list as many pages as you like
    // INS_FOLDER + "/instr_1.html",
    // INS_FOLDER + "/instr_2.html",
    // INS_FOLDER + "/instr_3.html",
    // INS_FOLDER + "/instr_4.html",
    // INS_FOLDER + "/instr_5.html",
    // INS_FOLDER + "/instr_6.html",
    // INS_FOLDER + "/instr_7.html",
    // INS_FOLDER + "/instr_8.html",
    INS_FOLDER + "/instr_ready.html",
    "stage.html",
    "debriefing.html"
];

psiTurk.preloadPages(pages);
var instructionPages = [ // add as a list as many pages as you like
    // INS_FOLDER + "/instr_1.html",
    // INS_FOLDER + "/instr_2.html",
    // INS_FOLDER + "/instr_3.html",
    // INS_FOLDER + "/instr_4.html",
    // INS_FOLDER + "/instr_5.html",
    // INS_FOLDER + "/instr_6.html",
    // INS_FOLDER + "/instr_7.html",
    // INS_FOLDER + "/instr_8.html",
    INS_FOLDER + "/instr_ready.html",
];

/********************
* HTML manipulation
*
* All HTML files in the templates directory are requested
* from the server when the PsiTurk object is created above. We
* need code to get those pages from the PsiTurk object and
* insert them into the document.
*
********************/
// function runner(){
//     Load the stage.html snippet into the body of the page
//     psiTurk.finishInstructions();
//     psiTurk.showPage('stage.html'); // load game stage
//     run_drillGame();
// }
/*******************
 * Run Task
 ******************/

 // Task object to keep track of the current phase
var currentview;
$(window).load( function(){
    width = 1028;
    height = 768;
    var buffer = 100;
    window.resizeTo(width + buffer, height + buffer);
    window.moveTo(((screen.width - width) / 2), 0); //((screen.height - height) / 2));
    psiTurk.doInstructions(
        instructionPages, // a list of pages you want to display in sequence
        function(){
            psiTurk.finishInstructions();
            psiTurk.showPage('stage.html'); // load game stage
            currentview = new drillGame();
        }
    );
});
