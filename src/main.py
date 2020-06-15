# -*- coding: utf-8 -*-
"""
Running socketio 
    basic call: socketio.run(app, host="0.0.0.0")
    more info, see: https://flask-socketio.readthedocs.io/en/latest/
To run gunicorn with eventlet
    gunicorn --worker-class eventlet -w 1 main:app
To run gunicorn with gevent
    gunicorn -k gevent -w 1 main:app
"""

from web import create_app, socketio    

app = create_app()

def run():
    app.logger.warning('Running mode %s %s:%s' % (app.config['ENV'], app.config['HOST'], app.config['PORT']))
    socketio.run(app, host=app.config['HOST'], port=app.config['PORT'])

if __name__ == '__main__':
    run()
