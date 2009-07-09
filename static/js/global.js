jQuery(window).load(function() {
	// Crazyweird fix lets us style abbr using CSS in IE - do NOT run onDomReady, must be onload
	document.createElement('abbr');
});

$.fn.wait = function(time, type) {
	time = time || 1000;
	type = type || 'fx';
	return this.queue(type, function() {
		var self = this;
		setTimeout(function() {
			$(self).dequeue();
		}, time);
	});
};

$(function() {
	$('#messages').wait(3000).slideUp('slow');

	$('.edit_status select').change(function(){
		edit_status = $(this).find('option:selected').val();
		if (edit_status == 'leave') {
			$(this).parents('tr').find('input,select').not('.edit_status select').attr('disabled', 'disabled');
			$(this).parents('tr').removeClass('remove');
		} else if (edit_status == 'change') {
			$(this).parents('tr').find('input,select').not('.edit_status select').removeAttr('disabled');
			$(this).parents('tr').removeClass('remove');
		} else if (edit_status == 'remove') {
			$(this).parents('tr').find('input,select').not('.edit_status select').attr('disabled', 'disabled');
			$(this).parents('tr').addClass('remove');
		}
	}).change();
});
