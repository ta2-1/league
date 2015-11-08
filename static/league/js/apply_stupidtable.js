(function($){
    $(function(){
        $($('#leaguecompetitor_set-group table th')[1]).attr('data-sort', "float").attr('data-sort-default', "desc");
        $('#leaguecompetitor_set-group table').stupidtable();
        $($('#leaguecompetitor_set-group table th')[1]).click().click();
    });
})(django.jQuery);
