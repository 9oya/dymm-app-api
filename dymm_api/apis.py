from flask import request, render_template, Blueprint
from flask_jwt_extended import (create_access_token, get_jwt_identity,
                                jwt_refresh_token_required, jwt_required)

from dymm_api import b_crypt
from .errors import ok, forbidden, bad_req, unauthorized
from .patterns import (MsgPattern, RegExPattern, ErrorPattern, TagType,
                       BookmarkSuperTag, TagClass)
from .schemas import Schema, validate_schema
from .mail import (confirm_mail_token, send_conf_mail, send_verif_mail,
                   verify_mail_code)
from .helpers import Helpers, str_to_bool

avt_api = Blueprint('avt_api', __name__, url_prefix='/api/avatar')
bnr_api = Blueprint('bnr_api', __name__, url_prefix='/api/banner')
mail_api = Blueprint('mail_api', __name__, url_prefix='/api/mail')
tag_api = Blueprint('tag_api', __name__, url_prefix='/api/tag')
_m = MsgPattern()
_r = RegExPattern()
_e = ErrorPattern()
_h = Helpers()
_s = Schema()


# GET services
# -----------------------------------------------------------------------------
@avt_api.route('/<int:avatar_id>', methods=['GET'])
@jwt_required
def fetch_a_avatar(avatar_id=None):
    if avatar_id is None:
        return bad_req(_m.EMPTY_PARAM.format('avatar_id'))
    avatar = _h.get_a_avatar(avatar_id)
    avatar_js = _h.convert_a_avatar_into_js(avatar)
    return ok(avatar_js)


@avt_api.route('/<int:avatar_id>/profile', methods=['GET'])
@jwt_required
def fetch_avatar_profile(avatar_id=None):
    if avatar_id is None:
        return bad_req(_m.EMPTY_PARAM.format('avatar_id'))
    avatar = _h.get_a_avatar(avatar_id)
    if not avatar.is_confirmed:
        return unauthorized(pattern=_e.MAIL_NEED_CONF, message=avatar.email)
    avatar_js = _h.convert_a_avatar_into_js(avatar)
    profile_tags = _h.get_profile_tags(avatar_id)
    profile_tag_jss = _h.convert_profile_tag_into_js(profile_tags)
    profile = dict(avatar=avatar_js,
                   profile_tags=profile_tag_jss)
    return ok(profile)


@avt_api.route('/<int:avatar_id>/cond', methods=['GET'])
@jwt_required
def fetch_avatar_cond_list(avatar_id=None):
    if avatar_id is None:
        return bad_req(_m.EMPTY_PARAM.format('avatar_id'))
    avt_cond_list = _h.get_avt_cond_list(avatar_id)
    avt_cond_list_js = _h.convert_avt_cond_list_into_js(avt_cond_list)
    return ok(avt_cond_list_js)


@avt_api.route('/<int:avatar_id>/group/<int:year_number>/<int:month_number>/'
               '<int:week_of_year>', methods=['GET'])
@avt_api.route('/<int:avatar_id>/group/<int:year_number>/<int:month_number>',
               methods=['GET'])
@jwt_required
def fetch_log_groups(avatar_id=None, year_number=None, month_number=None,
                     week_of_year=None):
    if not avatar_id:
        return bad_req(_m.EMPTY_PARAM.format('avatar_id'))
    if not year_number:
        return bad_req(_m.EMPTY_PARAM.format('year_number'))
    if not month_number:
        return bad_req(_m.EMPTY_PARAM.format('month_number'))
    if len(str(year_number)) != 4 or year_number < 1960:
        return bad_req(_m.BAD_PARAM.format('year_number'))
    if month_number < 1 or month_number > 12:
        return bad_req(_m.BAD_PARAM.format('month_number'))
    if week_of_year:
        if week_of_year < 1 or week_of_year > 54:
            return bad_req(_m.BAD_PARAM.format('week_of_year'))
    log_groups = _h.get_log_groups(avatar_id, year_number, month_number,
                                   week_of_year)
    log_groups_js = _h.convert_log_groups_into_js(log_groups)
    return ok(log_groups_js)


@avt_api.route('/<int:avatar_id>/group-note/<int:page>')
def fetch_log_group_notes(avatar_id=None, page=None):
    if avatar_id is None:
        return bad_req(_m.EMPTY_PARAM.format('avatar_id'))
    if page is None:
        bad_req(_m.EMPTY_PARAM.format('page'))
    log_groups = _h.get_log_group_notes(avatar_id, page)
    log_groups_js = _h.convert_log_groups_into_js(log_groups)
    return ok(log_groups_js)


@avt_api.route('/group/<int:group_id>/log', methods=['GET'])
@jwt_required
def fetch_group_of_logs(group_id=None):
    if not group_id:
        return bad_req(_m.EMPTY_PARAM.format('group_id'))
    log_group = _h.get_a_log_group(group_id)
    logs_js = dict(group_id=log_group.id)
    if log_group.food_cnt > 0:
        food_logs = _h.get_tag_logs(log_group.id, TagType.food)
        logs_js['food_logs'] = _h.convert_tag_logs_into_js(food_logs)
    if log_group.act_cnt > 0:
        act_logs = _h.get_tag_logs(log_group.id, TagType.activity)
        logs_js['act_logs'] = _h.convert_tag_logs_into_js(act_logs)
    if log_group.drug_cnt > 0:
        drug_logs = _h.get_tag_logs(log_group.id, TagType.drug)
        logs_js['drug_logs'] = _h.convert_tag_logs_into_js(drug_logs)
    if log_group.cond_score is not None:
        logs_js['cond_score'] = log_group.cond_score
    return ok(logs_js)


@avt_api.route('/<int:avatar_id>/group/<int:year_number>/<int:month_number>/'
               'avg-score', methods=['GET'])
@jwt_required
def fetch_log_group_avg_cond_score_per_month(avatar_id=None, year_number=None,
                                             month_number=None):
    this_avg = _h.get_avg_score_per_month(avatar_id, year_number, month_number)
    if month_number == 1:
        year_number -= year_number
        month_number = 12
    else:
        month_number -= 1
    last_avg = _h.get_avg_score_per_month(avatar_id, year_number, month_number)
    if this_avg.avg_score is None:
        this_avg = "0.000"
    else:
        this_avg = str(this_avg.avg_score)
    if last_avg.avg_score is None:
        last_avg = "0.000"
    else:
        last_avg = str(last_avg.avg_score)
    return ok(dict(
        this_month_score=this_avg,
        last_month_score=last_avg
    ))


@bnr_api.route('', methods=['GET'])
def fetch_banners():
    banners = _h.get_banners()
    banners_js = _h.convert_banners_into_js(banners)
    return ok(data=banners_js)


@mail_api.route('/conf/<token>', methods=['GET'])
def confirm_mail_token_service(token=None):
    if token is None:
        return bad_req()
    try:
        email = confirm_mail_token(token)
    except ValueError:
        return 'The confirmation link is invalid or has expired.'
    avatar = _h.get_a_avatar(email=email)
    if not avatar:
        return forbidden(_e.USER_INVALID)
    if avatar.is_confirmed:
        return 'Account already confirmed. Enjoy Dymm :)'
    if not _h.update_avatar_mail_confirm(avatar.id):
        return ('Sorry, email confirmation process has been failed :( <br/>'
                'Please try again.')
    return render_template(
        'mail_conf_result.html',
        message='Your email address has successfully confirmed!'
    )


@tag_api.route('/<int:tag_id>/set/<sort_type>', methods=['GET'])
@tag_api.route('/<int:tag_id>/set/<sort_type>/page/<int:page>',
               methods=['GET'])
@tag_api.route('/<int:tag_id>/set/<sort_type>/avt/<int:avatar_id>/'
               'page/<int:page>', methods=['GET'])
def fetch_tag_sets(tag_id=None, sort_type=None, avatar_id=None, page=None):
    if tag_id is None:
        return bad_req(_m.EMPTY_PARAM.format('tag_id'))
    tag = _h.get_a_tag(tag_id)
    tag_js = _h.convert_a_tag_into_js(tag)
    if avatar_id and tag.tag_type == TagType.history:
        log_histories = _h.get_log_histories(avatar_id)
        log_histories_js = _h.convert_log_histories_into_js(log_histories)
        return ok(dict(tag=tag_js, sub_tags=log_histories_js))
    if avatar_id and tag.tag_type == TagType.bookmark:
        if (tag.id == BookmarkSuperTag.food
                or tag.id == BookmarkSuperTag.activity
                or tag.id == BookmarkSuperTag.drug
                or tag.id == BookmarkSuperTag.condition):
            bookmarks = _h.get_bookmarks(avatar_id, tag.id)
            bookmarks_js = _h.convert_bookmarks_into_js(bookmarks)
            return ok(dict(tag=tag_js, sub_tags=bookmarks_js))
    if tag.class1 == TagClass.drug and tag.division1 != 0:
        sort_type = 'eng'
    tag_sets = _h.get_tag_sets(tag.id, sort_type, page)
    tag_sets_js = _h.convert_tag_sets_into_js(tag_sets)
    bookmarks_total = _h.get_bookmarks_total(tag_id)
    if avatar_id:
        if (tag.tag_type == TagType.food
                or tag.tag_type == TagType.activity
                or tag.tag_type == TagType.drug
                or tag.tag_type == TagType.condition):
            bookmark = _h.get_a_bookmark(avatar_id=avatar_id, tag_id=tag_id)
            if bookmark:
                return ok(dict(tag=tag_js, sub_tags=tag_sets_js,
                               bookmark_id=bookmark.id,
                               bookmarks_total=bookmarks_total))
    return ok(dict(tag=tag_js, sub_tags=tag_sets_js,
                   bookmarks_total=bookmarks_total))


@tag_api.route('/<int:tag_id>/set/match/<is_selected>', methods=['GET'])
@jwt_required
def fetch_tag_sets_w_matching_idx(tag_id=None, is_selected=None):
    if tag_id is None:
        return bad_req(_m.EMPTY_PARAM.format('fact_id'))
    if not str_to_bool(is_selected):
        tag_sets = _h.get_tag_sets(tag_id, 'priority')
        tags_js, matching_idx = _h.convert_tag_sets_into_js_add_idx(
            tag_sets, tag_id)
        return ok(dict(sub_tags=tags_js, select_idx=matching_idx))
    super_tag = _h.get_a_super_tag(tag_id)
    tag_sets = _h.get_tag_sets(super_tag.id, 'priority')
    tags_js, matching_idx = _h.convert_tag_sets_into_js_add_idx(
        tag_sets, tag_id)
    return ok(dict(sub_tags=tags_js, select_idx=matching_idx))


# POST services
# -----------------------------------------------------------------------------
@avt_api.route('/auth', methods=['POST'])
def auth_old_avatar():
    result = validate_schema(request.get_json(), _s.auth_avatar)
    if not result['ok']:
        return bad_req(result['message'])
    data = result['data']
    try:
        avatar_id = data['id']
        avatar = _h.get_a_avatar(avatar_id=avatar_id)
        if not avatar:
            avatar = _h.get_a_avatar(email=data['email'])
    except KeyError:
        avatar = _h.get_a_avatar(email=data['email'])
    if not avatar:
        return unauthorized(_e.MAIL_INVALID)
    if not b_crypt.check_password_hash(avatar.password_hash, data['password']):
        return unauthorized(_e.PASS_INVALID)
    avatar_js = _h.convert_a_avatar_into_js(avatar)
    profile_tags = _h.get_profile_tags(avatar.id)
    auth = dict(avatar=avatar_js, language_id=profile_tags[0].tag_id)
    return ok(auth)


@avt_api.route('/create', methods=['POST'])
def create_new_avatar():
    result = validate_schema(request.get_json(), _s.create_avatar)
    if not result['ok']:
        return bad_req(result['message'])
    data = result['data']
    if _h.is_email_duplicated(data['email']):
        return unauthorized(_e.MAIL_DUP)
    avatar = _h.create_a_new_avatar(data)
    _h.create_def_profile_tags(avatar.id, data['language_id'])
    avatar_js = _h.convert_a_avatar_into_js(avatar)
    auth = dict(avatar=avatar_js, language_id=data['language_id'])
    send_conf_mail(avatar.email)
    return ok(auth)


@avt_api.route('/token/refresh', methods=['POST'])
@jwt_refresh_token_required
def refresh_access_token():
    current_user = get_jwt_identity()
    token = create_access_token(identity=current_user, fresh=False)
    return ok(token)


@avt_api.route('/email/<string:option>', methods=['POST'])
def find_old_email(option=None):
    result = validate_schema(request.get_json(), _s.avatar_email)
    if not result['ok']:
        return bad_req(result['message'])
    data = result['data']
    try:
        email = data['email']
    except KeyError:
        return bad_req(_m.EMPTY_PARAM.format('email'))
    if option == 'find':
        if _h.is_email_duplicated(email):
            return ok()
        else:
            return unauthorized(_e.MAIL_INVALID)
    if option == 'verify':
        send_verif_mail(email)
        return ok()
    elif option == 'code':
        if email == verify_mail_code(data['code']):
            return ok()
        else:
            return unauthorized(_e.CODE_INVALID)
    else:
        return bad_req(_m.EMPTY_PARAM.format('option'))


@avt_api.route('/cond', methods=['POST'])
@jwt_required
def post_avatar_cond():
    result = validate_schema(request.get_json(), _s.create_avatar_cond)
    if not result['ok']:
        return bad_req(result['message'])
    data = result['data']
    _h.create_cond_log(data)
    log_history = _h.get_a_log_history_even_inactive(data['avatar_id'],
                                                     data['tag_id'])
    if log_history:
        _h.update_log_history_date(log_history)
    else:
        _h.create_a_log_history(data['avatar_id'], data['tag_id'])
    return ok()


@avt_api.route('/bookmark', methods=['POST'])
@jwt_required
def post_bookmark():
    result = validate_schema(request.get_json(), _s.create_bookmark)
    if not result['ok']:
        return bad_req(result['message'])
    data = result['data']
    try:
        avatar_id = data['avatar_id']
    except KeyError:
        return bad_req(_m.EMPTY_PARAM.format('avatar_id'))
    try:
        tag_type = data['tag_type']
    except KeyError:
        return bad_req(_m.EMPTY_PARAM.format('tag_type'))
    try:
        sub_id = data['tag_id']
    except KeyError:
        return bad_req(_m.EMPTY_PARAM.format('tag_id'))
    bookmark = _h.get_a_bookmark_include_inactive(avatar_id, sub_id)
    if bookmark:
        _h.update_bookmark_is_active(bookmark)
        bookmark_id = bookmark.id
    else:
        super_id = _h.get_bookmark_super_tag_id(tag_type)
        if not super_id:
            return bad_req(_m.BAD_PARAM.format('tag_type'))
        bookmark_id = _h.create_a_bookmark(avatar_id, super_id, sub_id)
    bookmarks_total = _h.get_bookmarks_total(sub_id)
    return ok(dict(bookmark_id=bookmark_id, bookmarks_total=bookmarks_total))


@avt_api.route('/log', methods=['POST'])
@jwt_required
def post_new_log():
    result = validate_schema(request.get_json(), _s.create_log)
    if not result['ok']:
        return bad_req(result['message'])
    data = result['data']
    _h.create_log(data)
    log_history = _h.get_a_log_history_even_inactive(data['avatar_id'],
                                                     data['tag_id'])
    if log_history:
        _h.update_log_history_date(log_history)
    else:
        _h.create_a_log_history(data['avatar_id'], data['tag_id'])
    return ok()


@mail_api.route('/conf-link', methods=['POST'])
@jwt_required
def send_mail_confirm_link_again():
    result = validate_schema(request.get_json(), _s.mail_conf_link)
    if not result['ok']:
        return bad_req(result['message'])
    data = result['data']
    try:
        avatar_id = data['avatar_id']
    except KeyError:
        return bad_req(_m.EMPTY_PARAM.format('avatar_id'))
    avatar = _h.get_a_avatar(avatar_id=avatar_id)
    if not avatar:
        return forbidden(_e.USER_INVALID)
    send_conf_mail(avatar.email)
    return ok()


@tag_api.route('/<int:tag_id>/search/page/<int:page>', methods=['POST'])
def search_tags(tag_id=None, page=None):
    if tag_id is None:
        return bad_req(_m.EMPTY_PARAM.format('tag_id'))
    if page is None:
        return bad_req(_m.EMPTY_PARAM.format('page'))
    result = validate_schema(request.get_json(), _s.search_key_word)
    if not result['ok']:
        return bad_req(result['message'])
    data = result['data']
    super_tag = _h.get_a_tag(tag_id)
    tag_js = _h.convert_a_tag_into_js(super_tag)
    tags = _h.search_low_div_tags_from_up_div_tag(super_tag, data['key_word'],
                                                  page)
    tags_js = _h.convert_tags_into_js(tags)
    return ok(dict(tag=tag_js, sub_tags=tags_js))


# PUT services
# -----------------------------------------------------------------------------
@avt_api.route('', methods=['PUT'])
@jwt_required
def put_avatar_info():
    result = validate_schema(request.get_json(), _s.update_avatar)
    if not result['ok']:
        return bad_req(result['message'])
    data = result['data']
    try:
        old_password = data['old_password']
        avatar = _h.get_a_avatar(data['avatar_id'])
        if not b_crypt.check_password_hash(avatar.password_hash, old_password):
            return unauthorized(_e.PASS_INVALID)
        _h.update_avatar_info(avatar.id, data['target'],
                              data['new_info'])
    except KeyError:
        _h.update_avatar_info(data['avatar_id'], data['target'],
                              data['new_info'])
    return ok()


@avt_api.route('/profile/<int:profile_tag_id>/<int:tag_id>', methods=['PUT'])
@jwt_required
def put_a_profile_tag(profile_tag_id=None, tag_id=None):
    if profile_tag_id is None:
        return bad_req(_m.EMPTY_PARAM.format('avatar_fact_id'))
    if tag_id is None:
        return bad_req(_m.EMPTY_PARAM.format('new_fact_id'))
    is_selected = True
    if _h.is_x_super_got_y_sub(19, tag_id):
        is_selected = False
    profile_tag = _h.get_a_profile_tag(profile_tag_id)
    _h.update_profile_tag(profile_tag, tag_id, is_selected)
    return ok()


@avt_api.route('/cond/<int:avatar_cond_id>', methods=['PUT'])
@jwt_required
def put_avatar_cond(avatar_cond_id=None):
    if avatar_cond_id is None:
        return bad_req(_m.EMPTY_PARAM.format('avatar_cond_id'))
    avatar_cond = _h.get_a_avatar_cond(avatar_cond_id)
    _h.update_avatar_cond_is_active(avatar_cond)
    return ok()


@avt_api.route('/<int:avatar_id>/bookmark/<int:bookmark_id>', methods=['PUT'])
@jwt_required
def put_bookmark(avatar_id=None, bookmark_id=None):
    if not avatar_id:
        return bad_req(_m.EMPTY_PARAM.format('avatar_id'))
    if not bookmark_id:
        return bad_req(_m.EMPTY_PARAM.format('bookmark_id'))
    bookmark = _h.get_a_bookmark(bookmark_id)
    _h.update_bookmark_is_active(bookmark)
    bookmarks_total = _h.get_bookmarks_total(bookmark.sub_tag_id)
    return ok(bookmarks_total)


@avt_api.route('/group/<int:group_id>/<option>', methods=['PUT'])
@jwt_required
def put_log_group(group_id=None, option=None):
    if group_id is None:
        return bad_req(_m.EMPTY_PARAM.format('group_id'))
    log_group = _h.get_a_log_group(group_id)
    if option == 'remove':
        _h.update_log_group_is_active(log_group)
        return ok()
    result = validate_schema(request.get_json(), _s.update_log_group)
    if not result['ok']:
        return bad_req(result['message'])
    data = result['data']
    if option == 'score':
        _h.update_log_group_cond_score(log_group, data['cond_score'])
        return ok()
    elif option == 'note':
        _h.update_log_group_note(log_group, data['note_txt'])
        return ok()
    else:
        return bad_req(_m.BAD_PARAM)


@avt_api.route('/log/<int:tag_log_id>', methods=['PUT'])
@jwt_required
def put_a_group_of_log(tag_log_id=None):
    if tag_log_id is None:
        return bad_req(_m.EMPTY_PARAM.format('tag_log_id'))
    tag_log = _h.get_a_tag_log(tag_log_id)
    _h.update_tag_log(tag_log)
    log_group = _h.get_a_log_group(tag_log.group_id)
    _h.update_log_group_log_cnt(log_group, tag_log.tag.tag_type)
    return ok()
