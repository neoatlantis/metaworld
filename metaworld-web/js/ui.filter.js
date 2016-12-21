define([
    'dbmanage',
    'jquery',
    'pubsub',
], function(
    dbm,
    $,
    ps
){
//////////////////////////////////////////////////////////////////////////////

function reloadFilter(){
    var questions = dbm.getQuestions();
    console.log(questions);
}

ps.subscribe('evt:metadata.refresh', reloadFilter);


//////////////////////////////////////////////////////////////////////////////
});
