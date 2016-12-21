(function(){
var questions = {}, classes = [], categories = [];
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

function findQuestionCategories(){
    categories = [];
    for(var qid in questions){
        if(categories.indexOf(questions[qid].category) < 0){
            categories.push(questions[qid].category);
        }
    }
}

function loadData(){
    questions = {};
    classes = [];
    loadMetaworldData(loadClass, loadQuestion);
    findQuestionCategories();
    ps.publish('evt:metadata.refresh');
}

ps.subscribe('evt:document.ready', loadData);

// ---- tool functions for searching database

ret.getQuestions = function(){
    var ret = {}, q;
    for(var qid in questions){
        q = questions[qid];
        ret[qid] = {
            id: qid,
            name: q.name,
            category: q.category,
            type: q.type,
        }
    }
    return ret;
}

ret.getQuestion = function(qid){
    var q = questions[qid], ret = {}
    if(!q) return null;
    ret.id = qid;
    ret.name = q.name;
    ret.category = q.category;
    ret.type = q.type;
    ret.max = q.max;
    ret.min = q.min;
    ret.plain = q.plain;
    ret.tree = q.tree;
    return ret;
}

ret.getQuestionCategories = function(){
    var ret = [];
    for(var i in categories) ret.push(categories[i]);
    return ret;
}

return ret;

//////////////////////////////////////////////////////////////////////////////
});
})();
