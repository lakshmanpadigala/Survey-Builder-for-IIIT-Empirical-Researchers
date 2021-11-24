from flask import Flask, request, render_template,jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_manager, login_user, logout_user, login_required, UserMixin,current_user
from Models import User,FormStructure,UserResponses

@login_manager.user_loader
def load_user(user_id):
    '''For Loading User'''
    return User.query.get(int(user_id))
    
@app.route('/login',methods = ['POST'])
def login():
    '''Route for Login User'''
    data = request.get_json()
    uname = data['uname']
    psw  = data['psw']
    check_user = User.query.filter_by(username = uname).first()
    if(check_user is not None):
        if(check_user.password == psw):
            login_user(check_user)
            print(current_user.username)
            return redirect(url_for('dashboard'))
        else:
            return redirect(url_for('login'))#wrong psw
    else:
        return redirect(url_for('login'))#no user exists

@app.route('/signup',methods = ['POST'])
def signup():
    '''Route for signup of User'''
    if(request.method == 'POST'):
        data = request.get_json()
        uname = data['uname']
        psw  = data['psw']
        check_user = User.query.filter_by(username = uname).first()
        if(check_user is not None):
            redirect(url_for('login'))#Username already Exists!
        else:
            user = User(username = uname,password = psw,isChef = False)
            db.session.add(user)
            db.session.commit()
            redirect(url_for('login'))

@app.route('/logout',methods=['GET'])
@login_required
def signout():
    '''Route for logout of User'''
    logout_user()
    return "Logged Out Successful!"