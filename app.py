#! quali-man-env/bin/python3.13

from datetime import date
from flask import Flask, render_template, redirect, url_for
from forms import DocumentForm, EmployeeForm
from classes import db, Document, Employee

from config import SECRET_KEY

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///documents.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = SECRET_KEY

db.init_app(app)

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    documents = Document.query.all()
    employees = Employee.query.all()
    current_date = date.today()
    for doc in documents:
        is_expired = doc.expiry_date and doc.expiry_date <= current_date
        print(f"Document {doc.id}: expiry_date={doc.expiry_date}, expired={is_expired}")
    return render_template('index.html', documents=documents, employees=employees,\
                           current_date=current_date)

# Страница добавления документов
@app.route('/add_document', methods=['GET', 'POST'])
def add_document():
    form = DocumentForm()
    employees = Employee.query.all()
    if not employees:
        return render_template('add_document.html', form=form, error="Нет сотрудников. Сначала добавьте сотрудника.")
    # Динамически задаем список сотрудников для SelectField
    form.employee_id.choices = [(employee.id, employee.name) for employee in employees]
    if form.validate_on_submit():
        # Создаем новую запись из данных формы
        new_document = Document(
            type=form.type.data,
            issue_date=form.issue_date.data,
            expiry_date=form.expiry_date.data,
            employee_id=form.employee_id.data
        )
        db.session.add(new_document)
        db.session.commit()
        return redirect(url_for('index'))  # Перенаправление на главную страницу
    errors = form.errors
    return render_template('add_document.html', form=form, errors=errors)

# Страница добавления сотрудников
@app.route('/add_employee', methods=['GET', 'POST'])
def add_employee():
    form = EmployeeForm()
    if form.validate_on_submit():
        # Создаем новую запись из данных формы
        new_employee = Employee(
            name=form.name.data,
            position=form.position.data
        )
        db.session.add(new_employee)
        db.session.commit()
        return redirect(url_for('index'))  # Перенаправление на главную страницу
    return render_template('add_employee.html', form=form)
