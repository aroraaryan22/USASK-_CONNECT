import os
import pathlib
import re
# import requests
import base64


from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort
from werkzeug.utils import secure_filename

from flaskProject.auth import login_required
from flaskProject.database import get_db

bluePrint = Blueprint('blog', __name__)


@bluePrint.route('/')
def home():
    return render_template('blog/home.html')


@bluePrint.route('/chat')
def chat():
    return render_template('blog/chat.html')


@bluePrint.route('/chatroom')
def chatroom():
    return render_template('blog/chatroom.html')


@bluePrint.route('/index')
def index():

    # Fetching posts created by users from the database

    database = get_db()
    posts = database.execute(
        'SELECT p.id, title, body, created, author_id, username, image'
        '  FROM post p JOIN user u ON p.author_id = u.id'
        '  ORDER BY created DESC'
    ).fetchall()

    return render_template('blog/index.html', posts=posts)


@bluePrint.route('/create', methods=('GET', 'POST'))
@login_required
def create():

    # Logging post arguments in database
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        image = request.files['image']

        # Storing image file on server
        filename = secure_filename(image.filename)
        mimetype = image.mimetype

        if image.filename != '':
            image.save(image.filename)

        # Converting image file to readable base64 format
        with open(filename, 'rb') as f:
            my_image = base64.b64encode(f.read())

        my_image_decoded = my_image.decode('utf-8')

        error = None

        if not title:
            error = 'Title required!'
        if error is not None:
            flash(error)
        else:
            database = get_db()
            database.execute(
                'INSERT INTO post (title, body, author_id, image)'
                '  VALUES (?, ?, ?, ?)',
                (title, body, g.user['id'], my_image_decoded)
            )
            database.commit()
            # Deleting image file from server after it's been stored in the database
            os.remove(filename)
            return redirect(url_for('blog.index'))

    return render_template('blog/create.html')


def get_post(id, check_author=True):
    post = get_db().execute(
        'SELECT p.id, title, body, created, author_id, username'
        '  FROM post p JOIN user u ON p.author_id = u.id'
        '  WHERE p.id = ?',
        (id,)
    ).fetchone()

    if post is None:
        abort(404, f"Post id {id} doesn't exist!")

    if check_author and post['author_id'] != g.user['id']:
        abort(403)

    return post


@bluePrint.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    post = get_post(id)

    # New arguments for update post
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']

        error = None

        if not title:
            error = 'Title required!'

        if error is not None:
            flash(error)
        else:
            database = get_db()
            database.execute(
                'UPDATE post SET title = ?, body = ?'
                '  WHERE id = ?',
                (title, body, id)
            )
            database.commit()
            return redirect(url_for('blog.index'))

    return render_template('blog/update.html', post=post)


@bluePrint.route('/<int:id>/delete', methods=('GET', 'POST'))
@login_required
def delete(id):

    # Deleting a post from the database

    get_post(id)
    database = get_db()
    database.execute(
        'DELETE FROM post WHERE id = ?',
        (id,)
    )
    database.commit()
    return redirect(url_for('blog.index'))
