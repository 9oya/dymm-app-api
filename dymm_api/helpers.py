import os, random, re, datetime, calendar
from datetime import datetime as dt

from flask_jwt_extended import create_access_token, create_refresh_token
from sqlalchemy import text, func, and_, or_

from dymm_api import b_crypt, db
from .patterns import (URIPattern, TagType, TagClass, AvatarInfo, CondLogType,
                       BookmarkSuperTag, RegExPattern, TagId)
from .models import (Avatar, AvatarCond, Banner, Bookmark, LogGroup, LogHistory,
                     ProfileTag, Tag, TagLog, TagSet)

_u = URIPattern()
_r = RegExPattern
db_session = db.session


def str_to_bool(v):
    return str(v).lower() in ("yes", "true", "t", "1")


def str_to_none(v):
    if v is '':
        return None
    else:
        return v


class Helpers(object):
    # Generators
    # -------------------------------------------------------------------------
    @staticmethod
    def gen_random_profile_color() -> int:
        profile_colors = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
        random.shuffle(profile_colors)
        random.shuffle(profile_colors)
        return profile_colors[5]

    # Validators
    # -------------------------------------------------------------------------
    @staticmethod
    def is_email_duplicated(email) -> bool:
        dup_email = Avatar.query.filter(
            Avatar.email == email,
            Avatar.is_active == True
        ).first()
        if dup_email:
            return True
        return False

    @staticmethod
    def is_x_super_got_y_sub(super_id, sub_id):
        tag_set = TagSet.query.filter(
            TagSet.super_id == super_id,
            TagSet.sub_id == sub_id,
            TagSet.is_active == True
        ).first()
        return tag_set

    @staticmethod
    def has_bookmark(avatar_id, tag_id) -> bool:
        if Helpers.get_a_bookmark(avatar_id=avatar_id, tag_id=tag_id):
            return True
        else:
            return False

    # Converters
    # -------------------------------------------------------------------------
    @staticmethod
    def convert_banners_into_js(banners: [Banner]) -> [dict]:
        _js_list = list()
        for banner in banners:
            _js = dict(
                id=banner.id,
                img_name=banner.img_name,
                bg_color=banner.bg_color,
                txt_color=banner.txt_color,
                eng_title=banner.eng_title,
                kor_title=banner.kor_title,
                jpn_title=banner.jpn_title,
                eng_subtitle=banner.eng_subtitle,
                kor_subtitle=banner.kor_subtitle,
                jpn_subtitle=banner.jpn_subtitle
            )
            _js_list.append(_js)
        return _js_list

    @staticmethod
    def convert_a_avatar_into_js(avatar: Avatar) -> dict:
        if avatar.date_of_birth is not None:
            date_of_birth = "{0}-{1}-{2}".format(avatar.date_of_birth.year,
                                                 avatar.date_of_birth.month,
                                                 avatar.date_of_birth.day)
        else:
            date_of_birth = None
        fr_ex_date = avatar.created_timestamp + datetime.timedelta(days=7)
        _js = dict(
            id=avatar.id,
            is_blocked=avatar.is_blocked,
            is_confirmed=avatar.is_confirmed,
            email=avatar.email,
            first_name=avatar.first_name,
            last_name=avatar.last_name,
            ph_number=avatar.ph_number,
            color_code=avatar.color_code,
            photo_name=avatar.photo_name,
            introudction=avatar.introduction,
            date_of_birth=date_of_birth,
            free_exp_date='{0}-{1}-{2}'.format(fr_ex_date.year,
                                               fr_ex_date.month,
                                               fr_ex_date.day),
            is_free_trial=fr_ex_date >= dt.utcnow(),
            access_token=create_access_token(
                identity=dict(email=avatar.email), fresh=True
            ),
            refresh_token=create_refresh_token(
                identity=dict(email=avatar.email)
            )
        )
        return _js

    @staticmethod
    def convert_avt_cond_list_into_js(avt_cond_list: [AvatarCond]) -> [dict]:
        _js_list = list()
        for avt_cond in avt_cond_list:
            try:
                start_date = avt_cond.start_date.strftime('%b/%d/%Y')
            except AttributeError:
                start_date = None
            try:
                end_date = avt_cond.end_date.strftime('%b/%d/%Y')
            except AttributeError:
                end_date = None
            _js = dict(
                id=avt_cond.id,
                avatar_id=avt_cond.avatar_id,
                tag_id=avt_cond.tag_id,
                start_date=start_date,
                end_date=end_date,
                eng_name=avt_cond.tag.eng_name,
                kor_name=avt_cond.tag.kor_name,
                jpn_name=avt_cond.tag.jpn_name
            )
            _js_list.append(_js)
        return _js_list

    @staticmethod
    def convert_log_groups_into_js(log_groups: [LogGroup]) -> list:
        _js_list = list()
        for log_group in log_groups:
            _js = dict(
                id=log_group.id,
                year_number=log_group.year_number,
                month_number=log_group.month_number,
                week_of_year=log_group.week_of_year,
                day_of_year=log_group.day_of_year,
                group_type=log_group.group_type,
                day_number=log_group.log_date.day,
                food_cnt=log_group.food_cnt,
                act_cnt=log_group.act_cnt,
                drug_cnt=log_group.drug_cnt,
                cond_score=log_group.cond_score,
                note=log_group.note
            )
            _js_list.append(_js)
        return _js_list

    @staticmethod
    def new_convert_log_groups_into_js(log_groups: [LogGroup]) -> list:
        _js_list = list()
        for log_group in log_groups:
            _js = dict(
                id=log_group.id,
                year_number=log_group.year_number,
                year_forweekofyear=log_group.year_forweekofyear,
                month_number=log_group.month_number,
                week_of_year=log_group.week_of_year,
                day_of_year=log_group.day_of_year,
                group_type=log_group.group_type,
                day_number=log_group.log_date.day,
                food_cnt=log_group.food_cnt,
                act_cnt=log_group.act_cnt,
                drug_cnt=log_group.drug_cnt,
                cond_score=log_group.cond_score,
                note=log_group.note
            )
            _js_list.append(_js)
        return _js_list

    @staticmethod
    def convert_tag_logs_into_js(tag_logs: [TagLog]) -> [dict]:
        _js_list = list()
        for tag_log in tag_logs:
            _js = dict(
                id=tag_log.id,
                group_id=tag_log.group_id,
                tag_id=tag_log.tag_id,
                tag_type=tag_log.tag.tag_type,
                x_val=tag_log.x_val,
                y_val=tag_log.y_val,
                eng_name=tag_log.tag.eng_name,
                kor_name=tag_log.tag.kor_name,
                jpn_name=tag_log.tag.jpn_name
            )
            _js_list.append(_js)
        return _js_list

    @staticmethod
    def convert_a_tag_into_js(tag: Tag) -> dict:
        _js = dict(id=tag.id,
                   tag_type=tag.tag_type,
                   eng_name=tag.eng_name,
                   kor_name=tag.kor_name,
                   jpn_name=tag.jpn_name,
                   class1=tag.class1,
                   division1=tag.division1,
                   division2=tag.division2,
                   division3=tag.division3,
                   division4=tag.division4,
                   division5=tag.division5)
        return _js

    @staticmethod
    def convert_tags_into_js(tags: [Tag]) -> [dict]:
        _js_list = list()
        for tag in tags:
            _js = dict(id=tag.id,
                       tag_type=tag.tag_type,
                       eng_name=tag.eng_name,
                       kor_name=tag.kor_name,
                       jpn_name=tag.jpn_name)
            _js_list.append(_js)
        return _js_list

    @staticmethod
    def convert_tag_sets_into_js(tag_sets) -> [dict]:
        _js_list = list()
        for tag_set in tag_sets:
            _js = dict(id=tag_set.sub.id,
                       tag_type=tag_set.sub.tag_type,
                       eng_name=tag_set.sub.eng_name,
                       kor_name=tag_set.sub.kor_name,
                       jpn_name=tag_set.sub.jpn_name,
                       class1=tag_set.sub.class1,
                       division1=tag_set.sub.division1,
                       division2=tag_set.sub.division2,
                       division3=tag_set.sub.division3,
                       division4=tag_set.sub.division4,
                       division5=tag_set.sub.division5)
            _js_list.append(_js)
        return _js_list

    @staticmethod
    def convert_tag_sets_into_js_add_idx(tag_sets, matching_id):
        _js_list = list()
        _idx = 0
        _matching_idx = 0
        for tag_set in tag_sets:
            _js = dict(
                id=tag_set.sub.id,
                idx=_idx,
                eng_name=tag_set.sub.eng_name,
                kor_name=tag_set.sub.kor_name,
                jpn_name=tag_set.sub.jpn_name
            )
            if tag_set.sub.id == int(matching_id):
                _matching_idx = _idx
            _idx += 1
            _js_list.append(_js)
        return _js_list, _matching_idx

    @staticmethod
    def convert_profile_tag_into_js(profile_tags: [ProfileTag]):
        _js_list = list()
        for profile_tag in profile_tags:
            _js = dict(
                id=profile_tag.id,
                tag_id=profile_tag.sub_tag_id,
                is_selected=profile_tag.is_selected,
                eng_name=profile_tag.sub_tag.eng_name,
                kor_name=profile_tag.sub_tag.kor_name,
                jpn_name=profile_tag.sub_tag.jpn_name
            )
            _js_list.append(_js)
        return _js_list

    @staticmethod
    def convert_bookmarks_into_js(bookmarks: [Bookmark]):
        _js_list = list()
        for bookmark in bookmarks:
            _js = dict(
                bookmark_id=bookmark.id,
                id=bookmark.sub_tag_id,
                tag_type=bookmark.sub_tag.tag_type,
                eng_name=bookmark.sub_tag.eng_name,
                kor_name=bookmark.sub_tag.kor_name,
                jpn_name=bookmark.sub_tag.jpn_name
            )
            _js_list.append(_js)
        return _js_list

    @staticmethod
    def convert_log_histories_into_js(log_histories: [LogHistory]):
        _js_list = list()
        for log_history in log_histories:
            _js = dict(
                id=log_history.tag_id,
                tag_type=log_history.tag.tag_type,
                eng_name=log_history.tag.eng_name,
                kor_name=log_history.tag.kor_name,
                jpn_name=log_history.tag.jpn_name
            )
            _js_list.append(_js)
        return _js_list

    @staticmethod
    def convert_rankings_into_js(rankings):
        _js_list = list()
        for ranking in rankings:
            # _js = dict(
            #     avatar_id=ranking.id,
            #     first_name=ranking.first_name,
            #     last_name=ranking.last_name,
            #     photo_name=ranking.photo_name,
            #     color_code=ranking.color_code,
            #     full_lifespan=ranking.full_lifespan,
            #     rank_num=ranking.rnk
            # )
            full_lifespan = ranking.full_lifespan
            if full_lifespan is None:
                full_lifespan = 30000
            _js = dict(
                avatar_id=ranking.id,
                first_name=ranking.first_name,
                last_name=ranking.last_name,
                photo_name=ranking.photo_name,
                color_code=ranking.color_code,
                full_lifespan=full_lifespan,
                rank_num=ranking.rnk
            )
            _js_list.append(_js)
        return _js_list

    @staticmethod
    def convert_a_ranking_into_js(ranking=None, avatar=None):
        if avatar is not None:
            _js = dict(
                avatar_id=avatar.id,
                first_name=avatar.first_name,
                last_name=avatar.last_name,
                photo_name=avatar.photo_name,
                color_code=avatar.color_code,
                full_lifespan=avatar.full_lifespan,
                rank_num=0
            )
        else:
            _js = dict(
                avatar_id=ranking.id,
                first_name=ranking.first_name,
                last_name=ranking.last_name,
                photo_name=ranking.photo_name,
                color_code=ranking.color_code,
                full_lifespan=ranking.full_lifespan,
                rank_num=ranking.rnk
            )
        return _js

    # GET methods
    # -------------------------------------------------------------------------
    @staticmethod
    def get_banners():
        banners = Banner.query.filter(
            Banner.is_active == True
        ).order_by(Banner.priority).all()
        return banners

    @staticmethod
    def get_a_tag(tag_id):
        tag = Tag.query.filter(
            Tag.id == tag_id
        ).first()
        return tag

    @staticmethod
    def get_a_super_tag(sub_id):
        tag_set = TagSet.query.filter(
            TagSet.sub_id == sub_id
        ).first()
        return tag_set.super

    @staticmethod
    def search_low_div_tags_from_up_div_tag(super_tag: Tag, keyword: str,
                                            page=None, per_page=40):
        tag_name = Tag.eng_name
        _reg_obj = re.compile(_r.kor_name)
        if _reg_obj.match(keyword[0]):
            tag_name = Tag.kor_name
        if super_tag.division1 == 0:
            if super_tag.class1 == TagClass.drug:
                drug_tags = Tag.query.filter(
                    # Tag.class1 == TagClass.drug_abc,
                    or_(Tag.class1 == TagClass.drug_abc,
                        Tag.class1 == TagClass.drug_pd_us,
                        Tag.class1 == TagClass.drug_pd_kr,
                        Tag.class1 == TagClass.supp),
                    Tag.division1 != 0,
                    Tag.division2 != 0,
                    func.lower(tag_name).contains(keyword.lower(),
                                                  autoescape=True),
                    Tag.is_active == True
                ).order_by(
                    Tag.class1,
                    Tag.division1,
                    Tag.eng_name
                ).paginate(page, per_page, False).items
                # supp_tags = Tag.query.filter(
                #     Tag.class1 == TagClass.food,
                #     Tag.division1 == 20,  # 20: Supplements
                #     Tag.division2 != 0,
                #     func.lower(tag_name).contains(keyword.lower(),
                #                                   autoescape=True),
                #     Tag.is_active == True
                # ).paginate(page, (per_page / 2), False).items
                # # supp_tags.extend(drug_tags)
                # drug_tags.extend(supp_tags)
                return drug_tags
            if super_tag.class1 == TagClass.food:
                tags = Tag.query.filter(
                    Tag.class1 == super_tag.class1,
                    Tag.division1 != 0,
                    Tag.division1 != 20,  # 20: Supplements
                    func.lower(tag_name).contains(keyword.lower(),
                                                  autoescape=True),
                    Tag.is_active == True
                ).paginate(page, per_page, False).items
                return tags
            if super_tag.class1 == TagClass.cond:
                cond_tags = Tag.query.filter(
                    Tag.class1 == super_tag.class1,
                    Tag.division1 != 0,
                    Tag.division4 == 0,
                    func.lower(tag_name).contains(keyword.lower(),
                                                  autoescape=True),
                    Tag.is_active == True
                ).paginate(page, per_page, False).items
                return cond_tags
            tags = Tag.query.filter(
                Tag.class1 == super_tag.class1,
                Tag.division1 != 0,
                func.lower(tag_name).contains(keyword.lower(),
                                              autoescape=True),
                Tag.is_active == True
            ).paginate(page, per_page, False).items
        elif super_tag.division2 == 0:
            if super_tag.class1 == TagClass.drug:
                # TODO: - Need to adjust TagSet
                drug_tags = Tag.query.filter(
                    # Tag.class1 == TagClass.drug_abc,
                    or_(Tag.class1 == TagClass.drug_abc,
                        Tag.class1 == TagClass.drug_pd_us),
                    Tag.division1 != 0,
                    Tag.division2 != 0,
                    func.lower(tag_name).contains(keyword.lower(),
                                                  autoescape=True),
                    Tag.is_active == True
                ).paginate(page, per_page, False).items
                return drug_tags
            if super_tag.class1 == TagClass.cond:
                cond_tags = Tag.query.filter(
                    Tag.class1 == super_tag.class1,
                    Tag.division1 == super_tag.division1,
                    Tag.division2 != 0,
                    Tag.division4 == 0,
                    func.lower(tag_name).contains(keyword.lower(),
                                                  autoescape=True),
                    Tag.is_active == True
                ).paginate(page, per_page, False).items
                return cond_tags
            tags = Tag.query.filter(
                Tag.class1 == super_tag.class1,
                Tag.division1 == super_tag.division1,
                Tag.division2 != 0,
                func.lower(tag_name).contains(keyword.lower(),
                                              autoescape=True),
                Tag.is_active == True
            ).paginate(page, per_page, False).items
        elif super_tag.division3 == 0:
            if super_tag.class1 == TagClass.cond:
                cond_tags = Tag.query.filter(
                    Tag.class1 == super_tag.class1,
                    Tag.division1 == super_tag.division1,
                    Tag.division2 == super_tag.division2,
                    Tag.division3 != 0,
                    Tag.division4 == 0,
                    func.lower(tag_name).contains(keyword.lower(),
                                                  autoescape=True),
                    Tag.is_active == True
                ).paginate(page, per_page, False).items
                return cond_tags
            tags = Tag.query.filter(
                Tag.class1 == super_tag.class1,
                Tag.division1 == super_tag.division1,
                Tag.division2 == super_tag.division2,
                Tag.division3 != 0,
                func.lower(tag_name).contains(keyword.lower(),
                                              autoescape=True),
                Tag.is_active == True
            ).paginate(page, per_page, False).items
        elif super_tag.division4 == 0:
            tags = Tag.query.filter(
                Tag.class1 == super_tag.class1,
                Tag.division1 == super_tag.division1,
                Tag.division2 == super_tag.division2,
                Tag.division3 == super_tag.division3,
                Tag.division4 != 0,
                func.lower(tag_name).contains(keyword.lower(),
                                              autoescape=True),
                Tag.is_active == True
            ).paginate(page, per_page, False).items
        elif super_tag.division5 == 0:
            tags = Tag.query.filter(
                Tag.class1 == super_tag.class1,
                Tag.division1 == super_tag.division1,
                Tag.division2 == super_tag.division2,
                Tag.division3 == super_tag.division3,
                Tag.division4 == super_tag.division4,
                Tag.division5 != 0,
                func.lower(tag_name).contains(keyword.lower(),
                                              autoescape=True),
                Tag.is_active == True
            ).paginate(page, per_page, False).items
        else:
            return False
        return tags

    @staticmethod
    def get_a_avatar(avatar_id=None, email=None):
        if avatar_id is None:
            avatar = Avatar.query.filter(
                Avatar.email == email,
                Avatar.is_active == True,
                Avatar.is_blocked == False
            ).first()
            return avatar
        avatar = Avatar.query.filter(
            Avatar.id == avatar_id,
            Avatar.is_active == True,
            Avatar.is_blocked == False
        ).first()
        return avatar

    @staticmethod
    def get_a_avatar_cond(avatar_cond_id):
        avt_cond = AvatarCond.query.filter(
            AvatarCond.id == avatar_cond_id,
            AvatarCond.is_active == True
        ).first()
        return avt_cond

    @staticmethod
    def get_avt_cond_list(avatar_id):
        avt_cond_list = AvatarCond.query.filter(
            AvatarCond.avatar_id == avatar_id,
            AvatarCond.is_active == True
        ).order_by(
            AvatarCond.end_date.desc(),
            AvatarCond.start_date.desc()
        ).all()
        return avt_cond_list

    @staticmethod
    def get_a_log_group(group_id) -> LogGroup:
        log_group = LogGroup.query.filter(
            LogGroup.id == group_id,
            LogGroup.is_active == True
        ).first()
        return log_group

    @staticmethod
    def get_log_groups(avatar_id, year_number, month_number=None,
                       week_of_year=None):
        if week_of_year is None:
            log_groups = LogGroup.query.filter(
                LogGroup.avatar_id == avatar_id,
                LogGroup.year_number == year_number,
                LogGroup.month_number == month_number,
                LogGroup.is_active == True
            ).order_by(
                LogGroup.day_of_year.desc(),
                LogGroup.group_type.desc()
            ).all()
            return log_groups
        log_groups = LogGroup.query.filter(
            LogGroup.avatar_id == avatar_id,
            LogGroup.year_number == year_number,
            LogGroup.week_of_year == week_of_year,
            LogGroup.is_active == True
        ).order_by(
            LogGroup.day_of_year.desc(),
            LogGroup.group_type.desc()
        ).all()
        return log_groups

    @staticmethod
    def new_get_log_groups(avatar_id, year_number=None, month_number=None,
                           week_of_year=None, year_forweekofyear=None):
        if week_of_year is None:
            # Get Monthly
            log_groups = LogGroup.query.filter(
                LogGroup.avatar_id == avatar_id,
                LogGroup.year_number == year_number,
                LogGroup.month_number == month_number,
                LogGroup.is_active == True
            ).order_by(
                LogGroup.day_of_year.desc(),
                LogGroup.group_type.desc()
            ).all()
            return log_groups
        # Get Weekly
        log_groups = LogGroup.query.filter(
            LogGroup.avatar_id == avatar_id,
            LogGroup.year_forweekofyear == year_forweekofyear,
            LogGroup.week_of_year == week_of_year,
            LogGroup.is_active == True
        ).order_by(
            LogGroup.day_of_year.desc(),
            LogGroup.group_type.desc()
        ).all()
        return log_groups

    @staticmethod
    def get_log_group_notes(avatar_id, page=None, per_page=20):
        log_groups = LogGroup.query.filter(
            LogGroup.avatar_id == avatar_id,
            LogGroup.note != None,
            LogGroup.is_active == True
        ).order_by(
            LogGroup.year_number,
            LogGroup.day_of_year.desc()
        ).paginate(page, per_page, False).items
        return log_groups

    @staticmethod
    def get_avg_score_per_month(avatar_id, year_number, month_number):
        avg_score = LogGroup.query.with_entities(
            func.avg(LogGroup.cond_score).label('avg_score')
        ).filter(
            LogGroup.avatar_id == avatar_id,
            LogGroup.year_number == year_number,
            LogGroup.month_number == month_number,
            LogGroup.is_active == True
        ).first()
        return avg_score

    @staticmethod
    def get_avg_score_per_week(avatar_id, year_number, week_of_year):
        avg_score = LogGroup.query.with_entities(
            func.avg(LogGroup.cond_score).label('avg_score')
        ).filter(
            LogGroup.avatar_id == avatar_id,
            LogGroup.year_number == year_number,
            LogGroup.week_of_year == week_of_year,
            LogGroup.is_active == True
        ).first()
        return avg_score

    @staticmethod
    def get_avg_score_per_year(avatar_id, year_number):
        avg_score = LogGroup.query.with_entities(
            func.avg(LogGroup.cond_score).label('avg_score')
        ).filter(
            LogGroup.avatar_id == avatar_id,
            LogGroup.year_number == year_number,
            LogGroup.is_active == True
        ).first()
        return avg_score

    @staticmethod
    def get_avg_score_between_dates(avatar_id, start_date, end_date):
        avg_score = LogGroup.query.with_entities(
            func.avg(LogGroup.cond_score).label('avg_score')
        ).filter(
            LogGroup.avatar_id == avatar_id,
            LogGroup.is_active == True,
            LogGroup.log_date.between(start_date, end_date)
        ).first()
        return avg_score

    @staticmethod
    def get_remaining_life_span(score: int):
        full_score = 1000
        if full_score > score > 840:
            waste_point = 109.5
            full_span_day = 365 * 200
            score_gap = full_score - score
            waste_day = score_gap * waste_point
            r_span_day = full_span_day - waste_day
        elif score == 840:
            r_span_day = 365 * 150
        elif 839 >= score >= 740:
            waste_point = 73
            full_score = 840
            full_span_day = 365 * 150
            score_gap = full_score - score
            waste_day = score_gap * waste_point
            r_span_day = full_span_day - waste_day
        elif 739 >= score >= 640:
            waste_point = 109.5
            full_score = 740
            full_span_day = 365 * 130
            score_gap = full_score - score
            waste_day = score_gap * waste_point
            r_span_day = full_span_day - waste_day
        else:
            waste_point = 36.5
            full_score = 640
            full_span_day = 365 * 100
            score_gap = full_score - score
            waste_day = score_gap * waste_point
            r_span_day = full_span_day - waste_day
        return r_span_day

    @staticmethod
    def get_tag_logs(group_id, tag_type) -> [TagLog]:
        tag_logs = db_session.query(
            TagLog
        ).join(
            TagLog.tag
        ).filter(
            TagLog.group_id == group_id,
            TagLog.is_active == True,
            Tag.tag_type == tag_type
        ).order_by(Tag.division1).all()
        return tag_logs

    @staticmethod
    def get_tag_sets(super_id: int, sort_type, page=None, per_page=40,
                     lang_id=None):
        if sort_type == 'eng':
            if page:
                tag_sets = TagSet.query.join(TagSet.sub).filter(
                    TagSet.super_id == super_id,
                    TagSet.is_active == True
                ).order_by(
                    Tag.eng_name
                ).paginate(page, per_page, False).items
                return tag_sets
            tag_sets = db_session.query(TagSet).join(TagSet.sub).filter(
                TagSet.super_id == super_id,
                TagSet.is_active == True
            ).order_by(Tag.eng_name).all()
        elif sort_type == 'kor':
            if page:
                tag_sets = TagSet.query.join(TagSet.sub).filter(
                    TagSet.super_id == super_id,
                    TagSet.is_active == True
                ).order_by(
                    Tag.kor_name
                ).paginate(page, per_page, False).items
                return tag_sets
            tag_sets = db_session.query(TagSet).join(TagSet.sub).filter(
                TagSet.super_id == super_id,
                TagSet.is_active == True
            ).order_by(Tag.kor_name).all()
        elif sort_type == 'jpn':
            if page:
                tag_sets = TagSet.query.join(TagSet.sub).filter(
                    TagSet.super_id == super_id,
                    TagSet.is_active == True
                ).order_by(
                    Tag.jpn_name
                ).paginate(page, per_page, False).items
                return tag_sets
            tag_sets = db_session.query(TagSet).join(TagSet.sub).filter(
                TagSet.super_id == super_id,
                TagSet.is_active == True
            ).order_by(Tag.jpn_name).all()
        elif sort_type == 'priority':
            if page:
                tag_sets = db_session.query(TagSet).filter(
                    TagSet.super_id == super_id,
                    TagSet.is_active == True
                ).order_by(
                    TagSet.priority.desc()
                ).paginate(page, per_page, False).items
                return tag_sets
            tag_sets = db_session.query(TagSet).filter(
                TagSet.super_id == super_id,
                TagSet.is_active == True
            ).order_by(TagSet.priority.desc()).all()
        elif sort_type == 'div':
            if lang_id == TagId.eng:
                # Case us drugs
                if page:
                    tag_sets = TagSet.query.join(TagSet.sub).filter(
                        TagSet.super_id == super_id,
                        TagSet.is_active == True,
                        Tag.class1 != 9
                    ).order_by(
                        Tag.class1,
                        Tag.division1,
                        Tag.division2,
                        Tag.division3,
                        Tag.division4,
                        Tag.division5
                    ).paginate(page, per_page, False).items
                    return tag_sets
                tag_sets = db_session.query(TagSet).join(TagSet.sub).filter(
                    TagSet.super_id == super_id,
                    TagSet.is_active == True
                ).order_by(
                    Tag.class1,
                    Tag.division1,
                    Tag.division2,
                    Tag.division3,
                    Tag.division4,
                    Tag.division5
                ).all()
                return tag_sets
            elif lang_id == TagId.kor:
                # Case kr drugs
                if page:
                    tag_sets = TagSet.query.join(TagSet.sub).filter(
                        TagSet.super_id == super_id,
                        TagSet.is_active == True,
                        Tag.class1 != 8
                    ).order_by(
                        Tag.class1,
                        Tag.division1,
                        Tag.division2,
                        Tag.division3,
                        Tag.division4,
                        Tag.division5
                    ).paginate(page, per_page, False).items
                    return tag_sets
                tag_sets = db_session.query(TagSet).join(TagSet.sub).filter(
                    TagSet.super_id == super_id,
                    TagSet.is_active == True
                ).order_by(
                    Tag.class1,
                    Tag.division1,
                    Tag.division2,
                    Tag.division3,
                    Tag.division4,
                    Tag.division5
                ).all()
                return tag_sets
            if page:
                tag_sets = TagSet.query.join(TagSet.sub).filter(
                    TagSet.super_id == super_id,
                    TagSet.is_active == True
                ).order_by(
                    Tag.class1,
                    Tag.division1,
                    Tag.division2,
                    Tag.division3,
                    Tag.division4,
                    Tag.division5
                ).paginate(page, per_page, False).items
                return tag_sets
            tag_sets = db_session.query(TagSet).join(TagSet.sub).filter(
                TagSet.super_id == super_id,
                TagSet.is_active == True
            ).order_by(
                Tag.class1,
                Tag.division1,
                Tag.division2,
                Tag.division3,
                Tag.division4,
                Tag.division5
            ).all()
        else:
            return False
        return tag_sets

    @staticmethod
    def get_valid_profile_tags(avatar_id, tag_sets):
        profile_tags = list()
        for tag_set in tag_sets:
            profile_tag = ProfileTag.query.filter(
                ProfileTag.avatar_id == avatar_id,
                ProfileTag.super_tag_id == tag_set.sub_id,
                ProfileTag.is_active == True
            ).first()
            if profile_tag:
                profile_tags.append(profile_tag)
            else:
                if tag_set.sub_id == TagId.language:
                    profile_tag = Helpers.create_profile_tag(avatar_id,
                                                             tag_set.sub_id,
                                                             TagId.eng,
                                                             True)
                elif tag_set.sub_id == TagId.theme:
                    profile_tag = Helpers.create_profile_tag(avatar_id,
                                                             tag_set.sub_id,
                                                             TagId.light,
                                                             True)
                else:
                    profile_tag = Helpers.create_profile_tag(avatar_id,
                                                             tag_set.sub_id,
                                                             tag_set.sub_id,
                                                             False)
                profile_tags.append(profile_tag)
        return profile_tags

    @staticmethod
    def get_a_profile_tag(profile_tag_id):
        profile_tag = ProfileTag.query.filter(
            ProfileTag.id == profile_tag_id,
            ProfileTag.is_active == True
        ).first()
        return profile_tag

    @staticmethod
    def get_a_lang_profile_tag(avatar_id):
        profile_tag = ProfileTag.query.filter(
            ProfileTag.avatar_id == avatar_id,
            ProfileTag.super_tag_id == TagId.language,
            ProfileTag.is_active == True
        ).first()
        return profile_tag

    @staticmethod
    def get_a_gender_profile_tag(avatar_id):
        profile_tag = ProfileTag.query.filter(
            ProfileTag.avatar_id == avatar_id,
            ProfileTag.super_tag_id == TagId.gender,
            ProfileTag.is_active == True
        ).first()
        return profile_tag

    @staticmethod
    def get_profile_tags(avatar_id: int) -> [ProfileTag]:
        profile_tags = ProfileTag.query.filter(
            ProfileTag.avatar_id == avatar_id,
            ProfileTag.is_active == True
        ).order_by(ProfileTag.priority.desc()).all()
        return profile_tags

    @staticmethod
    def get_a_tag_log(tag_log_id) -> TagLog:
        tag_log = TagLog.query.filter(
            TagLog.id == tag_log_id,
            TagLog.is_active == True
        ).first()
        return tag_log

    @staticmethod
    def get_a_bookmark(bookmark_id=None, avatar_id=None, tag_id=None):
        if bookmark_id:
            bookmark = Bookmark.query.filter(
                Bookmark.id == bookmark_id,
                Bookmark.is_active == True
            ).first()
            return bookmark
        elif avatar_id and tag_id:
            bookmark = Bookmark.query.filter(
                Bookmark.avatar_id == avatar_id,
                Bookmark.sub_tag_id == tag_id,
                Bookmark.is_active == True
            ).first()
            return bookmark
        else:
            return False

    @staticmethod
    def get_bookmarks_total(tag_id: int) -> int:
        bookmarks = Bookmark.query.filter(
            Bookmark.sub_tag_id == tag_id,
            Bookmark.is_active == True
        ).all()
        return len(bookmarks)

    @staticmethod
    def get_bookmarks(avatar_id, super_id):
        bookmarks = Bookmark.query.filter(
            Bookmark.avatar_id == avatar_id,
            Bookmark.super_tag_id == super_id,
            Bookmark.is_active == True
        ).all()
        return bookmarks

    @staticmethod
    def get_a_bookmark_include_inactive(avatar_id, sub_id):
        bookmark = Bookmark.query.filter(
            Bookmark.avatar_id == avatar_id,
            Bookmark.sub_tag_id == sub_id
        ).first()
        return bookmark

    @staticmethod
    def get_bookmark_super_tag_id(tag_type):
        if tag_type == TagType.food:
            super_id = BookmarkSuperTag.food
        elif tag_type == TagType.activity:
            super_id = BookmarkSuperTag.activity
        elif tag_type == TagType.drug:
            super_id = BookmarkSuperTag.drug
        elif tag_type == TagType.condition:
            super_id = BookmarkSuperTag.condition
        else:
            return False
        return super_id

    @staticmethod
    def get_a_log_history_even_inactive(avatar_id, tag_id):
        log_history = LogHistory.query.filter(
            LogHistory.avatar_id == avatar_id,
            LogHistory.tag_id == tag_id
        ).first()
        return log_history

    @staticmethod
    def get_log_histories(avatar_id):
        log_histories = LogHistory.query.filter(
            LogHistory.avatar_id == avatar_id,
            LogHistory.is_active == True
        ).order_by(
            LogHistory.modified_timestamp.desc()
        ).limit(24).all()
        return log_histories

    @staticmethod
    def new_get_log_histories(avatar_id, page, per_page):
        log_histories = LogHistory.query.filter(
            LogHistory.avatar_id == avatar_id,
            LogHistory.is_active == True
        ).order_by(
            LogHistory.modified_timestamp.desc()
        ).paginate(page, per_page, False).items
        return log_histories

    @staticmethod
    def get_a_lifespan_ranking(avatar_id, age_range):
        today = datetime.datetime.today()
        start_date = '1900-1-1'
        end_date = None
        if age_range == 2:
            start_date = '{0}-{1}-{2}'.format(today.year - 30,
                                              today.month, today.day)
            end_date = '2999-12-1'
        elif age_range == 3:
            start_date = '{0}-{1}-{2}'.format(today.year - 50,
                                              today.month, today.day)
            end_date = '{0}-{1}-{2}'.format(today.year - 30,
                                            today.month, today.day)
        elif age_range == 4:
            start_date = '{0}-{1}-{2}'.format(today.year - 70,
                                              today.month, today.day)
            end_date = '{0}-{1}-{2}'.format(today.year - 50,
                                            today.month, today.day)
        elif age_range == 5:
            end_date = '{0}-{1}-{2}'.format(today.year - 70,
                                            today.month, today.day)
        if end_date is not None:
            sq = db_session.query(
                Avatar.id,
                Avatar.first_name,
                Avatar.last_name,
                Avatar.photo_name,
                Avatar.color_code,
                Avatar.full_lifespan,
                func.rank().over(
                    order_by=Avatar.full_lifespan.desc()
                ).label('rnk')
            ).filter(
                Avatar.full_lifespan > 0,
                and_(Avatar.date_of_birth >= start_date,
                     Avatar.date_of_birth <= end_date)
            ).subquery()

            ranking = db_session.query(sq).filter(
                sq.c.id == avatar_id
            ).first()
        else:
            sq = db_session.query(
                Avatar.id,
                Avatar.first_name,
                Avatar.last_name,
                Avatar.photo_name,
                Avatar.color_code,
                Avatar.full_lifespan,
                func.rank().over(
                    order_by=Avatar.full_lifespan.desc()
                ).label('rnk')
            ).filter(
                Avatar.full_lifespan > 0
            ).subquery()

            ranking = db_session.query(sq).filter(
                sq.c.id == avatar_id
            ).first()
        return ranking

    @staticmethod
    def get_lifespan_rankings(age_range, starting, page, per_page=20):
        today = datetime.datetime.today()
        start_date = '1900-1-1'
        end_date = None
        if age_range == 2:
            start_date = '{0}-{1}-{2}'.format(today.year - 30,
                                              today.month, today.day)
            end_date = '2999-12-1'
        elif age_range == 3:
            start_date = '{0}-{1}-{2}'.format(today.year - 50,
                                              today.month, today.day)
            end_date = '{0}-{1}-{2}'.format(today.year - 30,
                                            today.month, today.day)
        elif age_range == 4:
            start_date = '{0}-{1}-{2}'.format(today.year - 70,
                                              today.month, today.day)
            end_date = '{0}-{1}-{2}'.format(today.year - 50,
                                            today.month, today.day)
        elif age_range == 5:
            end_date = '{0}-{1}-{2}'.format(today.year - 70,
                                            today.month, today.day)
        if end_date is not None:
            sq = db_session.query(
                Avatar.id,
                Avatar.first_name,
                Avatar.last_name,
                Avatar.photo_name,
                Avatar.color_code,
                Avatar.full_lifespan,
                func.rank().over(
                    order_by=Avatar.full_lifespan.desc()
                ).label('rnk')
            ).filter(
                Avatar.is_active == True,
                Avatar.is_blocked == False,
                Avatar.full_lifespan > 0,
                and_(Avatar.date_of_birth >= start_date,
                     Avatar.date_of_birth <= end_date)
            ).subquery()
        else:
            sq = db_session.query(
                Avatar.id,
                Avatar.first_name,
                Avatar.last_name,
                Avatar.photo_name,
                Avatar.color_code,
                Avatar.full_lifespan,
                func.rank().over(
                    order_by=Avatar.full_lifespan.desc()
                ).label('rnk')
            ).filter(
                Avatar.is_active == True,
                Avatar.is_blocked == False,
                Avatar.full_lifespan > 0
            ).subquery()

        if starting == 2:
            starting = 100
        elif starting == 3:
            starting = 500
        elif starting == 4:
            starting = 1000
        rankings = db_session.query(sq).filter(
            sq.c.rnk >= starting
        ).paginate(page, per_page, False).items
        return rankings

    # CREATE methods
    # -------------------------------------------------------------------------
    @staticmethod
    def create_a_new_avatar(data):
        try:
            password_hash = b_crypt.generate_password_hash(
                data['password']).decode('utf-8')
            avatar = Avatar(
                is_active=True,
                is_admin=False,
                is_blocked=False,
                is_confirmed=False,
                email=data['email'],
                password_hash=password_hash,
                first_name=data['first_name'],
                last_name=data['last_name'],
                color_code=Helpers.gen_random_profile_color()
            )
            db_session.add(avatar)
            db_session.commit()
        except AttributeError:
            return False
        return avatar

    @staticmethod
    def create_log(data):
        tag = Helpers.get_a_tag(data['tag_id'])
        try:
            log_group_id = data['log_group_id']
        except KeyError:
            log_group_id = None
        if log_group_id is None:
            # Create new log group
            food_cnt = 0
            act_cnt = 0
            drug_cnt = 0
            if tag.tag_type == TagType.food:
                food_cnt = 1
            elif tag.tag_type == TagType.activity:
                act_cnt = 1
            elif tag.tag_type == TagType.drug:
                drug_cnt = 1
            new_log_group = LogGroup(
                avatar_id=data['avatar_id'],
                group_type=data['group_type'],
                year_number=data['year_number'],
                month_number=data['month_number'],
                week_of_year=data['week_of_year'],
                day_of_year=data['day_of_year'],
                log_date=data['log_date'],
                is_active=True,
                food_cnt=food_cnt,
                act_cnt=act_cnt,
                drug_cnt=drug_cnt,
            )
            db_session.add(new_log_group)
            db_session.commit()
            log_group_id = new_log_group.id
        else:
            # Existed log group
            log_group = LogGroup.query.filter(
                LogGroup.id == log_group_id,
                LogGroup.avatar_id == data['avatar_id'],
                LogGroup.is_active == True
            ).first()
            if tag.tag_type == TagType.food:
                log_group.food_cnt += 1
            elif tag.tag_type == TagType.activity:
                log_group.act_cnt += 1
            elif tag.tag_type == TagType.drug:
                log_group.drug_cnt += 1
        new_tag_log = TagLog(
            group_id=log_group_id,
            tag_id=tag.id,
            is_active=True,
            x_val=data['x_val'],
            y_val=data['y_val']
        )
        db_session.add(new_tag_log)
        db_session.commit()

    @staticmethod
    def new_create_log(data):
        tag = Helpers.get_a_tag(data['tag_id'])
        try:
            log_group_id = data['log_group_id']
        except KeyError:
            log_group_id = None
        if log_group_id is None:
            # Create new log group
            food_cnt = 0
            act_cnt = 0
            drug_cnt = 0
            if tag.tag_type == TagType.food:
                food_cnt = 1
            elif tag.tag_type == TagType.activity:
                act_cnt = 1
            elif tag.tag_type == TagType.drug:
                drug_cnt = 1
            new_log_group = LogGroup(
                avatar_id=data['avatar_id'],
                group_type=data['group_type'],
                year_number=data['year_number'],
                year_forweekofyear=data['year_forweekofyear'],
                month_number=data['month_number'],
                week_of_year=data['week_of_year'],
                day_of_year=data['day_of_year'],
                log_date=data['log_date'],
                is_active=True,
                food_cnt=food_cnt,
                act_cnt=act_cnt,
                drug_cnt=drug_cnt,
            )
            db_session.add(new_log_group)
            db_session.commit()
            log_group_id = new_log_group.id
        else:
            # Existed log group
            log_group = LogGroup.query.filter(
                LogGroup.id == log_group_id,
                LogGroup.avatar_id == data['avatar_id'],
                LogGroup.is_active == True
            ).first()
            if tag.tag_type == TagType.food:
                log_group.food_cnt += 1
            elif tag.tag_type == TagType.activity:
                log_group.act_cnt += 1
            elif tag.tag_type == TagType.drug:
                log_group.drug_cnt += 1
        new_tag_log = TagLog(
            group_id=log_group_id,
            tag_id=tag.id,
            is_active=True,
            x_val=data['x_val'],
            y_val=data['y_val']
        )
        db_session.add(new_tag_log)
        db_session.commit()

    @staticmethod
    def create_cond_log(data):
        tag = Helpers.get_a_tag(data['tag_id'])
        avatar_cond = AvatarCond.query.filter(
            AvatarCond.avatar_id == data['avatar_id'],
            AvatarCond.tag_id == tag.id,
            AvatarCond.is_active == True
        ).first()
        if avatar_cond:
            if data['cond_log_type'] == CondLogType.start_date:
                avatar_cond.start_date = data['log_date']
            else:
                avatar_cond.end_date = data['log_date']
            avatar_cond.modified_timestamp = text("timezone('utc'::text, now())")
            db_session.commit()
            return True
        else:
            if data['cond_log_type'] == CondLogType.start_date:
                avatar_cond = AvatarCond(
                    avatar_id=data['avatar_id'],
                    tag_id=tag.id,
                    is_active=True,
                    start_date=data['log_date']
                )
            else:
                avatar_cond = AvatarCond(
                    avatar_id=data['avatar_id'],
                    tag_id=tag.id,
                    is_active=True,
                    end_date=data['log_date']
                )
            db_session.add(avatar_cond)
            db_session.commit()
            return True

    @staticmethod
    def create_profile_tag(avatar_id, super_tag_id, sub_tag_id, is_selected):
        profile_tag = ProfileTag(
            avatar_id=avatar_id,
            super_tag_id=super_tag_id,
            sub_tag_id=sub_tag_id,
            is_active=True,
            is_selected=is_selected
        )
        db_session.add(profile_tag)
        db_session.commit()
        return profile_tag

    @staticmethod
    def create_def_profile_tags(avatar_id, language_id):
        tag_sets = Helpers.get_tag_sets(super_id=TagId.profile,
                                        sort_type='priority')
        for tag_set in tag_sets:
            if tag_set.sub_id == TagId.language:
                Helpers.create_profile_tag(avatar_id=avatar_id,
                                           super_tag_id=tag_set.sub_id,
                                           sub_tag_id=language_id,
                                           is_selected=True)
                continue
            elif tag_set.sub_id == TagId.theme:
                Helpers.create_profile_tag(avatar_id=avatar_id,
                                           super_tag_id=tag_set.sub_id,
                                           sub_tag_id=TagId.light,
                                           is_selected=True)
                continue
            else:
                Helpers.create_profile_tag(avatar_id=avatar_id,
                                           super_tag_id=tag_set.sub_id,
                                           sub_tag_id=tag_set.sub_id,
                                           is_selected=False)
        return True

    @staticmethod
    def create_a_bookmark(avatar_id, super_id, sub_id):
        bookmark = Bookmark(
            avatar_id=avatar_id,
            super_tag_id=super_id,
            sub_tag_id=sub_id,
            is_active=True
        )
        db_session.add(bookmark)
        db_session.commit()
        return bookmark.id

    @staticmethod
    def create_a_log_history(avatar_id, tag_id):
        log_history = LogHistory(
            avatar_id=avatar_id,
            tag_id=tag_id,
            is_active=True,
            modified_timestamp=text("timezone('utc'::text, now())")
        )
        db_session.add(log_history)
        db_session.commit()

    @staticmethod
    def upload_single_file(file, location, filename):
        file.save(os.path.join(location, filename))
        return True

    # UPDATE methods
    # -------------------------------------------------------------------------
    @staticmethod
    def update_avatar_mail_confirm(avatar_id):
        db_session.query(Avatar).filter(
            Avatar.id == avatar_id,
            Avatar.is_active == True
        ).update({"is_confirmed": True,
                  "modified_timestamp": text("timezone('utc'::text, now())")},
                 synchronize_session=False)
        db_session.commit()
        return True

    @staticmethod
    def update_avatar_info(avatar: Avatar, target, new_info) -> bool:
        if target == AvatarInfo.first_name:
            avatar.first_name = new_info
            avatar.modified_timestamp = text("timezone('utc'::text, now())")
            db_session.commit()
            return True
        elif target == AvatarInfo.last_name:
            avatar.last_name = new_info
            avatar.modified_timestamp = text("timezone('utc'::text, now())")
            db_session.commit()
            return True
        elif target == AvatarInfo.intro:
            if new_info == "":
                new_info = None
            avatar.introduction = new_info
            avatar.modified_timestamp = text("timezone('utc'::text, now())")
            db_session.commit()
            return True
        elif target == AvatarInfo.email:
            avatar.email = new_info
            avatar.is_confirmed = False
            avatar.modified_timestamp = text("timezone('utc'::text, now())")
            db_session.commit()
            return True
        elif target == AvatarInfo.color_code:
            avatar.color_code = new_info
            avatar.modified_timestamp = text("timezone('utc'::text, now())")
            db_session.commit()
            return True
        elif target == AvatarInfo.photo_name:
            avatar.photo_name = new_info
            avatar.modified_timestamp = text("timezone('utc'::text, now())")
            db_session.commit()
        elif target == AvatarInfo.full_lifespan:
            avatar.full_lifespan = new_info
            avatar.modified_timestamp = text("timezone('utc'::text, now())")
            db_session.commit()
        elif target == TagId.password:
            password_hash = b_crypt.generate_password_hash(new_info).decode(
                'utf-8')
            avatar.password_hash = password_hash
            avatar.modified_timestamp = text("timezone('utc'::text, now())")
            db_session.commit()
            return True
        elif target == TagId.date_of_birth:
            avatar.date_of_birth = new_info
            avatar.modified_timestamp = text("timezone('utc'::text, now())")
            db_session.commit()
            return True
        else:
            return False

    @staticmethod
    def update_profile_tag(profile_tag: ProfileTag, tag_id, is_selected):
        profile_tag.sub_tag_id = tag_id
        profile_tag.is_selected = is_selected
        profile_tag.modified_timestamp = text("timezone('utc'::text, now())")
        db_session.commit()
        return True

    @staticmethod
    def update_log_group_cond_score(log_group: LogGroup, score):
        log_group.cond_score = score
        db_session.commit()
        return True

    @staticmethod
    def update_log_group_note(log_group: LogGroup, note: str):
        if len(note) <= 0:
            note = None
        log_group.note = note
        db_session.commit()
        return True

    @staticmethod
    def update_log_group_is_active(log_group: LogGroup):
        log_group.is_active = False
        db_session.commit()
        return True

    @staticmethod
    def update_log_group_log_cnt(log_group: LogGroup, tag_type):
        if tag_type == TagType.food:
            log_group.food_cnt -= 1
        elif tag_type == TagType.activity:
            log_group.act_cnt -= 1
        elif tag_type == TagType.drug:
            log_group.drug_cnt -= 1
        db_session.commit()
        return True

    @staticmethod
    def update_tag_log(tag_log: TagLog):
        tag_log.is_active = False
        db_session.commit()
        return True

    @staticmethod
    def update_avatar_cond_is_active(avatar_cond: AvatarCond):
        avatar_cond.is_active = False
        db_session.commit()
        return True

    @staticmethod
    def update_bookmark_is_active(bookmark: Bookmark):
        if bookmark.is_active:
            bookmark.is_active = False
        else:
            bookmark.is_active = True
        db_session.commit()
        return True

    @staticmethod
    def update_log_history_date(log_history: LogHistory):
        log_history.modified_timestamp = text("timezone('utc'::text, now())")
        db_session.commit()
        return True
