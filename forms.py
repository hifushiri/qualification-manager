# forms.py
#! quali-man-env/bin/python3.13

from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, DateField, SubmitField, SelectField, PasswordField, EmailField
from wtforms.validators import DataRequired, Optional, Email, EqualTo, Length

class DocumentForm(FlaskForm):
    employee_id = SelectField('ФИО сотрудника', coerce=int, validators=[DataRequired()])
    type = StringField('Тип документа', validators=[DataRequired()])
    issue_date = DateField('Дата выдачи', validators=[DataRequired()])
    expiry_date = DateField('Дата истечения', validators=[Optional()])
    registration_number = StringField('Регистрационный номер', validators=[Optional()])
    file = FileField('Файл документа', validators=[FileAllowed(['pdf', 'jpg', 'png'], 'Только PDF, JPG или PNG!'), Optional()])
    submit = SubmitField('Добавить')

class EmployeeForm(FlaskForm):
    name = StringField('ФИО', validators=[DataRequired(), Length(max=50)])
    position = StringField('Должность', validators=[DataRequired(), Length(max=100)])
    submit = SubmitField('Добавить')

class RegisterForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired(), Length(min=4, max=20)])
    email = EmailField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Пароль', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Подтвердить пароль', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Регистрация')

class LoginForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    submit = SubmitField('Войти')