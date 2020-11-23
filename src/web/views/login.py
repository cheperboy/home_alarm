from flask import Blueprint, session, redirect, url_for, render_template, request, current_app
from flask_wtf import Form
from wtforms.fields import StringField, PasswordField, SubmitField
from wtforms.validators import Required

from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import current_user, login_user, logout_user, login_required

from ..models import User, DBLog
from .. import db

login = Blueprint('login', __name__)

class LoginForm(Form):
    """Accepts a nickname and a room."""
    name        = StringField('Name', validators=[Required()])
    password    = PasswordField('Password', validators=[Required()])
    submit      = SubmitField('login')

@login.route('/login', methods=['GET', 'POST'])
def index():
    # name     = form.name.data
    # password = request.form.get('password')
    form = LoginForm()
    if form.validate_on_submit():
        current_app.logger.debug('form valid')
        user = User.get_by_name(User, form.name.data)
        if not user :
            # flash('No user in database', 'warning')
            detail="wrong user " + form.name.data
            current_app.logger.info(detail)
            DBLog.new(badge="danger", subject="login", message="failed", detail=detail, ip=request.remote_addr)
            return redirect(url_for('login.index'))
        if not check_password_hash(user.password, form.password.data):
            # flash('Wrong password', 'warning')
            detail = "wrong password"
            current_app.logger.info(detail)
            DBLog.new(badge="danger", subject="login", message="failed", user=str(user.name), detail=detail, ip=request.remote_addr)
            # app.logger.info('logging failed : Wrong password')
            return redirect(url_for('login.index'))

        # username & pasword are correct: login and write DBLog
        login_user(user)
        current_app.logger.info('login succes %s' % (user.name))
        DBLog.new(badge="success", subject="login", message="success", ip=request.remote_addr)
        # session['name'] = form.name.data
        return redirect(url_for('panel.index'))
    elif request.method == 'GET':
        current_app.logger.debug('loading form')
        form.name.data = session.get('name', '')
    return render_template('login.html.j2', form=form)

@login.route('/logout', methods=['GET', 'POST'])
def logout():
    current_app.logger.info('logout %s' % (current_user.name))
    DBLog.new(badge="primary", subject="login", message="logout", ip=request.remote_addr)
    logout_user()
    return redirect(url_for('panel.index'))
