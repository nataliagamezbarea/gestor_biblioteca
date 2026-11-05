import os
import secrets
from datetime import timedelta

from flask import Flask
from sqlalchemy import inspect, text

from database import db
from models import Book, Loan, User
from routes.dashboard import dashboard_bp
from routes.main import main_bp

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///library.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

secret_key_path = os.path.join(app.instance_path, '.secret_key')
if not os.environ.get('SECRET_KEY') and not os.path.exists(secret_key_path):
    os.makedirs(app.instance_path, exist_ok=True)
    try:
        with open(secret_key_path, 'x', encoding='utf-8') as secret_file:
            secret_file.write(secrets.token_hex(32))
    except FileExistsError:
        pass
if not os.environ.get('SECRET_KEY'):
    os.chmod(secret_key_path, 0o600)
if os.environ.get('SECRET_KEY'):
    app.config['SECRET_KEY'] = os.environ['SECRET_KEY']
else:
    with open(secret_key_path, encoding='utf-8') as secret_file:
        app.config['SECRET_KEY'] = secret_file.read().strip()
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=30)
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

db.init_app(app)
app.register_blueprint(main_bp)
app.register_blueprint(dashboard_bp)

# Keep the original API paths while retaining the remote dashboard API paths.
app.add_url_rule(
    '/api/books',
    endpoint='api_books',
    view_func=app.view_functions['dashboard.manage_books'],
    methods=['GET', 'POST'],
)
app.add_url_rule(
    '/api/books/<int:book_id>',
    endpoint='api_book',
    view_func=app.view_functions['dashboard.manage_book'],
    methods=['PUT', 'DELETE'],
)
app.add_url_rule(
    '/api/users',
    endpoint='api_users',
    view_func=app.view_functions['dashboard.manage_users'],
    methods=['GET', 'POST'],
)
app.add_url_rule(
    '/api/users/<int:user_id>',
    endpoint='api_user',
    view_func=app.view_functions['dashboard.manage_user'],
    methods=['PUT', 'DELETE'],
)
app.add_url_rule(
    '/api/loans',
    endpoint='api_loans',
    view_func=app.view_functions['dashboard.manage_loans'],
    methods=['GET', 'POST'],
)
app.add_url_rule(
    '/api/loans/<int:loan_id>/return',
    endpoint='api_return_loan',
    view_func=app.view_functions['dashboard.return_loan'],
    methods=['PUT'],
)

with app.app_context():
    db.create_all()
    user_columns = {column['name'] for column in inspect(db.engine).get_columns('user')}
    if 'password_hash' not in user_columns:
        with db.engine.begin() as connection:
            connection.execute(text('ALTER TABLE user ADD COLUMN password_hash VARCHAR(256)'))

if __name__ == '__main__':
    app.run(debug=True)
