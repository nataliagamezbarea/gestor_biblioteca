from datetime import datetime

from flask import Blueprint, jsonify, render_template, request
from werkzeug.security import generate_password_hash

from auth import admin_required, current_user, login_required
from database import db
from models import Book, Loan, User

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')


@dashboard_bp.route('/')
@login_required
def index():
    user = current_user()
    is_admin = user.role == 'Administrador'
    books = Book.query.order_by(Book.title).all()

    loan_query = db.session.query(Loan, Book, User).join(Book).join(User)
    if not is_admin:
        loan_query = loan_query.filter(Loan.user_id == user.id)
    loan_history = loan_query.order_by(Loan.loan_date.desc()).all()

    active_loans_query = Loan.query.filter_by(status='Activo')
    if not is_admin:
        active_loans_query = active_loans_query.filter_by(user_id=user.id)

    return render_template(
        'dashboard.html',
        books=books,
        users_count=User.query.count() if is_admin else None,
        active_loans_count=active_loans_query.count(),
        loan_history=loan_history,
        current_user=user,
        is_admin=is_admin,
    )


@dashboard_bp.route('/gestion')
@admin_required
def gestion():
    return render_template('gestion.html')


@dashboard_bp.route('/api/stats')
@login_required
def stats():
    user = current_user()
    active_loans_query = Loan.query.filter_by(status='Activo')
    if user.role != 'Administrador':
        active_loans_query = active_loans_query.filter_by(user_id=user.id)
    return jsonify({
        'total_books': Book.query.count(),
        'total_users': User.query.count() if user.role == 'Administrador' else None,
        'active_loans': active_loans_query.count(),
    })


@dashboard_bp.route('/api/books', methods=['GET', 'POST'])
@login_required
def manage_books():
    if request.method == 'POST':
        user = current_user()
        if user.role != 'Administrador':
            return jsonify({'error': 'Se requieren permisos de administrador'}), 403

        data = request.get_json(silent=True) or {}
        required_fields = ('title', 'author', 'isbn')
        if any(not str(data.get(field, '')).strip() for field in required_fields):
            return jsonify({'error': 'Título, autor e ISBN son obligatorios'}), 400
        try:
            copies = int(data.get('copies', 1))
        except (TypeError, ValueError):
            return jsonify({'error': 'El número de ejemplares no es válido'}), 400
        if copies < 1:
            return jsonify({'error': 'Debe haber al menos un ejemplar'}), 400

        book = Book(
            title=data['title'].strip(),
            author=data['author'].strip(),
            isbn=data['isbn'].strip(),
            copies=copies,
        )
        db.session.add(book)
        db.session.commit()
        return jsonify({'message': 'Libro añadido con éxito'}), 201

    books = Book.query.order_by(Book.title).all()
    return jsonify([{
        'id': book.id,
        'title': book.title,
        'author': book.author,
        'isbn': book.isbn,
        'copies': book.copies,
    } for book in books])


@dashboard_bp.route('/api/users', methods=['GET', 'POST'])
@admin_required
def manage_users():
    if request.method == 'POST':
        data = request.get_json(silent=True) or {}
        name = str(data.get('name', '')).strip()
        email = str(data.get('email', '')).strip().lower()
        password = data.get('password', '')
        if not name or not email or not password:
            return jsonify({'error': 'Nombre, correo y contraseña son obligatorios'}), 400
        if len(password) < 8:
            return jsonify({'error': 'La contraseña debe tener al menos 8 caracteres'}), 400
        if User.query.filter(db.func.lower(User.email) == email).first():
            return jsonify({'error': 'Ya existe una cuenta con ese correo'}), 409

        db.session.add(User(
            name=name,
            email=email,
            role='Usuario',
            password_hash=generate_password_hash(password),
        ))
        db.session.commit()
        return jsonify({'message': 'Usuario registrado'}), 201

    users = User.query.order_by(User.name).all()
    return jsonify([{
        'id': user.id,
        'name': user.name,
        'email': user.email,
        'role': user.role,
    } for user in users])


@dashboard_bp.route('/api/loans', methods=['GET', 'POST'])
@login_required
def manage_loans():
    user = current_user()
    if request.method == 'POST':
        data = request.get_json(silent=True) or {}
        try:
            book_id = int(data['book_id'])
        except (KeyError, TypeError, ValueError):
            return jsonify({'error': 'El identificador del libro no es válido'}), 400

        book = db.session.get(Book, book_id)
        if not book or book.copies <= 0:
            return jsonify({'error': 'No hay ejemplares disponibles'}), 400

        db.session.add(Loan(book_id=book.id, user_id=user.id))
        book.copies -= 1
        db.session.commit()
        return jsonify({'message': 'Préstamo procesado'}), 201

    loans_query = db.session.query(Loan, Book, User).join(Book).join(User)
    if user.role != 'Administrador':
        loans_query = loans_query.filter(Loan.user_id == user.id)
    loans = loans_query.order_by(Loan.loan_date.desc()).all()
    return jsonify([{
        'id': loan.id,
        'book_title': book.title,
        'user_name': borrower.name,
        'loan_date': loan.loan_date.strftime('%Y-%m-%d %H:%M'),
        'return_date': loan.return_date.strftime('%Y-%m-%d %H:%M') if loan.return_date else None,
        'status': loan.status,
    } for loan, book, borrower in loans])


@dashboard_bp.route('/api/loans/<int:loan_id>/return', methods=['PUT'])
@admin_required
def return_loan(loan_id):
    loan = db.session.get(Loan, loan_id)
    if not loan or loan.status == 'Devuelto':
        return jsonify({'error': 'Préstamo no encontrado o ya devuelto'}), 400

    loan.status = 'Devuelto'
    loan.return_date = datetime.utcnow()
    book = db.session.get(Book, loan.book_id)
    if book:
        book.copies += 1
    db.session.commit()
    return jsonify({'message': 'Libro devuelto con éxito'})
