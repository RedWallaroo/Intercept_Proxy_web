var prev_data = null;

function load_data() {
	//load data from /data. optionally providing a query
	//parameter read from the #format select

    //var format = $('select#format option:selected')[0].value;
    //var url = '/data' + (format ? "?format=" + format : "")

    var url = '/data'
    $.ajax({ url:     url,
             success: function(data) {
             	          display_data(data);
             	          wait_for_update();},
         });
    return true;

}

function wait_for_update() {
   // Uses separate update notification and data providing URls. Could
   // be combined, but if they are separated, the Python routine that
   // provides data needn't be changed from what's required for standard,
   // non-long polling web app.
    var url = '/updated'
    $.ajax({ type: "POST",
             url:     url,
             success: load_data,
             complete: wait_for_update,
             timeout: 60000,
         });
}

function check_for_update(){
    console.log("inside check_for_update")
    var url = '/update'
    $.ajax({ type: "POST",
             url:     url,
             success: function(data) {
                       console.log("success from check_for_update ajax", data);
                       display_data(data);},
            //complete: check_for_update,
             //timeout: 50000,
         });
}

function start() {
    console.log("inside start")
    var url = '/start'
    $.ajax({ type: "POST",
             url:     url,
             success: function(data) {
                        console.log("success from start ajax", data);
                        display_data(data);
                        check_for_update();},
         });
}

function stop() {
    console.log("inside stop")
    var url = '/stop'
    $.ajax({ type: "POST",
             url:     url,
             success: function(data) {
                        console.log("success from stop ajax", data)
                        display_data(data)},
         });
}

function forward() {
    console.log("inside forward")
    var url = '/forward'
    $.ajax({ type: "POST",
             url:     url,
             success: function(data) {
                        console.log("success from forward ajax", data)
                        display_data(data)},
         });
}

function drop() {
    console.log("inside drop")
    var url = '/drop'
    $.ajax({ type: "POST",
             url:     url,
             success: function(data) {
                        console.log("success from drop ajax", data)
                        display_data(data)},
         });
}

function display_data(data) {
	// show the data acquired by load_data()
    console.log("inside of display_data")
	if (data) { // if there is data, and it's changed
        // update the contents of several HTML elements via JQuery
        console.log(data)


      //if (data.status){
      if (data.indexOf("status:") === 0){

        switch(data)
        {
          case "status: listening on socket":
             $("#intercept_btn").val('Turn Intercept OFF');
             break;
          case "status: listener socket closed":
             $("#intercept_btn").val('Turn Intercept ON');
             break;
          default:
             break;
        }

        $("#search_box").val(data);
        check_for_update();
      }

      //if (data.data) {
      if (data.indexOf("data:") === 0){
           data = data.replace("data:","")
           $("#raw_request").val(data);
           // remember this data, in case we want to compare it to the next update
           prev_data = data;
      }


      //if (data.empty) {
      if (data.indexOf("empty:") === 0){
        //setTimeout(check_for_update(), 5000)
        check_for_update();
      }
           //$("#request_bar").val(data.request_bar);
        //$("#raw_request").val(data.raw_request);



        // a little UI sparkle - show the #updated div, then after a little while,
        // fade it away.
        //$("#updated"). fadeIn('fast');
        //setTimeout(function() { $("#updated").fadeOut('slow'); }, 2500);
	}
}

$(document).ready(function() {
	// initial document setup - hide the #updated message, and provide a
	// 'loading' message
	//$("div#updated").fadeOut(0);
	//$("div#contents").append("awaiting data...");
	//When page loads...

    console.log("inside document ready")
    //On Click Event - Intercept button
    $("#intercept").submit(function() {
        if ($("#intercept_btn").val() == 'Turn Intercept ON') {
           start();
           console.log("start was called")
        } else if ($("#intercept_btn").val() == 'Turn Intercept OFF') {
           stop();
           console.log("stop was called")
        }
        return false;
    });

    //On Click Event - Forward button
    $("#Forward_btn").click(function() {
        console.log("forward button clicked")
        $("#raw_request").val("");
        forward();
        return false;
    });

    //On Click Event - Drop button
    $("#Drop_btn").click(function() {
    console.log("drop button clicked")
    drop();
    return false;
    });

	// load initial data ( assuming it will be immediately available)
	//load_data();
	 // wait_for_update(); otherwise
});



//$(document).ajaxStop(function(){
    //console.log("inside ajaxstop")
    //setTimeout(20)
//});