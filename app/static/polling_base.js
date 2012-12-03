var prev_data = null;

function load_data() {
	//load data from /data. optionally providing a query
	//parameter read from the #format select

    var format = $('select#format option:selected')[0].value;
    var url = '/data' + (format ? "?format=" + format : "")

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

   $.ajax({ url: '/updated',
            success: load_data, //if /update signals results ready, load them
            complete: wait_for_update, // if the wait_for_update poll times out, rerun
            timeout: 60000,
        });
}

function display_data(data) {
	// show the data acquired by load_data()

	if (data && (data != prev_data)) { // if there is data, and it's changed
        // update the contents of several HTML divs via JQuery
        $('div#value').html(data.value);
        $('div#contents').html(data.contents);

        // remember this data, in case we want to compare it to the next update
        prev_data = data;

        // a little UI sparkle - show the #updated div, then after a little while,
        // fade it away.
        $("#updated"). fadeIn('fast');
        setTimeout(function() { $("#updated").fadeOut('slow'); }, 2500);
	}
}

$(document).ready(function() {
	// initial document setup - hide the #updated message, and provide a
	// 'loading' message

	$("div#updated").fadeOut(0);
	$("div#contents").append("awaiting data...");
	$("#search_box").val("Intercept is OFF");

	// load initial data ( assuming it will be immediately available)
	load_data();
	 // wait_for_update(); otherwise
});