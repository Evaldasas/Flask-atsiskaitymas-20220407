from flask_wtf import FlaskForm
from wtforms import SubmitField, BooleanField, StringField, PasswordField, TextAreaField
from wtforms.validators import DataRequired, ValidationError, EqualTo
from wtforms_sqlalchemy.fields import  QuerySelectMultipleField
import app

class RegisterForm(FlaskForm):
    name = StringField('Full name', [DataRequired()])
    e_mail = StringField('Email', [DataRequired()])
    password = PasswordField('Password', [DataRequired()])
    confirmed_password = PasswordField("Repeat password", [EqualTo('password', 'Passwords does not match!')])
    submit = SubmitField("Register")
       
    def validate_name(self, name):
        user = app.User.query.filter_by(name=name.data).first()
        if user:
            raise ValidationError('This name is already in use. Please choose another one!')
    
    def validate_e_mail(self, e_mail):
        user = app.User.query.filter_by(e_mail=e_mail.data).first()
        if user:
            raise ValidationError('This e-mail is already in use. Please choose another one!')

def actor_query():
    return app.Actor.query

def movie_query():
    return app.Movie.query

def get_pk(obj):
    return str(obj)

class LoginForm(FlaskForm):
    e_mail = StringField('Email', [DataRequired()])
    password = PasswordField('Password', [DataRequired()])
    remember = BooleanField("Remember me")
    submit = SubmitField('Login')

class AddActor(FlaskForm):
    actor_name = StringField('Actor Name', [DataRequired()])
    movies = QuerySelectMultipleField('Choose movies for this actor', query_factory=movie_query, allow_blank=True, get_label="movie_title", get_pk=get_pk)
    submit = SubmitField('Add Actor')

class AddMovie(FlaskForm):
    movie_title = StringField('Movie title', [DataRequired()])
    movie_description = TextAreaField('Description', [DataRequired()])
    actors = QuerySelectMultipleField('Select actors for this movie', query_factory=actor_query, allow_blank=True, get_label="actor_name", get_pk=get_pk)
    submit = SubmitField('Add Movie')