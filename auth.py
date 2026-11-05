from functools import wraps

from flask import jsonify, redirect, request, session, url_for

from database import db
from models import User


def current_user():
    user_id = session.get('user_id')
    user = db.session.get(User, user_id) if user_id is not None else None
    if user is None and user_id is not None:
        session.clear()
    return user


def login_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if current_user() is None:
            if request.path.startswith('/api/') or '/api/' in request.path:
                return jsonify({'error': 'Inicia sesión para continuar'}), 401
            return redirect(url_for('main.home'))
        return view(*args, **kwargs)

    return wrapped_view


def admin_required(view):
    @wraps(view)
    @login_required
    def wrapped_view(*args, **kwargs):
        user = current_user()
        if user is None or user.role != 'Administrador':
            if request.path.startswith('/api/') or '/api/' in request.path:
                return jsonify({'error': 'Se requieren permisos de administrador'}), 403
            return redirect(url_for('dashboard.index'))
        return view(*args, **kwargs)

    return wrapped_view
