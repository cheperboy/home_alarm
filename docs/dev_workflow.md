# Developpement stuff

## Virtualenv

Activate virtualenv `workon dev`.  
To run Developement server `(dev) pi@alarm:~/Dev/home_alarm/src $ python main.py`

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

