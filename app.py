from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm 
from wtforms import StringField, PasswordField, BooleanField, IntegerField
from wtforms.validators import InputRequired, Email, Length
from flask_sqlalchemy  import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import sqlite3
import arrow
import google_maps
from datetime import timedelta
from datetime import datetime
from datetime import date

app = Flask(__name__)
app.config['SECRET_KEY'] = 'Thisissupposedtobesecret!'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////home/kiquance/building_user_login_system-master/finish/database.db'
bootstrap = Bootstrap(app)
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin, db.Model):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(15),unique=True)
	email = db.Column(db.String(50),unique=True)
	password = db.Column(db.String(80))
	contact = db.Column(db.String(10),unique=True)
	address = db.Column(db.String(30),unique=True)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class LoginForm(FlaskForm):
    username = StringField('username', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=8, max=80)])
    remember = BooleanField('remember me')

class RegisterForm(FlaskForm):
    email = StringField('email', validators=[InputRequired(), Email(message='Invalid email'), Length(max=50)])
    username = StringField('username', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=8, max=80)])
    contact = StringField('username', validators=[InputRequired(), Length(min=10)])
    address = StringField('username', validators=[InputRequired(), Length(min=0, max=30)])
	
class DaysForm(FlaskForm):
    days = IntegerField('days', validators=[InputRequired(), Length(min=1)])

class addorderForm(FlaskForm):
    order_name=StringField('ordername', validators=[InputRequired(), Length(min=1, max=30)])    
    seller_address = StringField('seller_address', validators=[InputRequired(), Length(min=1, max=30)])
    user_address = StringField('user_address', validators=[InputRequired(), Length(min=1, max=30)])

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/addorder', methods=['GET', 'POST'])
def addorder():
    form=addorderForm()
    #name = form.username.data
    if request.method == 'POST':
        a=request.form.get('ordername')
        b=request.form.get('source_address')
        c=request.form.get('dest_address')
        eta = int(google_maps.main(b,c))
        current=datetime.now()

        current+=timedelta(hours=eta)
        eta=str(current)[0:10]
        conn = sqlite3.connect("database.db")
        cur = conn.cursor()

        cursor = cur.execute("insert into orders (order_name,user_id ,source_address, dest_address,est_delivery)values (\""+str(a)+"\",\""+str(current_user.id)+"\",\""+str(b)+"\" ,\""+str(c)+"\",\""+(eta)+"\")")
        # #orders3= cursor.fetchall()
        conn.commit()
        cursor.close()
        cur.close()
        conn.close()
        # return render_template('dashboard.html')
        return redirect(url_for('days'))
    return render_template('addorder.html',form=form)


@app.route('/estimate',methods=['GET','POST'])
def estimate():
    pass

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    ##name = form.username.data
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if check_password_hash(user.password, form.password.data):
                login_user(user, remember=form.remember.data)
                #conn = sqlite3.connect("database.db")
                #cur = conn.cursor()
                #cursor = cur.execute("SELECT * from orders where user_id="+ str(user.id))
                #orders1=cursor.fetchall()
                return redirect(url_for('days'))
        return '<h1>Invalid username or password</h1>'
        #return '<h1>' + form.username.data + ' ' + form.password.data + '</h1>'
    return render_template('login.html', form=form)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = RegisterForm()

    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data, method='sha256')
        new_user = User(username=form.username.data, email=form.email.data, password=hashed_password,contact = form.contact.data, address = form.address.data)
        db.session.add(new_user)
        db.session.commit()

        return '<h1>New user has been created!</h1>'
        #return '<h1>' + form.username.data + ' ' + form.email.data + ' ' + form.password.data + '</h1>'

    return render_template('signup.html', form=form)

	
@app.route('/days', methods=['GET', 'POST'])
def days():
    form= DaysForm()
    if request.method == 'POST':

        ab=request.form['text']
        conn = sqlite3.connect("database.db")
        cur = conn.cursor()
        cursor = cur.execute("select order_id, order_name, seller_id, user_id, source_address from orders where user_id="+str(current_user.id))
        orders1= cursor.fetchall()
        conn.commit()
        cursor.close()
        cur.close()
        conn.close()
        #conn.close
        #conn = sqlite3.connect("database.db")
        conn2 = sqlite3.connect("database.db")
        cur2 = conn2.cursor()
        #time=
        #a=str(ab) 
        tod=date.today()
        todstr=str(tod)
        ttt =  date.today()+timedelta(days=int(ab))

        tday =  str(ttt)
        
        
        
        cursor2 = cur2.execute("select order_id,order_name,est_delivery from orders where est_delivery <= \""+tday+"\" AND est_delivery > \""+todstr+"\" order by est_delivery asc")
        orders2=cursor2.fetchall()
        # print(tday)
        # print(orders2)
        #cursor.close()
        #del cursor
        #conn.close()
        return render_template("dashboard.html",orders1=orders1, orders2=orders2)
        
        #return redirect(url_for('dashboard'))
    #return redirect(url_for('days'))

    return render_template('days.html')
 



@app.route('/dashboard',methods=['GET','POST'])
@login_required
def dashboard():
    form1=addorderForm()
    if request.method == 'POST':
        return render_template('addorder.html',form=form1)
    else:
        return redirect(url_for('days'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
