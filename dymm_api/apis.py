import re

from flask import request, render_template, Blueprint
from flask_jwt_extended import (create_access_token, get_jwt_identity,
                                jwt_refresh_token_required, jwt_required)

from dymm_api import b_crypt
from errors import ok, forbidden, bad_req, unauthorized
from patterns import (MsgPattern, RegExPatter, ErrorPattern, TagType,
                      BookmarkSuperTag)
from schemas import (validate_schema, update_avatar_schema, create_log_schema,
                     auth_avatar_schema, create_avatar_schema,
                     create_cond_log_schema, update_cond_score_schema)
from mail import confirm_mail_token, send_mail
from helpers import Helpers, str_to_bool

api = Blueprint('api', __name__, url_prefix='/api')
_m = MsgPattern()
_r = RegExPatter()
_e = ErrorPattern()
_h = Helpers()


# GET services
# -----------------------------------------------------------------------------
@api.route('/mail/conf/<token>', methods=['GET'])
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


@api.route('<int:avatar_id>/mail/<email>/conf-link', methods=['GET'])
@jwt_required
def send_mail_confirm_link_again(avatar_id=None, email=None):
    if avatar_id is None:
        return bad_req(_m.EMPTY_PARAM.format('user_id'))
    if email is None:
        return bad_req(_m.EMPTY_PARAM.format('email'))
    if not re.match(_r.EMAIL, email):
        return bad_req(_m.BAD_PARAM.format('email'))
    avatar = _h.get_a_avatar(avatar_id=avatar_id)
    if not avatar:
        return forbidden(_e.USER_INVALID)
    send_mail(avatar.email)
    return ok()


@api.route('/banner', methods=['GET'])
def fetch_banners():
    banners = _h.get_banners()
    banners_js = _h.convert_banners_into_js(banners)
    return ok(data=banners_js)


@api.route('/tag/<int:tag_id>/set/<sort_type>', methods=['GET'])
@api.route('/tag/<int:tag_id>/set/<sort_type>/<int:avatar_id>',
           methods=['GET'])
def fetch_tag_sets(tag_id=None, sort_type=None, avatar_id=None):
    if tag_id is None:
        return bad_req(_m.EMPTY_PARAM.format('tag_id'))
    tag = _h.get_a_tag(tag_id)
    tag_js = _h.convert_a_tag_into_js(tag)
    if avatar_id and tag.tag_type == TagType.bookmark:
        if (tag.id == BookmarkSuperTag.food
                or tag.id == BookmarkSuperTag.activity
                or tag.id == BookmarkSuperTag.drug
                or tag.id == BookmarkSuperTag.condition):
            bookmarks = _h.get_bookmarks(avatar_id, tag.id)
            bookmarks_js = _h.convert_bookmarks_into_js(bookmarks)
            return ok(dict(tag=tag_js, sub_tags=bookmarks_js))
    tag_sets = _h.get_tag_sets(tag_id, sort_type)
    tag_sets_js = _h.convert_tag_sets_into_js(tag_sets)
    if avatar_id:
        if (tag.tag_type == TagType.food
                or tag.tag_type == TagType.activity
                or tag.tag_type == TagType.drug):
            bookmark = _h.get_a_bookmark(avatar_id=avatar_id, tag_id=tag_id)
            if bookmark:
                return ok(dict(tag=tag_js, sub_tags=tag_sets_js,
                               bookmark_id=bookmark.id))
    return ok(dict(tag=tag_js, sub_tags=tag_sets_js))


@api.route('/tag/<int:tag_id>/set/match/<is_selected>', methods=['GET'])
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


@api.route('/avatar/<int:avatar_id>/profile', methods=['GET'])
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


@api.route('/avatar/<int:avatar_id>', methods=['GET'])
@jwt_required
def fetch_a_avatar(avatar_id=None):
    if avatar_id is None:
        return bad_req(_m.EMPTY_PARAM.format('avatar_id'))
    avatar = _h.get_a_avatar(avatar_id)
    avatar_js = _h.convert_a_avatar_into_js(avatar)
    return ok(avatar_js)


@api.route('/avatar/<int:avatar_id>/cond', methods=['GET'])
@jwt_required
def fetch_avatar_cond_list(avatar_id=None):
    if avatar_id is None:
        return bad_req(_m.EMPTY_PARAM.format('avatar_id'))
    avt_cond_list = _h.get_avt_cond_list(avatar_id)
    avt_cond_list_js = _h.convert_avt_cond_list_into_js(avt_cond_list)
    return ok(avt_cond_list_js)


@api.route('/log/group/<int:avatar_id>/<int:year_number>/<int:month_number>/'
           '<int:week_of_year>', methods=['GET'])
@api.route('/log/group/<avatar_id>/<int:year_number>/<int:month_number>',
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


@api.route('/log/group/<int:group_id>/tag-log', methods=['GET'])
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
    if log_group.has_cond_score:
        logs_js['cond_score'] = log_group.cond_score
    return ok(logs_js)


# POST services
# -----------------------------------------------------------------------------
@api.route('/avatar', methods=['POST'])
def auth_existed_avatar():
    result = validate_schema(request.get_json(), auth_avatar_schema)
    if not result['ok']:
        return bad_req(result['message'])
    data = result['data']
    avatar = _h.get_a_avatar(email=data['email'])
    if not avatar:
        return unauthorized(_e.MAIL_INVALID)
    if not b_crypt.check_password_hash(avatar.password_hash, data['password']):
        return unauthorized(_e.PASS_INVALID)
    avatar_js = _h.convert_a_avatar_into_js(avatar)
    profile_tags = _h.get_profile_tags(avatar.id)
    auth = dict(avatar=avatar_js, language_id=profile_tags[0].tag_id)
    return ok(auth)


@api.route('/avatar/create', methods=['POST'])
def create_new_avatar():
    result = validate_schema(request.get_json(), create_avatar_schema)
    if not result['ok']:
        return bad_req(result['message'])
    data = result['data']
    if _h.is_email_duplicated(data['email']):
        return unauthorized(_e.MAIL_DUP)
    avatar = _h.create_a_new_avatar(data)
    _h.create_def_profile_tags(avatar.id, data['language_id'])
    avatar_js = _h.convert_a_avatar_into_js(avatar)
    auth = dict(avatar=avatar_js, language_id=data['language_id'])
    send_mail(avatar.email)
    return ok(auth)


@api.route('/avatar/token/refresh', methods=['POST'])
@jwt_refresh_token_required
def refresh_access_token():
    current_user = get_jwt_identity()
    token = create_access_token(identity=current_user, fresh=False)
    return ok(token)


@api.route('/log', methods=['POST'])
@jwt_required
def post_new_log():
    result = validate_schema(request.get_json(), create_log_schema)
    if not result['ok']:
        return bad_req(result['message'])
    data = result['data']
    _h.create_log(data)
    return ok()


@api.route('/log/cond', methods=['POST'])
@jwt_required
def post_cond_log():
    result = validate_schema(request.get_json(), create_cond_log_schema)
    if not result['ok']:
        return bad_req(result['message'])
    data = result['data']
    _h.create_cond_log(data)
    return ok()


@api.route('/avatar/<int:avatar_id>/bookmark/<int:tag_type>/<int:sub_id>',
           methods=['POST'])
@jwt_required
def post_bookmark(avatar_id=None, tag_type=None, sub_id=None):
    if not avatar_id:
        return bad_req(_m.EMPTY_PARAM.format('avatar_id'))
    if not tag_type:
        return bad_req(_m.EMPTY_PARAM.format('tag_type'))
    if not sub_id:
        return bad_req(_m.EMPTY_PARAM.format('sub_id'))
    bookmark = _h.get_a_bookmark_even_inactive(avatar_id, sub_id)
    if bookmark:
        _h.update_bookmark_is_active(bookmark)
        return ok(message=_m.OK_PUT.format('bookmark'))
    else:
        super_id = _h.get_bookmark_super_tag_id(tag_type)
        if not super_id:
            return bad_req(_m.BAD_PARAM.format('tag_type'))
        _h.create_a_bookmark(avatar_id, super_id, sub_id)
        return ok(message=_m.OK_POST.format('bookmark'))


# PUT services
# -----------------------------------------------------------------------------
@api.route('/avatar', methods=['PUT'])
@jwt_required
def put_avatar_info():
    result = validate_schema(request.get_json(), update_avatar_schema)
    if not result['ok']:
        return bad_req(result['message'])
    data = result['data']
    _h.update_avatar_info(data['avatar_id'], data['target'],
                          data['new_info'])
    return ok()


@api.route('/profile/<int:profile_tag_id>/<int:tag_id>', methods=['PUT'])
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


@api.route('/log/group/<int:group_id>/<option>', methods=['PUT'])
@jwt_required
def put_cond_score(group_id=None, option=None):
    if group_id is None:
        return bad_req(_m.EMPTY_PARAM.format('group_id'))
    log_group = _h.get_a_log_group(group_id)
    if option == 'cond-score':
        result = validate_schema(request.get_json(), update_cond_score_schema)
        if not result['ok']:
            return bad_req(result['message'])
        data = result['data']
        _h.update_log_group_cond_score(log_group, data)
        return ok()
    elif option == 'remove':
        _h.update_log_group_is_active(log_group)
        return ok()
    else:
        return bad_req(_m.BAD_PARAM)


@api.route('/log/<int:tag_log_id>', methods=['PUT'])
@jwt_required
def put_a_group_of_log(tag_log_id=None):
    if tag_log_id is None:
        return bad_req(_m.EMPTY_PARAM.format('group_id'))
    tag_log = _h.get_a_tag_log(tag_log_id)
    _h.update_tag_log(tag_log)
    log_group = _h.get_a_log_group(tag_log.group_id)
    _h.update_log_group_log_cnt(log_group, tag_log.tag.tag_type)
    return ok()


@api.route('/avatar/cond/<int:avatar_cond_id>', methods=['PUT'])
@jwt_required
def put_a_avatar_cond(avatar_cond_id=None):
    if avatar_cond_id is None:
        return bad_req(_m.EMPTY_PARAM.format('avatar_cond_id'))
    avatar_cond = _h.get_a_avatar_cond(avatar_cond_id)
    _h.update_avatar_cond_is_active(avatar_cond)
    return ok()


@api.route('/avatar/<int:avatar_id>/bookmark/<int:bookmark_id>',
           methods=['PUT'])
@jwt_required
def put_bookmark(avatar_id=None, bookmark_id=None):
    if not avatar_id:
        return bad_req(_m.EMPTY_PARAM.format('avatar_id'))
    if not bookmark_id:
        return bad_req(_m.EMPTY_PARAM.format('bookmark_id'))
    bookmark = _h.get_a_bookmark(bookmark_id)
    _h.update_bookmark_is_active(bookmark)
    return ok()
