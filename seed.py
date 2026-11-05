from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash
from app import app
from database import db
from models import Book, User, Loan

def seed_database():
    with app.app_context():
        # Crear tablas si no existen en la base de datos
        db.create_all()

        # 1. CATALOGO DE LIBROS
        books_data = [
            Book(title='Cien años de soledad', author='Gabriel García Márquez', isbn='978-84-376-0494-7', copies=5),
            Book(title='Don Quijote de la Mancha', author='Miguel de Cervantes', isbn='978-84-241-1603-3', copies=3),
            Book(title='1984', author='George Orwell', isbn='978-84-9989-094-4', copies=4),
            Book(title='El principito', author='Antoine de Saint-Exupéry', isbn='978-84-348-9447-1', copies=6),
            Book(title='Fahrenheit 451', author='Ray Bradbury', isbn='978-84-450-7494-7', copies=2),
            Book(title='Orgullo y prejuicio', author='Jane Austen', isbn='978-84-9794-082-5', copies=4),
            Book(title='Crónica de una muerte anunciada', author='Gabriel García Márquez', isbn='978-84-9759-243-7', copies=3),
            Book(title='Un mundo feliz', author='Aldous Huxley', isbn='978-84-9759-425-7', copies=2)
        ]
        
        for book in books_data:
            if not Book.query.filter_by(isbn=book.isbn).first():
                db.session.add(book)

        # Contraseña por defecto para las cuentas de prueba: "123456"
        default_password = generate_password_hash('123456')

        # 2. USUARIOS (4 Admins + 4 Usuarios Normales)
        users_data = [
            # 4 Administradores (rol 'Admin')
            User(name='Carlos Gómez', email='carlos.gomez@colegio.edu', role='Admin', password_hash=default_password),
            User(name='Elena Rodríguez', email='elena.rodriguez@colegio.edu', role='Admin', password_hash=default_password),
            User(name='Marta Sánchez', email='marta.sanchez@colegio.edu', role='Admin', password_hash=default_password),
            User(name='Javier López', email='javier.lopez@colegio.edu', role='Admin', password_hash=default_password),
            
            # 4 Usuarios Normales (rol 'Usuario')
            User(name='Lucas Martínez', email='lucas.martinez@alumno.edu', role='Usuario', password_hash=default_password),
            User(name='Sofía Fernández', email='sofia.fernandez@alumno.edu', role='Usuario', password_hash=default_password),
            User(name='Mateo Torres', email='mateo.torres@alumno.edu', role='Usuario', password_hash=default_password),
            User(name='Lucía Navarro', email='lucia.navarro@alumno.edu', role='Usuario', password_hash=default_password)
        ]

        for user in users_data:
            if not User.query.filter_by(email=user.email).first():
                db.session.add(user)

        db.session.commit()

        # 3. HISTORIAL Y REGISTRO DE PRÉSTAMOS
        all_books = Book.query.all()
        all_users = User.query.all()

        if len(all_books) >= 5 and len(all_users) >= 8 and Loan.query.count() == 0:
            loans_data = [
                Loan(book_id=all_books[0].id, user_id=all_users[4].id, loan_date=datetime.utcnow() - timedelta(days=10), status='Activo'),
                Loan(book_id=all_books[1].id, user_id=all_users[5].id, loan_date=datetime.utcnow() - timedelta(days=5), status='Activo'),
                Loan(book_id=all_books[2].id, user_id=all_users[6].id, loan_date=datetime.utcnow() - timedelta(days=15), return_date=datetime.utcnow() - timedelta(days=2), status='Devuelto'),
                Loan(book_id=all_books[3].id, user_id=all_users[7].id, loan_date=datetime.utcnow() - timedelta(days=8), status='Activo'),
                Loan(book_id=all_books[4].id, user_id=all_users[0].id, loan_date=datetime.utcnow() - timedelta(days=3), status='Activo')
            ]

            for loan in loans_data:
                if loan.status == 'Activo':
                    book = Book.query.get(loan.book_id)
                    if book and book.copies > 0:
                        book.copies -= 1
                db.session.add(loan)

            db.session.commit()

        print("Base de datos generada exitosamente con contraseñas encriptadas.")

if __name__ == '__main__':
    seed_database()