from flask import render_template, redirect, url_for
from flask_login import login_required
from datetime import datetime
from app.main import bp

@bp.route('/')
@bp.route('/index')
def index():
    return render_template('index.html', title='Accueil', year=datetime.now().year)

@bp.route('/dashboard')
@login_required
def dashboard():
    return redirect(url_for('shipments.list_shipments'))