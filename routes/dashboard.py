from datetime import datetime
from flask import Blueprint, render_template, request, jsonify
from database import db
from models import Book, User, Loan

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')

# Vista principal del Dashboard
@dashboard_bp.route('/')
def index():
    return render_template('dashboard.html')

# API interna para métricas del panel
@dashboard_bp.route('/api/stats')
def stats():
    total_books = Book.query.count()
    total_users = User.query.count()
    active_loans = Loan.query.filter_by(status='Activo').count()
    return jsonify({
        'total_books': total_books,
        'total_users': total_users,
        'active_loans': active_loans
    })

# CRUD Libros (Admin)
@dashboard_bp.route('/api/books', methods=['GET', 'POST'])
def manage_books():
    if request.method == 'POST':
        data = request.json
        new_book = Book(
            title=data['title'],
            author=data['author'],
            isbn=data['isbn'],
            copies=int(data.get('copies', 1))
        )
        db.session.add(new_book)
        db.session.commit()
        return jsonify({'message': 'Libro añadido con éxito'}), 201

    books = Book.query.all()
    return jsonify([{
        'id': b.id, 'title': b.title, 'author': b.author, 
        'isbn': b.isbn, 'copies': b.copies
    } for b in books])

# CRUD Usuarios (Admin)
@dashboard_bp.route('/api/users', methods=['GET', 'POST'])
def manage_users():
    if request.method == 'POST':
        data = request.json
        new_user = User(
            name=data['name'],
            email=data['email'],
            role=data.get('role', 'Alumno')
        )
        db.session.add(new_user)
        db.session.commit()
        return jsonify({'message': 'Usuario registrado'}), 201

    users = User.query.all()
    return jsonify([{
        'id': u.id, 'name': u.name, 'email': u.email, 'role': u.role
    } for u in users])

# Gestión de Préstamos (Admin)
@dashboard_bp.route('/api/loans', methods=['GET', 'POST'])
def manage_loans():
    if request.method == 'POST':
        data = request.json
        book = Book.query.get(data['book_id'])
        
        if not book or book.copies <= 0:
            return jsonify({'error': 'No hay copias disponibles'}), 400
        
        new_loan = Loan(book_id=data['book_id'], user_id=data['user_id'])
        book.copies -= 1
        db.session.add(new_loan)
        db.session.commit()
        return jsonify({'message': 'Préstamo procesado'}), 201

    loans = db.session.query(Loan, Book, User).join(Book).join(User).all()
    return jsonify([{
        'id': l.Loan.id,
        'book_title': l.Book.title,
        'user_name': l.User.name,
        'loan_date': l.Loan.loan_date.strftime('%Y-%m-%d %H:%M'),
        'status': l.Loan.status
    } for l in loans])