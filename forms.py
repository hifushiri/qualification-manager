#! quali-man-env/bin/python3.13

from flask_wtf import FlaskForm
from wtforms import StringField, DateField, SubmitField
from wtforms.validators import DataRequired

class CertificateForm(FlaskForm):
    employee_name = StringField('ФИО', validators=[DataRequired()])
    certificate_type = StringField('Тип аттестата', validators=[DataRequired()])
    issue_date = DateField('Дата выдачи', validators=[DataRequired()])
    expiry_date = DateField('Дата истечения', validators=[DataRequired()])
    submit = SubmitField('Добавить')