(function($){               
    $(document).ready(function(){                   
        $('#id_no_record').change(function() {
           $('#id_player1').val('');
           $('#id_player2 option').remove();
           $('#id_player2').html($('#id_player1').html());
        });
        $('#id_player1').change(function() {
            $('#id_player2 option').remove();
            var c_id = $('#id_player1 option:selected').val();
        	
            if (!$('#id_no_record').is(':checked')) {
                $('#id_player2').append('<option value selected="selected">---------</option>');
                
                date = $('#id_end_datetime_0').val();
                $.getJSON(FORCE_SCRIPT_NAME + "/leagues/"+ $('#id_league').val() +"/competitors/"+c_id+"/opponents?date="+date,
                    function(data){
                        //alert(data);
                        if (data["HTTPRESPONSE"] == 1)
                        {   
                            data = data['data']
                            for (i = 0; i < data.length; i++) {
                                $('#id_player2').append('<option value="' + data[i].id + '">' + data[i].name + '</option>');
                            }
                        }
                });
            } else {
                $('#id_player2').html($('#id_player1').html());
                $('#id_player2').val('');
                $('#id_player2 [value=' + c_id + ']').remove();
            }
        });
    })          
})(django.jQuery);
