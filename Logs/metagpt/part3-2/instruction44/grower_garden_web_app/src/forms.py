from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from src.models import User

class RegistrationForm(FlaskForm):
    username = StringField(
        'Username',
        validators=[DataRequired(), Length(min=3, max=64)]
    )
    email = StringField(
        'Email',
        validators=[DataRequired(), Email(), Length(max=120)]
    )
    password = PasswordField(
        'Password',
        validators=[DataRequired(), Length(min=6, max=128)]
    )
    confirm_password = PasswordField(
        'Confirm Password',
        validators=[DataRequired(), EqualTo('password')]
    )
    roblox_username = StringField(
        'Roblox Username',
        validators=[DataRequired(), Length(min=3, max=64)]
    )
    private_server_info = TextAreaField(
        'Private Server Info',
        validators=[Length(max=1024)]
    )
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username is already taken.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email is already registered.')

class LoginForm(FlaskForm):
    username = StringField(
        'Username',
        validators=[DataRequired(), Length(min=3, max=64)]
    )
    password = PasswordField(
        'Password',
        validators=[DataRequired()]
    )
    submit = SubmitField('Login')

class PurchaseForm(FlaskForm):
    roblox_username = StringField(
        'Roblox Username',
        validators=[DataRequired(), Length(min=3, max=64)]
    )
    private_server_info = TextAreaField(
        'Private Server Info',
        validators=[Length(max=1024)]
    )
    submit = SubmitField('Purchase')