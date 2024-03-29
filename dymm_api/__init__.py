from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from flask_mail import Mail

from .blueprint import register_blueprint
from .custom_jwt import customize_jwt

app = Flask('dymm_api')
app.config.from_object('dymm_api.config.ProductionConfig')
# app.config.from_object('dymm_api.config.DevelopmentConfig')

db = SQLAlchemy(app)
b_crypt = Bcrypt(app)
jwt = JWTManager(app)
mail = Mail(app)
register_blueprint(app)
customize_jwt(jwt)
