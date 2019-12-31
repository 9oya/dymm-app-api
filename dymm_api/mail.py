import secrets

from flask import render_template, session
from flask_mail import Message
from itsdangerous import URLSafeTimedSerializer

from dymm_api import app, mail
from .patterns import URIPattern, TagId

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


def verify_mail_code(verif_code: str):
    return session.pop(verif_code.lower(), None)


def send_conf_mail(mail_address):
    message = Message()
    message.add_recipient(mail_address)
    mail_token = generate_confirmation_token(mail_address)
    uri = _u.HOST + '/api/mail/conf/' + mail_token
    message.html = render_template('mail_conf_msg.html', uri=uri)
    message.subject = "Verify your Dymm email address"
    mail.send(message)


def new_send_conf_mail(mail_address, lang_id):
    message = Message()
    message.add_recipient(mail_address)
    mail_token = generate_confirmation_token(mail_address)
    uri = _u.HOST + '/api/mail/conf/' + mail_token
    message.html = render_template('new_mail_conf_msg.html', lang_id=lang_id,
                                   uri=uri)
    if lang_id == TagId.kor:
        message.subject = "딤Dymm 이메일 주소를 확인해주세요."
    else:
        message.subject = "Verify your Dymm email address."
    mail.send(message)


def send_verif_mail(mail_address):
    message = Message()
    message.add_recipient(mail_address)
    verif_code = generate_verification_code(mail_address)
    message.html = render_template('mail_verification.html',
                                   mail_address=mail_address,
                                   verif_code=verif_code.upper())
    message.subject = "Dymm Account Verification"
    mail.send(message)


def new_send_verif_mail(mail_address, lang_id):
    message = Message()
    message.add_recipient(mail_address)
    verif_code = generate_verification_code(mail_address)
    message.html = render_template('new_mail_verification.html',
                                   lang_id=lang_id,
                                   mail_address=mail_address,
                                   verif_code=verif_code.upper())
    if lang_id == TagId.kor:
        message.subject = "딤Dymm 계정 검증"
    else:
        message.subject = "Dymm Account Verification"
    mail.send(message)


def send_opinion_mail(data):
    message = Message()
    message.add_recipient('eido9oya@dymm.io')
    message.html = render_template('mail_user_opinion.html', data=data)
    message.subject = "Opinion from tag: {0} user: {1}".format(data["tag"].id,
                                                               data["avatar"].id)
    mail.send(message)
