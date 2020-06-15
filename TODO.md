# TODO

* Move static js in vendor directory. strategy to be defined:
	* use local vendor directory: available even if internet down
	* use cdn external provider: not available is network down

* Add email alert when soft error
* separate logger for 404, 500, 302
* Add log html viewer

* partial date formatting <td>{{ log.dt.strftime('%d/%m %H:%M') }}</td>
