from enum import unique
from flask import Flask, request, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_manager, login_user, logout_user, login_required, UserMixin,current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo
import random
import requests
import lazy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/surveyBuilder'
app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'
s = requests.Session()
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)

class User(UserMixin,db.Model):
    id = db.Column(db.Integer,primary_key=True)
    username = db.Column(db.String(20),unique = True,nullable=False)
    password = db.Column(db.String(10),nullable = False)
    forms = db.relationship('FormStructure',backref = 'creator',lazy = 'dynamic')

class FormStructure(db.Model):
    id = db.Column(db.Integer,primary_key = True)
    formName = db.Column(db.String(20),nullable=False)
    description = db.Column(db.Text)
    dateCreated = db.Column(db.DateTime,nullable=False,default = datatime.utcnow)
    formJson = db.Column(db.PickleType,nullable = False)
    owner_id = db.Column(db.Integer,db.ForeignKey('user.id'))#creator
    responses = db.relationship('UserResponses',backref = 'formId')

class UserResponses(db.Model):
    id = db.Column(db.Integer,primary_key = True)
    form_id = db.Column(db.Integer,db.ForeignKey('formstructure.id'))#formID 
    responseObject = db.Column(db.PickleType,nullable = False)
    responseTime = db.Column(db.DateTime,nullable=False,default = datatime.utcnow)
