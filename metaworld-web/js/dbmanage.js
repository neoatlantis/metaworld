(function(){
var questions = {}, classes = [];
define(['pubsub'], function(ps){
//////////////////////////////////////////////////////////////////////////////

var ret = {};

// ---- functions for loading data from external JSONP

function loadClass(json){
    classes.push(json);
}

function loadQuestion(qrepr, qfunc){
    var qid = qrepr.id;
    questions[qid] = qrepr;
    questions[qid].calculate = qfunc;
}

function loadData(){
    questions = {};
    classes = [];
    loadMetaworldData(loadClass, loadQuestion);
    ps.publish('evt:metadata.refresh');
}

ps.subscribe('evt:document.ready', loadData);

// ---- tool functions for searching database

ret.getQuestions = function(){
    var ret = {}, q;
    for(var qid in questions){
        q = questions[qid];
        ret[qid] = {
            name: q.name,
            category: q.category,
            type: q.type,
        }
    }
    return ret;
}

return ret;

//////////////////////////////////////////////////////////////////////////////
});
})();
