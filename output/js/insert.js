function validateEmail(email) {
    var re = /^(([^<>()[\]\\.,;:\s@"]+(\.[^<>()[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
return re.test(email);
}

$("document").ready(function(){
	  $("#subscribe").submit(function(){
		    var data = {
			      "email": $('#email').val()
		    };

		    $.ajax({
			      type: "POST",
			      dataType: "json",
			      url: "insert.php", //Relative or absolute path to response.php file
			      data: data,
			      encode: true,
			      success: function(data) {
				        $('#email').val("");
				        alert(data["msg"]);
			      },
			      error: function(xhr, status, error) {
			          var err = eval("(" + xhr.responseText + ")");
			          alert(err.Message);
			      }
		    });

	      return false;

	  });
});
