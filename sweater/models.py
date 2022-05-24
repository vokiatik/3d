from flask import abort
from flask_user import UserMixin, current_user

from sweater import db
from flask_admin.contrib.sqla import ModelView


class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    active = db.Column('is_active', db.Boolean(), nullable=False, server_default='1')
    username = db.Column(db.String(255), nullable=False, unique=True)
    email = db.Column(db.String(255), nullable=False, unique=True)
    email_confirmed_at = db.Column(db.DateTime())
    password = db.Column(db.String(255), nullable=False, server_default='')
    roles = db.relationship('Role', secondary='user_roles')


# Define the Role data-model
class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(50), unique=True)

    def __str__(self):
        return self.name


# Define the UserRoles association table
class UserRoles(db.Model):
    __tablename__ = 'user_roles'
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey('users.id', ondelete='CASCADE'))
    role = db.Column(db.String(50), db.ForeignKey('roles.name', ondelete='CASCADE'))

    def __str__(self):
        return self.user_id, self.role


class Model(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), nullable=False)
    description = db.Column(db.String(1024))
    project = db.Column(db.String(32))


class Control(ModelView):
    def is_accessible(self):
        if current_user.has_roles('Admin'):
            return current_user.is_authenticated
        else:
            return abort(403)

    def not_auth(self):
        return 'Permission denied'
