class URIPattern:
    HOST = 'http://127.0.0.1:5000'
    # HOST = 'https://dymm-api-test4.herokuapp.com'
    ASSET = 'dymm_api/static/asset'


class ErrorPattern:
    TOKEN_INVALID = 11
    TOKEN_EXPR = 12
    TOKEN_NEED_FRESH = 13

    MAIL_NEED_CONF = 21
    MAIL_DUP = 22

    USER_INVALID = 31
    MAIL_INVALID = 32
    PASS_INVALID = 33


class MsgPattern:
    BAD_PARAM = 'Bad request, Wrong pattern parameters has been passed.'
    EMPTY_PARAM = "Bad request, Parameter {} is Empty."
    EXPIRED = 'Forbidden, Expired token has been passed.'
    DUPLICATED = 'Forbidden, Duplicated {} has been passed.'
    NONEXISTENT = 'Forbidden, Can\' find matching id{}.'
    INCORRECT = 'Forbidden, That {} is incorrect.'
    INVALID = 'Forbidden, Invalid {} has been passed.'
    OK_POST = 'Ok, The {} has been posted.'
    OK_PUT = 'Ok, The {} has been updated.'
    OK_DELETE = 'Ok, The {} has been deleted.'
    OK_IMPORT = 'Ok, The {} {} data has been inserted.'
    OK_UPLOAD = 'Ok, The {} {} data has been uploaded.'
    OK_MODIFY = 'Ok, The {} {} data has been modified.'
    UN_AUTH = 'Unauthorized, Wrong {} has been passed.'


class RegExPatter:
    NUMERIC_ID = '^[0-9]+$'
    EMAIL = '^[A-Za-z0-9\.\+_-]+@[A-Za-z0-9\._-]+\.[a-zA-Z]*$'
    year = '[1960-2200]'
    month = '[1-12]'
    week_of_year = '[1-54]'


class CondLogType:
    start_date = 1
    end_date = 2


class TagType:
    activity = 7
    condition = 8
    drug = 9
    food = 10
    character = 11
    category = 12
    bookmark = 13
    diary = 14
    history = 15


class AvatarInfo:
    first_name = 11
    last_name = 12
    ph_number = 13
    profile_type = 14
    intro = 15
