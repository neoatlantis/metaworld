define([
    'dbmanage',
    'jquery',
    'pubsub',
    'ui.filter.question-tree',
    'ui.jquery.qgen',
], function(
    dbm,
    $,
    ps
){
//////////////////////////////////////////////////////////////////////////////

var userAnswers = {};

// ---- manage general user selection of new answers

function updateUserAnswer(qid, newAnswer){
    if(!newAnswer){
        delete userAnswers[qid];
    } else {
        userAnswers[qid] = newAnswer;
    }
    ps.publish('evt:ui.filter.changed', userAnswers);
}



// ---- on selection of an item in js tree

function onSelectNodeJstree(en, qid){
    if(qid){
        // a question was selected
        $('.mw-question-sheet .mw-no-question').hide();
        $('.mw-question-sheet .mw-has-question').show();
    } else {
        // not a question selected
        $('.mw-question-sheet .mw-no-question').show();
        $('.mw-question-sheet .mw-has-question').hide();
        return;
    }
    var q = dbm.getQuestion(qid);
    $('.mw-has-question')
        .empty()
        .data('qid', qid)
        .questionify(q, userAnswers[qid])
        .on('click', function(){
            var qid = $(this).data('qid');
            updateUserAnswer(qid, $(this).questionify('read'));
        })
    ;
}
ps.subscribe('evt:ui.filter.question-tree.selection', onSelectNodeJstree);







//////////////////////////////////////////////////////////////////////////////
});
