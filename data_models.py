import ast
from datetime import datetime
from database import db


class User(db.Model):

    __tablename__ = 'USERS'
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    username = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    type = db.Column(db.Integer, nullable=False)


class Question(db.Model):

    __tablename__ = 'QUESTIONS'
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    text = db.Column(db.Text, nullable=False)
    state = db.Column(db.Integer, nullable=False)
    type = db.Column(db.Integer, nullable=False)
    required = db.Column(db.Integer, nullable=False)
    responses = db.Column(db.Text, nullable=False)
    survey_id = db.Column(db.Integer, nullable=False)
    def responsesList(self):
        return ast.literal_eval(self.responses)


class Survey(db.Model):

    __tablename__ = 'SURVEYS'
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.Text, nullable=False)
    state = db.Column(db.Integer, nullable=False)
    questions = db.Column(db.Text, nullable=False)
    uid = db.Column(db.Integer, db.ForeignKey('USERS.id'), nullable=False)
    access = db.Column(db.Integer,  nullable=False)
    create_time = db.Column(db.DateTime, nullable=False,
                            default=datetime.now())
    
    def questionsList(self):
        return ast.literal_eval(self.questions)


class Response(db.Model):

    __tablename__ = 'RESPONSES'
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    u_id = db.Column(db.Integer, db.ForeignKey(User.id), nullable=False)
    s_id = db.Column(db.Integer, db.ForeignKey(Survey.id), nullable=False)
    q_id = db.Column(db.Integer, db.ForeignKey(Question.id), nullable=False)
    text = db.Column(db.Text)
    num = db.Column(db.Integer)
    user = db.relationship(User)
    survey = db.relationship(Survey)
    question = db.relationship(Question)

    def responsesList(self):
        return ast.literal_eval(self.responses)
