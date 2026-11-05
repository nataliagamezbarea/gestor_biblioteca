from datetime import datetime
from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
# Configuración de SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///library.db'
app.config['SQLALCHEMY_TRACK_MODIFICATION'] = False

db = SQLAlchemy(app)

# ------------------- MODELOS DE DATOS -------------------

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    isbn = db.Column(db.String(20), unique=True, nullable=False)
    copies = db.Column(db.Integer, default=1)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    role = db.Column(db.String(20), default='Alumno') # 'Alumno' o 'Profesor'

class Loan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    loan_date = db.Column(db.DateTime, default=datetime.utcnow)
    return_date = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(20), default='Activo') # 'Activo' o 'Devuelto'

# Crea las tablas en la BD si no existen
with app.app_context():
    db.create_all()

# ------------------- RUTAS Y API REST -------------------

@app.route('/')
def index():
    return render_template('index.html')

# --- LIBROS ---
@app.route('/api/books', methods=['GET', 'POST'])
def handle_books():
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
        return jsonify({'message': 'Libro creado correctamente'}), 201

    books = Book.query.all()
    return jsonify([{
        'id': b.id, 'title': b.title, 'author': b.author, 
        'isbn': b.isbn, 'copies': b.copies
    } for b in books])

# --- USUARIOS ---
@app.route('/api/users', methods=['GET', 'POST'])
def handle_users():
    if request.method == 'POST':
        data = request.json
        new_user = User(
            name=data['name'],
            email=data['email'],
            role=data.get('role', 'Alumno')
        )
        db.session.add(new_user)
        db.session.commit()
        return jsonify({'message': 'Usuario creado correctamente'}), 201

    users = User.query.all()
    return jsonify([{
        'id': u.id, 'name': u.name, 'email': u.email, 'role': u.role
    } for u in users])

# --- PRÉSTAMOS ---
@app.route('/api/loans', methods=['GET', 'POST'])
def handle_loans():
    if request.method == 'POST':
        data = request.json
        book = Book.query.get(data['book_id'])
        
        # Validación de ejemplares disponibles
        if not book or book.copies <= 0:
            return jsonify({'error': 'No hay ejemplares disponibles'}), 400
        
        new_loan = Loan(
            book_id=data['book_id'],
            user_id=data['user_id']
        )
        book.copies -= 1  # Descuento de stock
        db.session.add(new_loan)
        db.session.commit()
        return jsonify({'message': 'Préstamo realizado con éxito'}), 201

    loans = db.session.query(Loan, Book, User).join(Book).join(User).all()
    return jsonify([{
        'id': l.Loan.id,
        'book_title': l.Book.title,
        'user_name': l.User.name,
        'loan_date': l.Loan.loan_date.strftime('%Y-%m-%d %H:%M'),
        'status': l.Loan.status
    } for l in loans])

@app.route('/api/loans/<int:loan_id>/return', methods=['PUT'])
def return_loan(loan_id):
    loan = Loan.query.get(loan_id)
    if not loan or loan.status == 'Devuelto':
        return jsonify({'error': 'Préstamo no encontrado o ya devuelto'}), 400

    loan.status = 'Devuelto'
    loan.return_date = datetime.utcnow()
    
    # Restaurar stock
    book = Book.query.get(loan.book_id)
    if book:
        book.copies += 1

    db.session.commit()
    return jsonify({'message': 'Libro devuelto con éxito'})

if __name__ == '__main__':
    app.run(debug=True)