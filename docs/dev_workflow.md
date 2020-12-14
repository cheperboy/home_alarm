# Developpement stuff

## Virtualenv
virtualenv `dev` or `prod`  


## Dev / Debug
To activate virtualenv `workon dev`  
Go into dev directory `cd ~/Dev/home_alarm/src`  
To run front-end server `python main.py`  
To run back-end process `python extAlarmProcess.py`  
Check the debug flags in 
- `extAlarmProcess.py`
- `noxAlarmProcess.py`
- `config.py`


When running front-end this way, it uses the port defined in `config.py` (`PORT = 5000`)
When running front-end in production mode, it uses the default port 8000 (for internal gunicorn server) and 80 for external web server.


## Documentation

Mkdoc used to generate the wiki. Markdown files are stored in folder *doc/*.  Published to [https://alarm-wiki.readthedocs.io](https://alarm-wiki.readthedocs.io). Pushing repository to github will trigger ReadTheDocs build.

Can be updated on the web and pushed to github from [https://stackedit.io](https://stackedit.io).  
!!! warning ""
    Don't forget to `git pull` the local repository after editing online.


To test documentation on local server, run `mkdocs serve --dev-addr 0.0.0.0:8001`.  

Configuration file `mkdoc.yml`:
``` yaml
site_name: Alarm
theme: readthedocs
repo_url: https://github.com/cheperboy/home_alarm/
docs_dir: docs/
nav:
    - Home: index.md
    - Install Software: install_alarm.md
    - Software: software.md
...
```
The packages required for building the documentation are declared in  

- flask_app/requirements.txt for dev build
- docs/requirements.txt for readthedocs.io build

### Usefule extensions

- [pymdown](https://squidfunk.github.io/mkdocs-material/extensions/pymdown/)
- [mermaid plugin](https://github.com/pugong/mkdocs-mermaid-plugin)
- [pymdown-extensions](https://facelessuser.github.io/pymdown-extensions/extensions/arithmatex/)

# Github config

!!! warning ""
    Add `*secret*` and `*.pem` to .gitignore

