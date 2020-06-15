import sys
from os.path import abspath as abspath
from os.path import dirname as dirname

from datetime import datetime

from flask import current_app, request

from flask_login import UserMixin
from flask_login import current_user

from . import db
from web import db

module_path = abspath(dirname(__file__)) # /home/pi/Dev/home_alarm/src/web
src         = dirname(module_path)       # /home/pi/Dev/home_alarm/src
sys.path.append(src)
from utils.util_request_ip import get_ip

class User(db.Model, UserMixin):
    __bind_key__ = 'users'
    id = db.Column(db.Integer, primary_key=True) # primary keys are required by SQLAlchemy
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))
    
    def __repr__(self):
        return '<User {0} {1} {2} {3}>'.format(self.id, self.email, self.name, self.password)
        
    @classmethod
    def last(self, cls):
        return(db.session.query(cls).order_by(cls.id.desc()).first())
        
    @classmethod
    def all(self, cls):
        return(db.session.query(cls).order_by(cls.id.desc()).all())
    
    @classmethod
    def get_by_name(self, cls, name):
        return db.session.query(cls).filter_by(name=name).first()
    
class DBLog(db.Model):
    __bind_key__ = 'logs'
    id      = db.Column(db.Integer, primary_key=True) # primary keys are required by SQLAlchemy
    dt      = db.Column(db.DateTime)
    user    = db.Column(db.String(20))
    ip      = db.Column(db.String(30))
    scope   = db.Column(db.String(20))
    badge   = db.Column(db.String(20))
    subject = db.Column(db.String(20))
    message = db.Column(db.String(100))
    detail  = db.Column(db.String(100))
    
    def __repr__(self):
        return '<DBLog {0} {1} {2} {3} {4} {5} {6} {7} {8}>'.format(self.id, self.dt, self.ip, self.user, self.scope, self.badge, self.subject, self.message, self.detail)
    
    # new_user = User(email=email, name=name, password=generate_password_hash(password, method='sha256'))

    @classmethod
    def new(self, ip="", user="", scope="", badge="", subject="", message="", detail=""):
        """Create log entry
        ip      retrieved from utils.util_request_ip (LAN/WAN)
        user    flask_login.current_user
        
        scope   [ nox | ext | None ]
        
        subject [ command | login | event ]
        
        badge   [ primary | danger | success ] -> color applied to message
        
        message depends on the subject
            subject login   [ success | logout | failed ]
            subject command [ start_alarm | stop_alarm ]
            subject event [ start | stop  | detection | serene_stop ]
        
        detail custom text
        """
        try:
            dt = datetime.now()
            if ip == "":
                ip = get_ip(current_app, request)
            
            if user == "":
                if (current_user.is_authenticated is True): 
                    user = current_user.name
                else:
                    user = "-"
            
            log = DBLog(dt=dt, ip=ip, user=user, scope=scope, badge=badge, subject=subject, message=message, detail=detail)
            db.session.add(log)
            db.session.commit()
        except:
            current_app.logger.exception("Error creating log")
            return False
        else:
            current_app.logger.debug('{0!r}'.format(log))
            # '{0!s} {0!r}'.format(Data())
            return True
    
    @classmethod
    def last(self, cls):
        return(db.session.query(cls).order_by(cls.id.desc()).first())
        
    # @classmethod
    # def all(self):
        # return(db.session.query(DBLog) \
                # .order_by(DBLog.id.desc()) \
                # .all())
    
    @classmethod
    def all(self, limit=None, scope=None, subject=None):
        """ Build a query to filter records
        If no parameters given: return all records
        scope shall be a string [ 'nox' | 'ext' ]
        subject can be string or list of values
        """
        query = db.session.query(DBLog) \
                          .order_by(DBLog.id.desc())
        if scope:
            query = query.filter(DBLog.scope == scope)
        if subject:
            if type(subject) == str:  query = query.filter(DBLog.subject == subject)
            if type(subject) == list: query = query.filter(DBLog.subject.in_(subject))
        if limit:
            query = query.limit(limit)
        return(query.all())
    
    @classmethod
    def logins(self):
        return(db.session.query(DBLog) \
                .filter(DBLog.subject == "login") \
                .order_by(DBLog.id.desc()) \
                .all())
    
    @classmethod
    def events(self):
        return(db.session.query(DBLog) \
                .filter(DBLog.subject == "event") \
                .order_by(DBLog.id.desc()) \
                .all())
    
    @classmethod
    def commands(self, limit=None, scope=None):
        query = db.session.query(DBLog) \
            .filter(DBLog.subject == "command") \
            .order_by(DBLog.id.desc())
        if scope:
            query = query.filter(DBLog.scope == scope)
        if limit:
            query = query.limit(limit)
        return(query.all())
        
    @classmethod
    def get_by_subject(self, cls, name):
        return db.session.query(cls).filter_by(name=name).first()
        