from flask import Flask, render_template,redirect, url_for
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import InputRequired, Email, Length
from forms.loginsys import LoginForm, RegisterForm
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_manager, login_user, login_required, logout_user, current_user
import config as cfg

import pandas as pd
import psycopg2
import psycopg2.extras as ex


app = Flask(__name__)
Bootstrap(app)

app.config['SECRET_KEY'] ='$SkillChen2022#'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:dba@localhost:5433/st'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# 加入登入管理
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class Webuser(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True)
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(120))
    enablekey = db.Column(db.String(1))

@login_manager.user_loader
def load_user(user_id):
    return Webuser.query.get(int(user_id))


# conn = psycopg2.connect(dbname=cfg.DB_NAME,user=cfg.DB_USER,password=cfg.DB_PASS,host=cfg.DB_HOST,port=cfg.DB_PORT)
# cur = conn.cursor(cursor_factory=ex.DictCursor)
# cur.execute("select * from ticker ")
# df = cur.fetchall()
# print(df)



@app.route("/")
def index():
    return render_template("index0.html")

@app.route('/login', methods=["GET","POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = Webuser.query.filter_by(username=form.username.data).first()
        if user:
            if check_password_hash(user.password, form.password.data):
                login_user(user, remember=form.remember.data)
                return redirect(url_for('dashboard'))
        return '<h1>Invalid username or password</h1>'                
        #return '<h1>' + form.username.data + ' ' + form.password.data + '</h1>'
    return render_template("login.html", form=form)

@app.route("/signup", methods=["GET","POST"])
def signup():
    form = RegisterForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data, method='sha256')
        new_user = Webuser(username=form.username.data,email=form.email.data,password=hashed_password,enablekey='N')
        db.session.add(new_user)
        db.session.commit()
        return '<h1>New User has been created!</h1>'
    return render_template("signup.html", form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))

@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html",webaccount=current_user.username)

@app.route("/orders")
@login_required
def orders():
    return render_template("orders.html")

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=3000)
