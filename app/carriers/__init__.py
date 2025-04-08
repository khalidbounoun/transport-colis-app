from flask import Blueprint

bp = Blueprint('carriers', __name__)

from app.carriers import routes