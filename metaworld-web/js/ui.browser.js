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
var ret = {};


// ---- when new data in dbm arrives, create list of classifications

function refreshClassList(){
    // turn classes overview into HTML structure, and store data in them.
    var classesOverview = dbm.getClasses();

    $('.mw-classes-list').empty();

    classesOverview.forEach(function(each){
        $('#templates [name="mw-classes-item"]')
            .clone()
            .appendTo('.mw-classes-list')
            .data('questions', each.questions)
            .find('[name="name"]')
                .text(each.name)
                .parent()
        ;
    });
}
ps.subscribe('evt:metadata.refresh', refreshClassList);




return ret;
//////////////////////////////////////////////////////////////////////////////
});
