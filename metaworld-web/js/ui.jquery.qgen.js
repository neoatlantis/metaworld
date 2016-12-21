/* Question Generator as plugin to jquery */

define(['jquery'], function($){
//////////////////////////////////////////////////////////////////////////////
$.fn.questionify = function(action, olddata){
    if('read' == action){
        // return user answer
        
        if(this.data('type') == 'choose'){
            var ret = [];
            this.find('.active[name="choice"]').each(function(){
                ret.push($(this).data('name'));
            });
            if(ret.length < 1) return null;
            return ret;
        }

        if(this.data('type') == 'range'){
            return;
        }

        return;
    }

    // or initialize this html element
    
    var q = action;
    if(!olddata) olddata = [];
    this.empty();

    this.data('type', q.type);

    if(q.type == 'choose'){
        $('#templates [name="mw-question-choose"]').clone().appendTo(this);
        this.find('[name="name"]').text(q.name);
        for(var i in q.plain){
            var qname = q.plain[i];
            this.find('[name="choice"]:first') // clone choices and fill 
                .clone()
                .text(qname)
                .data('name', qname)
                .appendTo(this.find('[name="choices"]'))
                .addClass((olddata.indexOf(qname) >= 0)?'active':'')
                .on('click', function(){
                    $(this).toggleClass('active');
                })
            ;
        }
        this.find('[name="choice"]:first').remove();
    } else if(q.type == 'range'){
        this.text('range');
    }

    return this;
}
//////////////////////////////////////////////////////////////////////////////
});
