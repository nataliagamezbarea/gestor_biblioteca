from flask import Blueprint, flash, jsonify, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

from database import db
from models import Book, User

main_bp = Blueprint('main', __name__)


@main_bp.route('/', methods=['GET', 'POST'])
def home():
    if session.get('user_id'):
        return redirect(url_for('dashboard.index'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        user = User.query.filter(db.func.lower(User.email) == email).first()
        if user and user.password_hash and check_password_hash(user.password_hash, password):
            session.clear()
            session['user_id'] = user.id
            session.permanent = request.form.get('remember_me') == 'on'
            return redirect(url_for('dashboard.index'))
        flash('Correo o contraseña incorrectos.', 'danger')

    return render_template('index.html')


@main_bp.route('/register', methods=['GET', 'POST'])
def register():
    if session.get('user_id'):
        return redirect(url_for('dashboard.index'))

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirmation = request.form.get('password_confirmation', '')

        if not name or not email:
            flash('Completa todos los campos.', 'danger')
        elif len(password) < 8:
            flash('La contraseña debe tener al menos 8 caracteres.', 'danger')
        elif password != confirmation:
            flash('Las contraseñas no coinciden.', 'danger')
        elif User.query.filter(db.func.lower(User.email) == email).first():
            flash('Ya existe una cuenta con ese correo.', 'danger')
        else:
            db.session.add(User(
                name=name,
                email=email,
                role='Usuario',
                password_hash=generate_password_hash(password),
            ))
            db.session.commit()
            flash('Cuenta de usuario creada. Ya puedes iniciar sesión.', 'success')
            return redirect(url_for('main.home'))

    return render_template('register.html')


@main_bp.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return redirect(url_for('main.home'))


@main_bp.route('/catalogo')
def public_catalog():
    books = Book.query.order_by(Book.title).all()
    return jsonify([{
        'id': book.id,
        'title': book.title,
        'author': book.author,
        'isbn': book.isbn,
        'copies': book.copies,
    } for book in books])


@main_bp.route('/catalogo/vista')
def catalog_page():
    return render_template('catalogo.html')
