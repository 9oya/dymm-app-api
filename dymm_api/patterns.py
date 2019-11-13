class URIPattern:
    HOST = 'http://127.0.0.1:5000'
    # HOST = 'https://dymm-api-01.appspot.com'
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
    CODE_INVALID = 34

    SCORE_NONE = 41
    BIRTH_NONE = 42


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


class RegExPattern:
    NUMERIC_ID = '^[0-9]+$'
    EMAIL = '^[A-Za-z0-9\.\+_-]+@[A-Za-z0-9\._-]+\.[a-zA-Z]*$'
    year = '[1960-2200]'
    month = '[1-12]'
    week_of_year = '[1-54]'
    kor_name = '[가-힣]'


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


class TagClass:
    act = 2
    cond = 3
    drug = 4
    food = 5
    drug_abc = 7


class TagId:
    act = 2
    cond = 3
    drug = 4
    food = 5
    profile = 19
    language = 20
    gender = 22
    date_of_birth = 23
    supp = 1040
    eng = 30
    kor = 35
    male = 36
    female = 37
    password = 14641
    theme = 14645
    light = 14646


class BookmarkSuperTag:
    history = 24
    food = 25
    activity = 26
    drug = 27
    condition = 28


class AvatarInfo:
    first_name = 11
    last_name = 12
    email = 13
    ph_number = 14
    intro = 15
    color_code = 16
    photo_name = 17
    full_lifespan = 18
