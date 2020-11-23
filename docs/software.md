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


## Front-end

### badges state
les couleurs des badges du statut d'alarme (ON, OFF, ..) sont définit dans html
Exemple dans `_ext_panel.html.j2`
    <span id="div_alarm_state_on_ext" class="badge badge-primary">ON</span>

lorsque le front-end reçoit une mise à jour du `state` via zmq socket, un traitement javascript va masquer l'ensemble des badges `state` puis n'afficher que celui correspondant à l'état qui vient d'être reçu. 

### badges event
Les event servent uniquement à mettre à jours l'historique des event affichés dans la page web sans rechargement de la page.  
Lorsque la page est rechargée (ctrl+R) alors les event sont lus depuis la base de donnée.  
en cas de nouvel évennement, celui-ci on le push dans la page web (via zmq) et on l'enregistre également dans la base de donnée.  

Les couleurs des badges event enregistrés en base de donnée sont définit dans le fichier qui provoque l'écriture (`extAlarmProcess.py`).  
Les couleurs des badges event affichés en live (via zmq push) sont définit dans le fichier js fichier (`alarm.js`). Il faut conserver une cohérence entre ces deux fichier pour avoir un affichage cohérent.  

### Ext bind to nox
Le module d'alarme principal est 'nox'.  
Un module secondaire 'ext' peut être activé. `PANEL_EXT = True  # Activate Ext Alarm module`  
lorsque `ext` est activé, il doit être bindé au module `nox`, c'est-à-dire que l'alarme extérieure s'allume et s'éteint automatiquement en fonction de l'état on/off de l'alarme `nox`.   
pour avoir ce comportement, il faut positionner ce paramètre dans `src/extAlarmProcess.py`  
`BIND_TO_NOX = True # None / True. bind start/stop to NoxAlarm status. should be True in production.`
Un panel spécifique est prévu pour cette config, en faisant apparaitre que les log de `nox` et les évennements de détection de `ext` (mais pas le status on/waiton/off).
