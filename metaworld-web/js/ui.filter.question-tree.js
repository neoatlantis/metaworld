define([
    'dbmanage',
    'jquery',
    'pubsub',
    'jstree'
], function(
    dbm,
    $,
    ps
){
//////////////////////////////////////////////////////////////////////////////


// ---- Listens for `evt.metadata.refresh` and refresh js tree.

function reloadQuestionTree(){
    var questions = dbm.getQuestions(), 
        categories = dbm.getQuestionCategories();
    var jstdata = [];

    // first put all categories in
    for(var catid in categories){
        jstdata.push({
            'parent': '#',
            'id': 'mwquestion-category-' + catid,
            'text': categories[catid],
        });
    }
    
    // and then questions
    var parentID, question, categoryFind;
    for(var qid in questions){
        question = questions[qid];
        parentID = '#';
        categoryFind = categories.indexOf(question.category);
        if(categoryFind >= 0){
            parentID = 'mwquestion-category-' + categoryFind;
        }
        jstdata.push({
            'parent': parentID,
            'id': 'mwquestion-question-' + qid,
            'text': question.name,
            'li_attr': {
                'data-qid': qid,
            }
        });
    }
    
    $('.mw-questions-tree')
        .jstree({
            core: {
                data: jstdata,
            }
        })
        .on('select_node.jstree', function(e, obj){
            var qid = obj.node.li_attr['data-qid'];
            ps.publish('evt:ui.filter.question-tree.selection', qid);
        })
    ;
}

ps.subscribe('evt:metadata.refresh', reloadQuestionTree);



// ---- when user answers changed, update js tree to show which questions were
//      answered

function updateJstreeMarkAnsweredQuestion(en, userAnswers){
    // TODO
    console.log(userAnswers);
}
ps.subscribe('evt:ui.filter.changed', updateJstreeMarkAnsweredQuestion);

//////////////////////////////////////////////////////////////////////////////
});
