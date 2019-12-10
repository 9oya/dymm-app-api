import os, datetime, pytz
from flask import request, render_template, Blueprint, send_file, send_from_directory
from flask_jwt_extended import (create_access_token, get_jwt_identity,
                                jwt_refresh_token_required, jwt_required)
from google.cloud import storage
import tempfile

from dymm_api import b_crypt
from .errors import ok, forbidden, bad_req, unauthorized
from .patterns import (MsgPattern, RegExPattern, ErrorPattern, TagType,
                       BookmarkSuperTag, TagClass, TagId, AvatarInfo)
from .schemas import Schema, validate_schema
from .mail import (confirm_mail_token, send_conf_mail, send_verif_mail,
                   verify_mail_code, send_opinion_mail)
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
    if avatar is None:
        return unauthorized(_e.USER_INVALID)
    avatar_js = _h.convert_a_avatar_into_js(avatar)
    lang_profile_tag = _h.get_a_lang_profile_tag(avatar_id)
    if lang_profile_tag is None:
        lang_profile_tag = _h.create_profile_tag(avatar_id, TagId.language,
                                                 TagId.eng, True)
    auth = dict(avatar=avatar_js, language_id=lang_profile_tag.sub_tag_id)
    return ok(auth)


@avt_api.route('/<int:avatar_id>/profile', methods=['GET'])
@jwt_required
def fetch_avatar_profile(avatar_id=None):
    if avatar_id is None:
        return bad_req(_m.EMPTY_PARAM.format('avatar_id'))
    avatar = _h.get_a_avatar(avatar_id)
    if not avatar.is_confirmed:
        return unauthorized(pattern=_e.MAIL_NEED_CONF, message=avatar.email)
    avatar_js = _h.convert_a_avatar_into_js(avatar)

    set_of_profile_tags = _h.get_tag_sets(TagId.profile, sort_type='priority')
    profile_tags = _h.get_valid_profile_tags(avatar_id, set_of_profile_tags)
    profile_tag_js_list = _h.convert_profile_tag_into_js(profile_tags)
    lang_profile_tag = _h.get_a_lang_profile_tag(avatar_id)
    profile = dict(avatar=avatar_js, language_id=lang_profile_tag.sub_tag_id,
                   profile_tags=profile_tag_js_list)
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


@avt_api.route('/<int:avatar_id>/group/<int:year_number>/avg-score',
               methods=['GET'])
@avt_api.route('/<int:avatar_id>/group/<int:year_number>/<int:month_number>/'
               'avg-score', methods=['GET'])
@avt_api.route('/<int:avatar_id>/group/<int:year_number>/<int:month_number>/'
               '<int:week_of_year>/avg-score', methods=['GET'])
@jwt_required
def fetch_log_group_avg_cond_score(avatar_id=None, year_number=None,
                                   month_number=None,
                                   week_of_year=None):
    if month_number is None:
        avg_score = _h.get_avg_score_per_year(avatar_id, year_number)
        if avg_score.avg_score is None:
            this_avg = "0.000"
        else:
            this_avg = str(avg_score.avg_score)
        return ok(dict(
            this_avg_score=this_avg
        ))
    if week_of_year:
        this_avg = _h.get_avg_score_per_week(avatar_id, year_number,
                                             week_of_year)
        if week_of_year == 1:
            week_of_year = 52
            year_number -= year_number
        else:
            week_of_year -= 1
        last_avg = _h.get_avg_score_per_week(avatar_id, year_number,
                                             week_of_year)
    else:
        this_avg = _h.get_avg_score_per_month(avatar_id, year_number,
                                              month_number)
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
        this_avg_score=this_avg,
        last_avg_score=last_avg
    ))


@avt_api.route('/<int:avatar_id>/group/<int:year_number>/score-board',
               methods=['GET'])
@avt_api.route('/<int:avatar_id>/group/<int:year_number>/<int:month_number>/'
               'score-board', methods=['GET'])
@jwt_required
def fetch_main_score_board_info(avatar_id=None, year_number=None,
                                month_number=None):
    if avatar_id is None:
        return bad_req(_m.EMPTY_PARAM.format('avatar_id'))
    if month_number:
        this_avg_score = _h.get_avg_score_per_month(avatar_id, year_number,
                                                    month_number)
    else:
        this_avg_score = _h.get_avg_score_per_year(avatar_id, year_number)
    if this_avg_score.avg_score is None:
        this_avg_score = "0.000"
    else:
        this_avg_score = str(this_avg_score.avg_score)
    avatar = _h.get_a_avatar(avatar_id)
    if avatar is None:
        return unauthorized(_e.USER_INVALID)
    gender_profile_tag = _h.get_a_gender_profile_tag(avatar_id)
    if gender_profile_tag is None:
        gender_profile_tag = _h.create_profile_tag(avatar_id, TagId.gender,
                                                   TagId.gender, False)
    gender_tag_js = _h.convert_a_tag_into_js(gender_profile_tag.sub_tag)
    return ok(dict(
        avg_score=this_avg_score,
        date_of_birth=avatar.date_of_birth,
        gender_tag=gender_tag_js
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
@tag_api.route('/<int:tag_id>/set/<sort_type>/page/<int:page>/lang/'
               '<int:lang_id>', methods=['GET'])
@tag_api.route('/<int:tag_id>/set/<sort_type>/avt/<int:avatar_id>/'
               'page/<int:page>/lang/<int:lang_id>', methods=['GET'])
def fetch_tag_sets(tag_id=None, sort_type=None, avatar_id=None, page=None,
                   lang_id=None):
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
    elif tag.class1 == TagClass.drug_abc and tag.division1 != 0:
        sort_type = 'div'
    if lang_id is None:
        tag_sets = _h.get_tag_sets(tag.id, sort_type, page)
    else:
        tag_sets = _h.get_tag_sets(tag.id, sort_type, page, lang_id=lang_id)
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


@avt_api.route('/<int:avatar_id>/profile/photo/<photo_name>')
def download_blob(avatar_id=None, photo_name=None):
    if avatar_id is None:
        return bad_req(_m.EMPTY_PARAM.format('avatar_id'))
    client = storage.Client()
    bucket = client.get_bucket(os.environ['CLOUD_STORAGE_BUCKET'])
    pathname = 'avatar/profile/'
    filename = photo_name
    blob = bucket.blob(pathname + filename)
    with tempfile.NamedTemporaryFile() as temp:
        blob.download_to_filename(temp.name)
        return send_file(temp.name, attachment_filename=filename)


@avt_api.route('/<int:avatar_id>/life-span', methods=['GET'])
def fetch_remaining_life_span(avatar_id=None):
    if avatar_id is None:
        return bad_req(_m.EMPTY_PARAM.format('avatar_id'))
    avatar = _h.get_a_avatar(avatar_id)
    if avatar is None:
        return unauthorized(_e.USER_INVALID)
    today = datetime.datetime.today()
    curr_year = today.year
    curr_month = today.month
    start_date = "{0}-{1}-{2}".format(curr_year - 1, curr_month, 1)
    end_date = "{0}-{1}-{2}".format(curr_year, curr_month, today.day)
    this_avg_score = _h.get_avg_score_between_dates(avatar_id, start_date,
                                                    end_date)
    if this_avg_score is None or this_avg_score.avg_score is None:
        return unauthorized(_e.SCORE_NONE)

    if avatar.date_of_birth is None:
        return unauthorized(_e.BIRTH_NONE)
    avg_score = format(this_avg_score.avg_score, '.2f')
    str_score = avg_score.split('.')[0] + avg_score.split('.')[1]
    full_lifespan_day = _h.get_remaining_life_span(int(str_score))
    full_lifespan_day = int(format(full_lifespan_day, '.0f'))

    # It's logging the full_lifespan_day into avatar table for ranking
    _h.update_avatar_info(avatar, AvatarInfo.full_lifespan, full_lifespan_day)

    date_of_birth = datetime.datetime(avatar.date_of_birth.year,
                                      avatar.date_of_birth.month,
                                      avatar.date_of_birth.day)
    gap_date = datetime.datetime.today() - date_of_birth
    r_lifespan_day = full_lifespan_day - gap_date.days
    return ok(r_lifespan_day)


@avt_api.route('/ranking/<int:age_range>/<int:starting>/<int:page>',
               methods=['GET'])
def fetch_lifespan_rankings(age_range=None, starting=None, page=None):
    if age_range is None:
        return bad_req(_m.EMPTY_PARAM.format('age_range'))
    if starting is None:
        return bad_req(_m.EMPTY_PARAM.format('starting'))
    rankings = _h.get_lifespan_rankings(age_range, starting, page, 15)
    js_rankings = _h.convert_rankings_into_js(rankings)
    return ok(dict(rankings=js_rankings))


@avt_api.route('/<int:avatar_id>/ranking/<int:age_range>', methods=['GET'])
def fetch_my_lifespan_ranking(avatar_id=None, age_range=None):
    if avatar_id is None:
        return bad_req(_m.EMPTY_PARAM.format('avatar_id'))
    if age_range is None:
        return bad_req(_m.EMPTY_PARAM.format('age_range'))
    ranking = _h.get_a_lifespan_ranking(avatar_id, age_range)
    if ranking is not None:
        js_ranking = _h.convert_a_ranking_into_js(ranking=ranking)
    else:
        avatar = _h.get_a_avatar(avatar_id)
        js_ranking = _h.convert_a_ranking_into_js(avatar=avatar)
    return ok(data=js_ranking)


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
    lang_profile_tag = _h.get_a_lang_profile_tag(avatar.id)
    if lang_profile_tag is None:
        lang_profile_tag = _h.create_profile_tag(avatar.id, TagId.language,
                                                 TagId.eng, True)
    auth = dict(avatar=avatar_js, language_id=lang_profile_tag.sub_tag_id)
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
        return unauthorized(_e.CODE_INVALID)
    data = result['data']
    try:
        email = data['email']
    except KeyError:
        return unauthorized(_e.CODE_INVALID)
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


@mail_api.route('/opinion', methods=['POST'])
@jwt_required
def send_user_opinion_mail():
    result = validate_schema(request.get_json(), _s.mail_user_opinion)
    if not result['ok']:
        return bad_req(result['message'])
    data = result['data']
    try:
        avatar_id = data['avatar_id']
        tag_id = data['tag_id']
        opinion = data['opinion']
    except KeyError:
        return bad_req(_m.BAD_PARAM)
    avatar = _h.get_a_avatar(avatar_id=avatar_id)
    if not avatar:
        return forbidden(_e.USER_INVALID)
    tag = _h.get_a_tag(tag_id)
    data = dict(tag=tag, avatar=avatar, opinion=opinion)
    send_opinion_mail(data=data)
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


# Unwrap when test on localhost
# @avt_api.route('/<int:avatar_id>/profile-img', methods=['POST'])
# def upload_profile_image1(avatar_id=None):
#     if avatar_id is None:
#         return bad_req(_m.EMPTY_PARAM.format('avatar_id'))
#     if request.method == 'POST':
#         if 'file' not in request.files:
#             return bad_req(_m.EMPTY_PARAM.format('file'))
#         file = request.files['file']
#         filename = 'photo-{0}.png'.format(str(avatar_id))
#         location = "dymm_api/static/avatar/profile"
#         _h.upload_single_file(file, location, filename)
#         _h.update_avatar_info(avatar_id, AvatarInfo.color_code, 99)
#         return ok()


# Unwrap when deploy product
@avt_api.route('/<int:avatar_id>/profile-img', methods=['POST'])
def upload_profile_image(avatar_id=None):
    """Process the uploaded file and upload it to Google Cloud Storage."""
    if avatar_id is None:
        return bad_req(_m.EMPTY_PARAM.format('avatar_id'))
    uploaded_file = request.files.get('file')
    if not uploaded_file:
        return bad_req(_m.EMPTY_PARAM.format('file'))

    # Create a Cloud Storage client.
    gcs = storage.Client()

    # Get the bucket that the file will be uploaded to.
    bucket = gcs.get_bucket(os.environ['CLOUD_STORAGE_BUCKET'])

    # Create a new blob and upload the file's content.
    # blob = bucket.blob(uploaded_file.filename)
    str_date = datetime.datetime.now(tz=pytz.utc).strftime('%Y%m%d%H%M%S')
    path_name = 'avatar/profile/'
    file_name = '{0}-{1}.png'.format(str(avatar_id), str_date)
    blob = bucket.blob(path_name + file_name)
    blob.upload_from_string(
        uploaded_file.read(),
        content_type=uploaded_file.content_type
    )
    avatar = _h.get_a_avatar(avatar_id)
    if avatar.photo_name:
        _blob = bucket.blob(path_name + avatar.photo_name)
        _blob.delete()
    _h.update_avatar_info(avatar, AvatarInfo.photo_name, file_name)
    _h.update_avatar_info(avatar, AvatarInfo.color_code, 0)
    # The public URL can be used to directly access the uploaded file via HTTP.
    print(blob.public_url)
    return blob.public_url


# PUT services
# -----------------------------------------------------------------------------
@avt_api.route('', methods=['PUT'])
@jwt_required
def put_avatar_info():
    result = validate_schema(request.get_json(), _s.update_avatar)
    if not result['ok']:
        return bad_req(result['message'])
    data = result['data']
    target = data['target']
    new_info = data['new_info']
    try:
        avatar_id = data['avatar_id']
        avatar = _h.get_a_avatar(avatar_id)
    except KeyError:
        # Case changing new password instead of old one that forgotten.
        avatar = _h.get_a_avatar(email=data['email'])
        _h.update_avatar_info(avatar, target, new_info)
        return ok()
    try:
        old_password = data['old_password']
        if not b_crypt.check_password_hash(avatar.password_hash, old_password):
            return unauthorized(_e.PASS_INVALID)
        _h.update_avatar_info(avatar, target, new_info)
    except KeyError:
        # If it's not attempt to change password.
        if target == AvatarInfo.email:
            if _h.is_email_duplicated(new_info):
                return unauthorized(_e.MAIL_DUP)
            if _h.update_avatar_info(avatar, target, new_info):
                send_conf_mail(new_info)
                return ok()
        _h.update_avatar_info(avatar, target, new_info)
    return ok()


@avt_api.route('/profile/<int:profile_tag_id>/<int:tag_id>', methods=['PUT'])
@jwt_required
def put_a_profile_tag(profile_tag_id=None, tag_id=None):
    if profile_tag_id is None:
        return bad_req(_m.EMPTY_PARAM.format('avatar_fact_id'))
    if tag_id is None:
        return bad_req(_m.EMPTY_PARAM.format('new_fact_id'))
    is_selected = True
    if _h.is_x_super_got_y_sub(TagId.profile, tag_id):
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
