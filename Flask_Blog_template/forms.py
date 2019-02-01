""" All Forms used in the system """
from wtforms import TextField, PasswordField, FormField, TextAreaField, SubmitField, SelectField, IntegerField,FloatField,BooleanField, validators
from wtforms.validators import Required, ValidationError
from flask_wtf import FlaskForm

class LoginForm(FlaskForm):
    """ LoginForm class having form fields for user login """

    username = TextField('Email',[Required(),validators.Email()])
    password = PasswordField('Password',[Required()])
    submit = SubmitField("Login")