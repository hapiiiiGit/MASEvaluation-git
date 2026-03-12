import functools
from flask import session, redirect, url_for, flash, request
from src.models import User

def login_required(view_func):
    """
    Decorator to ensure the user is logged in before accessing the route.
    Redirects to login page if not authenticated.
    """
    @functools.wraps(view_func)
    def wrapped_view(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login', next=request.url))
        return view_func(*args, **kwargs)
    return wrapped_view

def admin_required(view_func):
    """
    Decorator to ensure the user is an admin before accessing the route.
    Redirects to login page if not authenticated or not admin.
    Assumes 'is_admin' attribute on User model (default: False).
    """
    @functools.wraps(view_func)
    def wrapped_view(*args, **kwargs):
        user_id = session.get('user_id')
        if not user_id:
            flash('Please log in to access the admin dashboard.', 'warning')
            return redirect(url_for('login', next=request.url))
        user = User.query.get(user_id)
        if not user or not getattr(user, 'is_admin', False):
            flash('You do not have permission to access this page.', 'danger')
            return redirect(url_for('index'))
        return view_func(*args, **kwargs)
    return wrapped_view