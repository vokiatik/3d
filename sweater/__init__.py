from dash import Dash
from dash import html

from flask import Flask

from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_admin import Admin
from flask_user import UserManager
from flask_admin.contrib.sqla import ModelView
from werkzeug.security import generate_password_hash

server = Flask(__name__)
dash_app = Dash(__name__, server=server, url_base_pathname='/dashboard/')
dash_app.layout = html.Div([html.H1('Dash page')])

server.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:1q2w3e4r5t@localhost:5432/3d'
server.config['MAX_CONTENT_LENGTH'] = 1024 * 1024 * 1024
server.secret_key = 'verylongsecret_keysecuritysupersecure'
server.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
server.config['USER_ENABLE_EMAIL'] = False
server.config['USER_LOGIN_URL'] = '/login'
db = SQLAlchemy(server)
admin = Admin(server)

login_manager = LoginManager(server)


from sweater import routes, models
from sweater.models import User, Control, Model, Role, UserRoles


user_manager = UserManager(server, db, User)
user_manager.login_manager = login_manager

USER_APP_NAME = "Flask-User QuickStart App"
USER_ENABLE_EMAIL = False
USER_ENABLE_USERNAME = True
USER_REQUIRE_RETYPE_PASSWORD = False


admin.add_view(Control(User, db.session))
admin.add_view(Control(Role, db.session))
admin.add_view(Control(Model, db.session))

'''
db.drop_all()
db.create_all()

admin_role = Role(name='Admin')
sub_role = Role(name='Subscriber')
db.session.add(sub_role)
db.session.add(admin_role)
db.session.commit()

user1 = User(
    username='admin', email='admin@example.com', active=True,
    password=generate_password_hash('password'))
user1.roles = [admin_role, sub_role]
#admin.roles = [admin_role, sub_role]
db.session.add(user1)
db.session.commit()
'''

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)
