import sqlite3
import click
from flask import current_app
from flask import g


def get_db():

    # Connect to sqlite database

    if 'database' not in g:
        g.database = sqlite3.connect(current_app.config['DATABASE'], detect_types=sqlite3.PARSE_DECLTYPES)
        g.database.row_factory = sqlite3.Row

    return g.database


def close_db(e=None):
    database = g.pop('database', None)

    if database is not None:
        database.close()


def init_db():

    # Initialize database for first run

    database = get_db()

    with current_app.open_resource('schema.sql') as f:
        database.executescript(f.read().decode('utf8'))


@click.command('init-db')
def init_db_command():
    init_db()
    click.echo('Database initialized!')


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
