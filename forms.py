#! quali-man-env/bin/python3.13

from flask_wtf import FlaskForm
from wtforms import StringField, DateField, SubmitField, SelectField
from wtforms.validators import DataRequired, Optional

class DocumentForm(FlaskForm):
    employee_id = SelectField('ФИО сотрудника', coerce=int, validators=[DataRequired()])
    type = StringField('Тип документа', validators=[DataRequired()])
    issue_date = DateField('Дата выдачи', validators=[DataRequired()])
    expiry_date = DateField('Дата истечения', validators=[Optional()])
    submit = SubmitField('Добавить')

class EmployeeForm(FlaskForm):
    name = StringField('ФИО', validators=[DataRequired()])
    position = StringField('Должность', validators=[DataRequired()])
    submit = SubmitField('Добавить')
