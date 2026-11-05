from flask import Blueprint, render_template, jsonify
from models import Book

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def home():
    return render_template('index.html')

@main_bp.route('/catalogo')
def public_catalog():
    books = Book.query.all()
    return jsonify([{
        'id': b.id, 'title': b.title, 'author': b.author, 
        'isbn': b.isbn, 'copies': b.copies
    } for b in books])