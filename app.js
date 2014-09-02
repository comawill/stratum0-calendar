(function($) {

	"use strict";
	var options = {
		events_source: 'events.json',
		view: 'month',
		modal: '#events-modal',
		tmpl_path: 'tmpls/',
		tmpl_cache: false,
		language: 'de-DE',
		onAfterViewLoad: function(view) {
			$('.page-header h3').text(this.getTitle());
			$('.btn-group button').removeClass('active');
			$('button[data-calendar-view="' + view + '"]').addClass('active');
		},
		classes: {
			months: {
				general: 'label'
			}
		},
		modal_title: function(event) { return event.title }
	};

	var calendar = $('#calendar').calendar(options);

	$('.btn-group button[data-calendar-nav]').each(function() {
		var $this = $(this);
		$this.click(function() {
			calendar.navigate($this.data('calendar-nav'));
		});
	});

	$('.btn-group button[data-calendar-view]').each(function() {
		var $this = $(this);
		$this.click(function() {
			calendar.view($this.data('calendar-view'));
		});
	});

}(jQuery));

function enhance_event(event) {
	data = event.split(": ", 2);
	return data[0] + ": <strong>" + data[1] + "</strong>"
}