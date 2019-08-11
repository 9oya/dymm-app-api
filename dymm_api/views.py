from flask import Blueprint

from dymm_api import app

test_view = Blueprint('test_view', __name__, url_prefix='')


@test_view.route('/')
def hello_world():
    return 'Hello World!'
