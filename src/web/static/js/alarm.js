/*
Class Alarm used to manage
- buttonevents and display,
- badges (alarm state) display
- events log (tr in table)


An alarm instance creates a socketio instance
*/

class Alarm {
	constructor(name, states, command_ack_delay) {
		this.name 				 		   = name;
		this.states						   = states
		this.command_ack_delay 	 = command_ack_delay;
		this.command_in_progress = false; // Change the behaviour of socket.on('alarmstate') when command was sent
		this.current_state 	     = "";
		this.btn_start_alarm 		 = "#btn_start_alarm_" + name
		this.btn_stop_alarm  		 = "#btn_stop_alarm_" + name
		this.btn_start_alarm_spinner 	= "#btn_start_alarm_spinner_" + name
		this.btn_stop_alarm_spinner		= "#btn_stop_alarm_spinner_" + name
		// http:// replaced by // to make it workin with https/ssl 
		this.socket = io.connect('//' + document.domain + ':' + location.port + '/'+name+'alarm');
		this.hide_badges_on_load()
	}

	/*
	----- Buttons Events -----
	*/
	on_click_btn_start_alarm() {
		$(this.btn_start_alarm).prop("disabled", true);
		$(this.btn_start_alarm_spinner).show();
		this.command_in_progress = true;
		this.launch_timer_command_ack();
	};
	on_click_btn_stop_alarm() {
		$(this.btn_stop_alarm).prop("disabled", true);
		$(this.btn_stop_alarm_spinner).show();
		this.command_in_progress = true;
		this.launch_timer_command_ack();
	};

	/*
	----- Badges (state) Display -----
	*/
	// Update badge when new state is received from socketio (on, off, ...)
	alarm_update_state_badges_display(state) {
		// Hide all state bades
		name = this.name
		this.states.forEach(function(item){
			var badge_div_id = '#div_alarm_state' + '_' + item +'_' + name
			$(badge_div_id).hide();
		});
		// Show the current state badge
		var badge_div_id = '#div_alarm_state'+'_'+ state +'_' + name
		$(badge_div_id).show();
	}

	// Hide the badges when pag is loaded first time
	// A fresh state will be visible on event from socketio
	hide_badges_on_load() {
		name = this.name
		this.states.forEach(function(item){
			var div_id = '#div_alarm_state'+'_'+item +'_' + name
			$(div_id).hide();
		});
    }

	/*
	----- Button Display -----
	*/
	// Called each time a state is received to disable useless buttons / enable required buttons / hide spinner
	enable_disable_start_stop_buttons(state) {
		if (state == 'off'){
			$(this.btn_start_alarm).show();
			$(this.btn_start_alarm).prop("disabled", false);
			$(this.btn_start_alarm_spinner).hide();
			$(this.btn_stop_alarm).hide();
		}
		else {
			$(this.btn_start_alarm).hide();
			$(this.btn_stop_alarm).show();
			$(this.btn_stop_alarm).prop("disabled", false);
			$(this.btn_stop_alarm_spinner).hide();
		}
	}

	/* ----- Process alarm state update received from socketio -----
	When a state update is received,
	If a command to change the state was lanched (before timeout) and a new/different state is received
	Or If no command was trigered (eg alarm is doing on -> detection)
	Then update the state display and update button display
	*/
	on_receive_alarmstate(msg) {
		console.log(this.name + " Received state " + msg.state);
	if ((this.command_in_progress === true
		&& this.current_state != msg.state )
		|| (this.command_in_progress === false))
		{
			this.current_state = msg.state 						// Update variable saving the current state
			this.alarm_update_state_badges_display(msg.state); 	// Update state display
			this.enable_disable_start_stop_buttons(msg.state);	// Update button display
				if (this.command_in_progress === true) {			// Acknoledge the new state
					this.command_in_progress = false
				}
		}
	};


	// ----- Usage of timeout for command Ack -----
	// Launch timer when a command is triggered
	// During the timer, a spinner is displayed and button is disabled,
	// If the command is acknoledged (new/different state is received)
	// Or if the timeout is reached,
	// Then the spinner is removed and button re-enabled.
	launch_timer_command_ack() {
		this.timeout_command_ack = window.setTimeout(function(){ this.command_in_progress = false;}, this.command_ack_delay);
	}
	// Clear timer when command ack is received
	clear_timer_command_ack() { window.clearTimeout(this.timeout_command_ack); }
}


$(document).ready(function(){
	var timer_command_ack_delay = 5*1000;	// timeout delay

	var states = ['init' , 'off'     , 'on'      , 'alert'     , 'was_alert'  ];
	var colors = ['info' , 'success' , 'primary' , 'warning'   , 'warning'    ];
	var events = ['init' , 'stop'    , 'start'   , 'detection' , 'serene_stop'];

	/* ----- OnClick Buttons Events -----
	When a button is clicked: disable it and show a spinner
	Record that a comand is in progress (stop processing state update unless a new/different state is received)
	Launch a timer to eventually stop the spinner and re-enable the button if no different state is received after a timeout
	"new/different" state to be understood as "command ack"
	*/
	if((typeof config_panel_ext !== 'undefined') && (config_panel_ext == "true")) {
		console.log("config_panel_ext " + config_panel_ext);

		// Create an instance of class Alarm()
		ext = new Alarm("ext", states, timer_command_ack_delay);

		// Button Command STOP ExtAlarm is clicked
		$("#btn_start_alarm_ext").on("click", function(){
			ext.on_click_btn_start_alarm();
			ext.socket.emit('command_alarm', {value: 'start_alarm'});
		});
		// Button Command START ExtAlarm is clicked
		$("#btn_stop_alarm_ext").on("click", function(){
			ext.on_click_btn_stop_alarm();
			ext.socket.emit('command_alarm', {value: 'stop_alarm'});
		});

		// Receive Extalarm state from server
	  ext.socket.on('extalarmstate', function(msg) {
	      ext.on_receive_alarmstate(msg)
	  });
		// Receive ExtAlarm Events from webserver via socketio. Add new event to table log
		ext.socket.on('extalarmevent', function(msg) {
			console.log("Received extalarmevent " + msg.alarm_event);
			add_event_to_table('#div_alarm_events_ext', msg);
		});
	}

	if((typeof config_panel_nox !== 'undefined') && (config_panel_nox == "true")) {
		console.log("config_panel_nox " + config_panel_nox);
		// Create an instance of class Alarm()
		nox = new Alarm("nox", states, timer_command_ack_delay);

		// Button Command STOP NoxAlarm is clicked
		$("#btn_start_alarm_nox").on("click", function(){
			nox.on_click_btn_start_alarm();
			nox.socket.emit('command_alarm', {value: 'start_alarm'});
		});
		// Button Command START NoxAlarm is clicked
		$("#btn_stop_alarm_nox").on("click", function(){
			nox.on_click_btn_stop_alarm();
			nox.socket.emit('command_alarm', {value: 'stop_alarm'});
		});
		// Receive Noxalarm state from server
    nox.socket.on('noxalarmstate', function(msg) {
        nox.on_receive_alarmstate(msg)
    });
		// Receive NoxAlarm Events from webserver via socketio. Add new event to table log
		nox.socket.on('noxalarmevent', function(msg) {
			console.log("Received noxalarmevent " + msg.alarm_event);
			add_event_to_table('#div_alarm_events_nox', msg)
		});
	}
	



	/* Add a tr (event) to table
	<tr>
		<td>user</td>
		<td>date</td>
		<td><span class="badge badge-success">Event</span></td>
	</tr>
	*/
	function add_event_to_table(table_div, msg) {
		event_index = events.indexOf(msg.alarm_event);
		badge_class_color = colors[event_index];
		badge_class_base = 'badge badge-';
		badge_class = badge_class_base + badge_class_color;

		new_tr_element = '<tr><td>'+ msg.user +'</td><td>'+ msg.date +'</td>'
		new_tr_element += '<td><span class="'+ badge_class +'">'+msg.alarm_event+'</span></td>'

		tbody = $(table_div).html();
		$(table_div).html(new_tr_element + tbody);
    }


	// DEAD CODE
	/*
	ext.socket.on('generic_event', function(msg) {
        // console.log("Received extalarmevent" + msg.alarm_event);
		// Create new <tr> element with color from Array "colors" and content from msg.alarm_event
		event_index = events.indexOf(msg.alarm_event);
		badge_class_base = 'badge badge-';
		badge_class_color = colors[event_index];
		badge_class = badge_class_base + badge_class_color;

		new_tr_element = '<tr><td>'+ msg.user +'</td><td>'+ msg.date +'</td>'
		new_tr_element += '<td><span class="'+ badge_class +'">'+msg.alarm_event+'</span></td>'

		// maintain a list of N events (<tr> elements)
        if (extevents_received.length >= 10){
            extevents_received.pop()
        }
        extevents_received.unshift(new_tr_element);
        extevents_html = '';
        for (var i = 0; i < extevents_received.length; i++){
            extevents_html = extevents_html + extevents_received[i];
        }
		//replace the content of <ul> with the N <tr> elements
        $('#div_alarm_events_ext').html(extevents_html);
    });
*/
});
