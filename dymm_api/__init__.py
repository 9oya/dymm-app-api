from flask import Flask
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy

from blueprint import register_blueprint
# from database import db_session
from custom_jwt import customize_jwt

app = Flask('dymm_api')
app.config.from_object('dymm_api.config.ProductionConfig')
# app.config.from_object('dymm_api.config.DevelopmentConfig')

db = SQLAlchemy(app)
b_crypt = Bcrypt(app)
jwt = JWTManager(app)
mail = Mail(app)
register_blueprint(app)
customize_jwt(jwt)


# @app.teardown_appcontext
# def shutdown_session(exception=None):
#     db_session.remove()


# if __name__ == "__main__":
#     context = ('cert.crt', 'key.key')
#     app.run(host='127.0.0.1',
#             port=5000,
#             ssl_context=context,
#             threaded=True,
#             debug=True)
