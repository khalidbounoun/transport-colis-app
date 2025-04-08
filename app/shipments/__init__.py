from flask import Blueprint

bp = Blueprint('shipments', __name__)

from app.shipments import routes