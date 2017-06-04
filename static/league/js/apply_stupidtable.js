(function($){
    $(function(){
        $($('#leaguecompetitor_set-group table th')[2]).attr('data-sort', "float").attr('data-sort-default', "desc");
        $('#leaguecompetitor_set-group table').stupidtable();
        $($('#leaguecompetitor_set-group table th')[2]).click().click();
    });
})(django.jQuery);
