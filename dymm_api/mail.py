import secrets

from flask import render_template, session
from flask_mail import Message
from itsdangerous import URLSafeTimedSerializer

from dymm_api import app, mail
from patterns import URIPattern

_u = URIPattern()


def generate_confirmation_token(email):
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    return serializer.dumps(email, salt=app.config['SECURITY_PASSWORD_SALT'])


def generate_verification_code(email):
    verif_code = secrets.token_hex(3)
    session[verif_code] = email
    return verif_code


def confirm_mail_token(token, expiration=36000):
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    try:
        email = serializer.loads(
            token,
            salt=app.config['SECURITY_PASSWORD_SALT'],
            max_age=expiration)
    except:
        raise ValueError
    return email


def verify_mail_code(verif_code):
    if session.pop(verif_code, None):
        return True
    else:
        return False


def send_conf_mail(mail_address):
    message = Message()
    # TODO: message.add_recipient(email_address)
    message.add_recipient('eslee004@gmail.com')
    mail_token = generate_confirmation_token(mail_address)
    uri = _u.HOST + '/api/mail/conf/' + mail_token
    message.html = render_template('mail_conf_msg.html', uri=uri)
    message.subject = "Confirm your account on Dymm"
    mail.send(message)


def send_verif_mail(mail_address):
    message = Message()
    # TODO: message.add_recipient(email_address)
    message.add_recipient('eslee004@gmail.com')
    verif_code = generate_verification_code(mail_address)
    message.html = render_template('mail_verification.html',
                                   verif_code=verif_code.upper())
    message.subject = "Dymm Account Verification"
    mail.send(message)
