# Software

## Alarm Process

<div class="mermaid">
graph LR
	on        		--> off
	alarm_detection --> off
	was_alarm 		--> off
	on        		--> alarm_detection
	alarm_detection --> was_alarm
</div>

## Sockets

Interaction between multiple tasks using sockets (socketio and ZMQ):

- Flask using socketio to async update web page and receive button actions from the user
- Thread acting as a gateway between flask and Alarm process
- Alarm process (while loop running a statemachine)
- Unipi IO

<div class="mermaid">
sequenceDiagram
	participant 1 as Web Browser
	participant 2 as Flask App
	participant 3 as Thread Gateway
	participant 4 as Alarm Process
	participant 5 as Unipi I/O

	Note over 1, 5: Command (button from web browser)
	1 -->> 2: socketio command_alarm
	2 -->> 3: set Flag start/stop
	3 -->> 4: ZMQ TOPIC_REQUEST (START/STOP)
	4 -->> 5: Evok API (write output)
	5 -->> 4: Evok API (read input)
	4 -->> 3: ZMQ EVENT (start/stop/detection/...)
	3 -->> 1: socketio emit event

	Note over 1, 5: Web page is loaded
	1 -->> 2: socketio connect
	2 -->> 3: set Flag "request status"
	3 -->> 4: ZMQ TOPIC_REQUEST (STATUS_UPDATE)
	4 -->> 3: ZMQ STATE (start/stop/detection/...)
	3 -->> 1: socketio emit state

	Note over 1, 5: Alarm state change
	5 -->> 4: Evok API (read input)
	4 -->> 3: ZMQ STATE
	3 -->> 1: socketio emit state
</div>
