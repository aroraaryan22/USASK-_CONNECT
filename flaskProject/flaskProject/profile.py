import functools

from flask import (Blueprint, flash, g, redirect, render_template, request, session, url_for)
from flaskProject.database import get_db
from flaskProject.auth import login_required


bluePrint = Blueprint('profile', __name__, url_prefix='/profile')


@bluePrint.route(g.user['username'])
@login_required
def profile():
    database = get_db()
