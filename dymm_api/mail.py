from flask import render_template
from flask_mail import Message
from itsdangerous import URLSafeTimedSerializer

from dymm_api import app, mail
from patterns import URIPattern

_u = URIPattern()


def generate_confirmation_token(email):
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    return serializer.dumps(email, salt=app.config['SECURITY_PASSWORD_SALT'])


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


def send_mail(mail_address):
    # Generate email-conf-token and send to acct.email
    message = Message()
    # message.add_recipient(email_address)
    # TODO: Change below line with above.
    message.add_recipient('eslee004@gmail.com')
    mail_token = generate_confirmation_token(mail_address)
    uri = _u.HOST + '/api/mail/conf/' + mail_token
    message.html = render_template('mail_conf_msg.html', uri=uri)
    message.subject = "Confirm your account on Flava"
    mail.send(message)