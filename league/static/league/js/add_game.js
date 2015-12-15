function setCookie(cname, cvalue) {
    var d = new Date();
    d.setTime(d.getTime() + (60*1000));
    var expires = "expires="+d.toUTCString();
    document.cookie = cname + "=" + cvalue + "; " + expires;
}

function getCookie(cname) {
    var name = cname + "=";
    var ca = document.cookie.split(';');
    for(var i=0; i<ca.length; i++) {
        var c = ca[i];
        while (c.charAt(0)==' ') c = c.substring(1);
        if (c.indexOf(name) == 0) return c.substring(name.length, c.length);
    }
    return "";
}


(function($){               
    $(document).ready(function(){
	var id_player1 = getCookie('id_player1');
	var id_player2 = getCookie('id_player2');
	var id_location = getCookie('id_location');
	if (id_player1 !== "" && id_player2 !== "") {
		$('#id_player1').val(id_player1);
		$('#id_player2').val(id_player2);
		$('#id_location').val(id_location);
	}
	$('#id_no_record').change(function() {
           $('#id_player1').val('');
           $('#id_player2 option').remove();
           $('#id_player2').html($('#id_player1').html());
        });
        $('#id_location').change(function() {
	    var l_id = $('#id_location option:selected').val();
	    setCookie('id_location', l_id);
	});
        $('#id_player1').change(function() {
            $('#id_player2 option').remove();
            var c_id = $('#id_player1 option:selected').val();
	    setCookie('id_player1', c_id);
        	
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

        $('#id_player2').change(function() {
	  var c_id = $('#id_player2 option:selected').val();
	  setCookie('id_player2', c_id);
	});
    })          
})(django.jQuery);
