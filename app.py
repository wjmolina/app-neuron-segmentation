import git

from datetime import datetime
from flask import Flask, render_template, request, flash, redirect, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'EsX_Team'

login_manager = LoginManager()
login_manager.init_app(app)

db = SQLAlchemy(app)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    datetime_created = db.Column(db.DateTime, default=datetime.utcnow)
    comments = db.relationship('Comment', back_populates='user')

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    comment = db.Column(db.String(200), nullable=False)
    datetime_created = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', back_populates='comments')

@app.route('/', methods=['GET', 'POST'])
@login_required
def index():
    if request.method == 'POST':
        if request.form['comment'] != '' and request.form['button'] == 'post_comment':
            db.session.add(Comment(
                user_id=current_user.id,
                comment=request.form['comment'],
            ))
            db.session.commit()
        elif request.form['button'] == 'logout':
            return redirect('/logout')
    return render_template(
        'index.html',
        comments=Comment.query.order_by(desc(Comment.datetime_created)).all()
    )

@login_manager.user_loader
def load_user(id):
    return User.query.filter_by(id=id).first()

@login_manager.unauthorized_handler
def unauthorized_callback():
    return redirect('/login')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/login')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect('/')
    if request.method == 'POST':
        if request.form['button'] == 'login':
            if user := User.query.filter_by(name=request.form['name'], password=request.form['password']).first():
                login_user(user)
                return redirect('/')
            else:
                return render_template('login.html', message='Invalid Credentials')
        elif request.form['button'] == 'register':
            return redirect('/register')
    elif request.method == 'GET':
        return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect('/')
    if request.method == 'POST':
        if request.form['button'] == 'register':
            if request.form['password'] != request.form['confirm']:
                return render_template('register.html', message='Password Mismatch')
            db.session.add(User(
                name=request.form['name'],
                password=request.form['password'],
            ))
            try:
                db.session.commit()
            except:
                return render_template('register.html', message='Name Taken')
        return redirect('/login')
    elif request.method == 'GET':
        return render_template('register.html')

@app.route('/update_server', methods=['POST'])
def webhook():
    if request.method == 'POST':
        git.Repo('https://github.com/wjmolina/PythonAnywhereApp').remotes.origin.pull()
        return 'Updated PythonAnywhere successfully', 200
    else:
        return 'Wrong Method', 400
