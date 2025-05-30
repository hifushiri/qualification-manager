#! quali-man-env/bin/python3.13

import os
from datetime import date
from flask import Flask, render_template, redirect, url_for, send_file, request, jsonify, flash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from forms import DocumentForm, EmployeeForm, RegisterForm, LoginForm
from classes import db, Document, Employee, User
from werkzeug.utils import secure_filename
from openpyxl import Workbook
from io import BytesIO

from config import SECRET_KEY

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///documents.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = SECRET_KEY
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Лимит 16 МБ

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

db.init_app(app)

# Инициализация Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


with app.app_context():
    db.create_all()

@app.route('/')
@login_required
def index():
    documents = Document.query.all()
    employees = Employee.query.all()
    current_date = date.today()
    for doc in documents:
        is_expired = doc.expiry_date and doc.expiry_date <= current_date
        print(f"Document {doc.id}: expiry_date={doc.expiry_date}, expired={is_expired}")
    return render_template('index.html', documents=documents, employees=employees)

# Страница добавления документов
@app.route('/add_document', methods=['GET', 'POST'])
@login_required
def add_document():
    form = DocumentForm()
    employees = Employee.query.all()
    if not employees:
        return render_template('add_document.html', form=form, error="Нет сотрудников. Сначала добавьте сотрудника.")
    form.employee_id.choices = [(employee.id, employee.name) for employee in employees]
    if form.validate_on_submit():
        file_path = None
        if form.file.data:
            file = form.file.data
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
        new_document = Document(
            type=form.type.data,
            issue_date=form.issue_date.data,
            expiry_date=form.expiry_date.data,
            employee_id=form.employee_id.data,
            registration_number=form.registration_number.data,
            file_path=file_path
        )
        db.session.add(new_document)
        db.session.commit()
        flash('Документ добавлен!', 'success')
        return redirect(url_for('index'))
    errors = form.errors
    return render_template('add_document.html', form=form, errors=errors)

@app.route('/download/<int:document_id>')
@login_required
def download_file(document_id):
    document = Document.query.get_or_404(document_id)
    if document.file_path and os.path.exists(document.file_path):
        return send_file(document.file_path, as_attachment=True)
    return "Файл не найден", 404

@app.route('/export_excel', methods=['POST'])
@login_required
def export_excel():
    data = request.get_json()
    rows = data.get('rows', [])
    
    wb = Workbook()
    ws = wb.active
    ws.title = "Documents"
    
    headers = ["ФИО", "Тип документа", "Дата выдачи", "Дата истечения", "Регистрационный номер", "Файл", "Должность"]
    ws.append(headers)
    
    for row in rows:
        ws.append([
            row[0],  # ФИО
            row[1],  # Тип документа
            row[2],  # Дата выдачи
            row[3],  # Дата истечения
            row[4],  # Регистрационный номер
            row[5],  # Файл
            row[6]   # Должность
        ])
    
    output = BytesIO()
    wb.save(output)
    output.seek(0)
    
    return send_file(
        output,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        download_name='documents.xlsx',
        as_attachment=True
    )


# Страница добавления сотрудников
@app.route('/add_employee', methods=['GET', 'POST'])
@login_required
def add_employee():
    form = EmployeeForm()
    if form.validate_on_submit():
        new_employee = Employee(
            name=form.name.data,
            position=form.position.data
        )
        db.session.add(new_employee)
        db.session.commit()
        flash('Сотрудник добавлен!', 'success')
        return redirect(url_for('index'))
    return render_template('add_employee.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegisterForm()
    if form.validate_on_submit():
        if User.query.filter_by(username=form.username.data).first():
            flash('Имя пользователя уже занято.', 'danger')
            return render_template('register.html', form=form)
        if User.query.filter_by(email=form.email.data).first():
            flash('Email уже зарегистрирован.', 'danger')
            return render_template('register.html', form=form)
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Регистрация успешна! Пожалуйста, войдите.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            flash('Вы вошли в систему!', 'success')
            return redirect(url_for('index'))
        flash('Неверный email или пароль.', 'danger')
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Вы вышли из системы.', 'success')
    return redirect(url_for('login'))

# Отладка маршрутов
with app.app_context():
    print("Registered routes:")
    for rule in app.url_map.iter_rules():
        print(f"{rule.endpoint}: {rule}")
