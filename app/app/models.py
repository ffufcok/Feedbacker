from datetime import datetime
from app import db, login
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    executor = db.Column(db.Integer) # идентификатор того, кто обрабатывает
    text = db.Column(db.String(300))
    is_done = db.Column(db.Boolean, default=False)
    answer = db.Column(db.String(300))
    user_id = db.Column(db.Integer)
    _group = db.Column(db.Integer)


    date_create = db.Column(db.DateTime, default=db.func.now())
    def done(self):
        self.is_done = True

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    lastname = db.Column(db.String(64), index=True, unique=True)
    firstname = db.Column(db.String(64), index=True, unique=True)
    _group = db.Column(db.Integer)
    queue = db.Column(db.Integer)

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


@login.user_loader
def load_user(id):
    return User.query.get(int(id))