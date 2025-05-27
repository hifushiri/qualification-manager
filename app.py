#! quali-man-env/bin/python3.13

from flask import Flask, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from forms import CertificateForm

from config import SECRET_KEY

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///certificates.db'
app.secret_key = SECRET_KEY
db = SQLAlchemy(app)

class Certificate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    employee_name = db.Column(db.String(100), nullable=False)
    certificate_type = db.Column(db.String(50), nullable=False)
    issue_date = db.Column(db.Date, nullable=False)
    expiry_date = db.Column(db.Date, nullable=True)

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    certificates = Certificate.query.all()
    return render_template('index.html', certificates=certificates)

@app.route('/add_certificate', methods=['GET', 'POST'])
def add_certificate():
    form = CertificateForm()
    if form.validate_on_submit():
        # Создаем новую запись из данных формы
        new_certificate = Certificate(
            employee_name=form.employee_name.data,
            certificate_type=form.certificate_type.data,
            issue_date=form.issue_date.data,
            expiry_date=form.expiry_date.data
        )
        db.session.add(new_certificate)
        db.session.commit()
        return redirect(url_for('index'))  # Перенаправление на главную страницу
    return render_template('add_certificate.html', form=form)