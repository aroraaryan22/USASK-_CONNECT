import os

from flask import Flask
from flask_socketio import SocketIO
from werkzeug.exceptions import abort
from werkzeug.utils import secure_filename
from . import database
from . import auth
from . import blog
from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)


def create_app(test_config=None):
    # Configure key and database file

    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='aryan',
        DATABASE=os.path.join(app.instance_path, '404.sqlite'),

    )
    socketio = SocketIO(app)

    # Implement chat with socketio

    def messageReceived(methods=['GET', 'POST']):
        print('message was received!!!')

    @socketio.on('my event')
    def handle_my_custom_event(json, methods=['GET', 'POST']):
        print('received my event: ' + str(json))
        socketio.emit('my response', json, callback=messageReceived)

    if __name__ == '__main__':
        socketio.run(app, debug=True)

    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Configuring blueprint module with templates

    database.init_app(app)
    app.register_blueprint(auth.bluePrint)
    app.register_blueprint(blog.bluePrint)
    app.add_url_rule('/', endpoint='index')

    return app
