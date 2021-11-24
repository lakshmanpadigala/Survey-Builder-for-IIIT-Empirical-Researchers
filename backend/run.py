from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/surveyBuilder'
app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'

login_manager = LoginManager()
bcrypt = Bcrypt(app)
login_manager.init_app(app)
login_manager.login_view = 'login'

import Routes

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)