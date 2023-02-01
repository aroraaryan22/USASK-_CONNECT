import functools

from flask import (Blueprint, flash, g, redirect, render_template, request, session, url_for)
from werkzeug.security import check_password_hash, generate_password_hash
from flaskProject.database import get_db

bluePrint = Blueprint('auth', __name__, url_prefix='/auth')


@bluePrint.route('/register', methods=('GET', 'POST'))
def register():
    # Fetching values from registration form

    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        age = request.form['age']
        database = get_db()
        error = None

        # Checking if all values are satisfied

        if not username:
            error = 'Username is required!'
        elif not password:
            error = 'Password is required!'
        elif not email:
            error = 'E-Mail is required!'
        elif not first_name:
            error = 'First Name is required!'
        elif not last_name:
            error = 'Last Name is required!'
        elif not age:
            error = 'Age is required!'
        elif not username or not password or not email or not first_name or not last_name or not age:
            error = 'Check for missing fields!'

        # Storing form values in sqlite database with password hashing for security

        if error is None:
            try:
                database.execute('INSERT INTO user (username, email, password, first_name, last_name, age)'
                                 'VALUES (?, ?, ?, ?, ?, ?)',
                                 (username, email, generate_password_hash(password), first_name, last_name, age),
                                 )
                database.commit()
            # Exception for registered users
            except database.IntegrityError:
                error = f"User {username} is already registered."
            else:
                # Redirecting to login page
                return redirect(url_for('auth.login'))

        flash(error)

    return render_template('auth/register.html')


@bluePrint.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        database = get_db()
        error = None

        # Validating credentials from database

        user = database.execute('SELECT * FROM user WHERE username = ?', (username,)).fetchone()

        if user is None:
            error = 'Incorrect username!'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password!'

        if error is None:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('blog.home'))
        flash(error)

    return render_template('auth/login.html')


@bluePrint.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        # Get username from database
        g.user = get_db().execute('SELECT * FROM user WHERE id = ?', (user_id,)).fetchone()


@bluePrint.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view


@bluePrint.route('/profile')
def profile():
    return render_template("auth/profile.html")


@bluePrint.route('/feedback')
def feedback():
    return render_template("auth/feedback.html")


@bluePrint.route('/about')
def about():
    return render_template("auth/about.html")
