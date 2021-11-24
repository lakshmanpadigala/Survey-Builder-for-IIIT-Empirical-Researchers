from flask import Flask, request, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_manager, login_user, logout_user, login_required, UserMixin,current_user
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin,db.Model):
    id = db.Column(db.Integer,primary_key=True)
    username = db.Column(db.String(20),unique = True,nullable=False)
    password = db.Column(db.String(10),nullable = False)
    forms = db.relationship('FormStructure',backref = 'creator',lazy = 'dynamic')

class FormStructure(db.Model):
    id = db.Column(db.Integer,primary_key = True)
    formName = db.Column(db.String(20),nullable=False)
    description = db.Column(db.Text)
    dateCreated = db.Column(db.DateTime,nullable=False,default = datetime.utcnow)
    formJson = db.Column(db.PickleType,nullable = False)
    owner_id = db.Column(db.Integer,db.ForeignKey('user.id'))#creator
    responses = db.relationship('UserResponses',backref = 'formId')

class UserResponses(db.Model):
    id = db.Column(db.Integer,primary_key = True)
    form_id = db.Column(db.Integer,db.ForeignKey('formstructure.id'))#formID 
    responseObject = db.Column(db.PickleType,nullable = False)
    responseTime = db.Column(db.DateTime,nullable=False,default = datetime.utcnow)
