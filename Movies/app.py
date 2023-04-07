import os
from flask import Flask, render_template, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from datetime import datetime
from flask_login import LoginManager, current_user, logout_user, login_user, UserMixin, login_required
import forms

basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)

secret_key = os.urandom(32)
app.config['SECRET_KEY'] = secret_key
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'movies.db')+'?check_same_thread=False'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

Migrate(app, db)

bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'


class User(db.Model, UserMixin):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column("Name", db.String(20), unique=True, nullable=False)
    e_mail = db.Column("Email", db.String(120), unique=True, nullable=False)
    password = db.Column("Password", db.String(60), unique=True, nullable=False)


movie_actor = db.Table('movie_actor', db.metadata,
    db.Column('movie_id', db.Integer, db.ForeignKey('movie.id'), primary_key=True),
    db.Column('actor_id', db.Integer, db.ForeignKey('actor.id'), primary_key=True)
)   
    
class Movie(db.Model):
    __tablename__ = 'movie'
    id = db.Column(db.Integer, primary_key=True)
    movie_title = db.Column("Title", db.String (100))
    movie_description = db.Column('Desription', db.String(1500))
    date = db.Column("Date", db.DateTime, default=datetime.now())
    actors = db.relationship("Actor", secondary=movie_actor, back_populates="movies")
    
    
class Actor(db.Model):
    __tablename__ = 'actor'
    id = db.Column(db.Integer, primary_key=True)
    actor_name = db.Column("Actor name", db.String)
    movies = db.relationship("Movie", secondary=movie_actor, back_populates="actors")

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route("/register", methods=['GET', 'POST'])
def register():
    db.create_all()
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = forms.RegisterForm()
    if form.validate_on_submit():
        encrypted_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(name=form.name.data, e_mail=form.e_mail.data, password=encrypted_password)
        db.session.add(user)
        db.session.commit()
        flash('You have succesfully registered. Please login.', 'success')
        return redirect(url_for('index'))
    return render_template('register.html', title='Register', form=form)

@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = forms.LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(e_mail=form.e_mail.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('index'))
        else:
            flash('Could not login. Please try again!', 'danger')
    return render_template('login.html', title='Login', form=form)

@app.route("/all_actors", methods=['GET', 'POST'])
@login_required
def all_actors():
    page = request.args.get('page', 1, type=int)
    all_actors = Actor.query.order_by(Actor.id.asc()).paginate(page=page, per_page=6)
    return render_template("all_actors.html", all_actors = all_actors)

@app.route("/add_actor", methods=['GET', 'POST'])
@login_required
def add_actor():
    form = forms.AddActor()
    if form.validate_on_submit():
        new_actor = Actor(actor_name=form.actor_name.data)
        for movie in form.movies.data:
            assigned_movie = Movie.query.get(movie.id)
            new_actor.movies.append(assigned_movie)
        db.session.add(new_actor)
        db.session.commit()
        flash('New actor has been added.', 'success')
        return redirect(url_for('all_actors'))
    return render_template("add_actor.html", form = form)

@app.route("/actor/<int:id>", methods=['GET', 'POST'])
@login_required
def actor(id):
    actor = Actor.query.get(id)
    return render_template("actor.html", actor=actor)

@app.route("/all_movies", methods=['GET', 'POST'])
@login_required
def all_movies():
    page = request.args.get('page', 1, type=int)
    all_movies = Movie.query.order_by(Movie.date.asc()).paginate(page=page, per_page=3)
    return render_template("all_movies.html", all_movies=all_movies)

@app.route("/add_movie", methods=['GET', 'POST'])
@login_required
def add_movie():
    form = forms.AddMovie()
    if form.validate_on_submit():
        new_movie = Movie(movie_title=form.movie_title.data, movie_description=form.movie_description.data)
        for actor in form.actors.data:
            assigned_actor = Actor.query.get(actor.id)
            new_movie.actors.append(assigned_actor)
        db.session.add(new_movie)
        db.session.commit()
        flash('New movie has been added.', 'success')
        return redirect(url_for('all_movies'))
    return render_template("add_movie.html", form = form, datetime=datetime)

@app.route("/movie/<int:id>", methods=['GET', 'POST'])
@login_required
def movie(id):
    movie = Movie.query.get(id)
    return render_template("movie.html", movie=movie)

@app.route("/logout")
def logout():
    logout_user()
    return render_template('index.html')

@app.route("/")
def index():
    return render_template('index.html')

if __name__ == '__main__':
    db.create_all()
    app.run(host='127.0.0.1', port=8000, debug=True)