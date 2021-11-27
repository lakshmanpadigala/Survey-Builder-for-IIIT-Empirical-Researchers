from datetime import datetime
from flask import Flask, request, render_template,jsonify,redirect,url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_manager, login_user, logout_user, login_required, UserMixin,current_user


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:1406@localhost/ssd_proj'
app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

db = SQLAlchemy(app)

class User(UserMixin,db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer,primary_key=True)
    username = db.Column(db.String(20),unique = True,nullable=False)
    password = db.Column(db.String(10),nullable = False)
    forms = db.relationship('FormStructure',backref = 'creator',lazy = 'dynamic')

    def get_id(self):
        return self.id

class FormStructure(db.Model):
    __tablename__ = 'formstructure'
    id = db.Column(db.Integer,primary_key = True)
    formName = db.Column(db.String(20),nullable=False)
    description = db.Column(db.Text)
    dateCreated = db.Column(db.DateTime,nullable=False,default = datetime.utcnow)
    formJson = db.Column(db.PickleType,nullable = False)
    isActive = db.Column(db.Boolean,nullable = False)
    owner_id = db.Column(db.Integer,db.ForeignKey('user.id'))#creator
    responses = db.relationship('UserResponses',backref = 'formId',lazy = 'dynamic')

class UserResponses(db.Model):
    __tablename__ = 'userresponses'
    id = db.Column(db.Integer,primary_key = True)
    form_id = db.Column(db.Integer,db.ForeignKey('formstructure.id'),nullable=False)#formID 
    responseObject = db.Column(db.PickleType,nullable = False)
    responseTime = db.Column(db.DateTime,nullable=False,default = datetime.utcnow)



@login_manager.user_loader
def load_user(user_id):
    '''For Loading User'''
    return User.query.get(int(user_id))
    
@app.route('/login',methods = ['POST','GET'])
def login():
    '''Route for Login User'''
    data = request.get_json()
    uname = data['username']
    psw  = data['password']
    check_user = User.query.filter_by(username = uname).first()
    if(check_user is not None):
        if(check_user.password == psw):
            login_user(check_user)
            print(current_user.username)
            return "Login successful!"
            #return redirect(url_for('dashboard'))
        else:
            return redirect(url_for('login'))#wrong psw
    else:
        return redirect(url_for('login'))#no user exists

@app.route('/signup',methods = ['POST','POST'])
def signup():
    '''Route for signup of User'''
    if(request.method == 'POST'):
        data = request.get_json()
        uname = data['username']
        psw  = data['password']
        check_user = User.query.filter_by(username = uname).first()
        if(check_user is not None):
            #redirect(url_for('login'))
            return "Username already Exists!"
        else:
            user = User(username = uname,password = psw)
            db.session.add(user)
            db.session.commit()
            #redirect(url_for('login'))
            return "sign up successful!"

@app.route('/logout',methods=['GET','POST'])
@login_required
def signout():
    '''Route for logout of User'''
    logout_user()
    return "Logged Out Successful!"

@app.route('/dashboard',methods = ['GET'])
@login_required
def dashboard():
    if request.method == 'GET':
        data = FormStructure.query.filter_by(owner_id = current_user.id).all()
        prev_forms = {}
        count = 1
        for i in data:
            prev_forms[count] = {'formId':i.id,'formName':i.formName,'isActive':i.isActive,'date':i.dateCreated}
            count += 1
    return prev_forms

@app.route('/makeactive/<int:form_id>',methods = ['POST'])
@login_required
def make_active(form_id):
    data = FormStructure.query.filter_by(id = form_id).first()
    data.isActive = True
    db.session.commit()
    return "Active Done!"

@app.route('/makeinactive/<int:form_id>',methods = ['POST'])
@login_required
def make_inactive(form_id):
    data = FormStructure.query.filter_by(id = form_id).first()
    data.isActive = False
    db.session.commit()
    return "InActive Done!"

@app.route('/responses/<int:form_id>',methods = ['GET'])
@login_required
def responses(form_id):
    if request.method == 'GET':
        res = UserResponses.query.filter_by(form_id = form_id).all()
        responses_recieved = {}
        count = 1
        for i in res:
            responses_recieved[count] = {'responseTime':i.responseTime,'responseObject':i.responseObject}
            count += 1
        return responses_recieved

@app.route('/form',methods = ['POST'])
@login_required
def create_form():
    data = request.get_json()
    form_name = data['form_name']
    description = data['description']
    questions = data['questions']
    form = FormStructure(owner_id = current_user.id,isActive=True,formName = form_name,description = description,formJson = questions)
    db.session.add(form)
    db.session.commit()
    return "form created syccessfully!"

@app.route('/form/<form_id>',methods = ['GET','POST'])
def form_diplay(form_id):
    if request.method == 'GET':
        data = FormStructure.query.filter_by(id = form_id).first()
        if data.isActive == True :
            form = {}
            form[data.id] = {'isActive':True,'formname':data.formName,'description':data.description,'form':data.formJson}
            return form
        elif data.isActive==False :
            form = {}
            form[data.id] = {'isActive':False,'formname':data.formName,'description':"Form is not accepting Responses!"}
            return form
    if request.method == 'POST' :
        data = FormStructure.query.filter_by(id = form_id).first()
        if data.isActive == True :
            data = request.get_json()
            responseObject = data['responseObject']
            ur = UserResponses(form_id = form_id,responseObject = responseObject)
            db.session.add(ur)
            db.session.commit()
            return "Response Saved Successfully"
        elif data.isActive==False :
            return "Response Can't be Saved!"


if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)