import random, datetime, pytz

from flask_jwt_extended import create_access_token, create_refresh_token
from sqlalchemy import text

from dymm_api import b_crypt
from database import db_session
from patterns import URIPattern, TagType, AvatarInfo, CondLogType
from models import (Avatar, AvatarCond, Banner, Bookmark, LogGroup, LogHistory,
                    ProfileTag, Tag, TagLog, TagSet)

_u = URIPattern()


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
        profile_colors = [1, 2, 3, 4, 5, 6, 7, 8]
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
        _js = dict(
            id=avatar.id,
            is_blocked=avatar.is_blocked,
            is_confirmed=avatar.is_confirmed,
            email=avatar.email,
            first_name=avatar.first_name,
            last_name=avatar.last_name,
            ph_number=avatar.ph_number,
            profile_type=avatar.profile_type,
            introudction=avatar.introduction,
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
                has_act=log_group.has_act,
                has_drug=log_group.has_drug,
                has_food=log_group.has_food,
                has_cond_score=log_group.has_cond_score,
                cond_score=log_group.cond_score
            )
            _js_list.append(_js)
        return _js_list

    @staticmethod
    def convert_tag_logs_into_js(tag_logs: [TagLog]) -> list:
        _js_list = list()
        for tag_log in tag_logs:
            _js = dict(
                id=tag_log.id,
                group_id=tag_log.group_id,
                tag_id=tag_log.tag_id,
                x_val=tag_log.x_val,
                y_val=tag_log.y_val,
                eng_name=tag_log.tag.eng_name,
                kor_name=tag_log.tag.kor_name,
                jpn_name=tag_log.tag.jpn_name
            )
            _js_list.append(_js)
        return _js_list

    @staticmethod
    def convert_a_tag_into_js(tag: Tag):
        _js = dict(id=tag.id,
                     tag_type=tag.tag_type,
                     eng_name=tag.eng_name,
                     kor_name=tag.kor_name,
                     jpn_name=tag.jpn_name)
        return _js

    @staticmethod
    def convert_tag_sets_into_js(tag_sets):
        _js_list = list()
        for tag_set in tag_sets:
            _js = dict(id=tag_set.sub.id,
                         tag_type=tag_set.sub.tag_type,
                         eng_name=tag_set.sub.eng_name,
                         kor_name=tag_set.sub.kor_name,
                         jpn_name=tag_set.sub.jpn_name)
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
                tag_id=profile_tag.tag_id,
                is_selected=profile_tag.is_selected,
                eng_name=profile_tag.tag.eng_name,
                kor_name=profile_tag.tag.kor_name,
                jpn_name=profile_tag.tag.jpn_name
            )
            _js_list.append(_js)
        return _js_list

    # GET methods
    # -------------------------------------------------------------------------
    @staticmethod
    def get_banners():
        banners = Banner.query.filter(
            Banner.is_active == True
        ).order_by(Banner.score).all()
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
    def get_a_avatar(avatar_id=None, email=None):
        if avatar_id is None:
            avatar = Avatar.query.filter(
                Avatar.email == email,
                Avatar.is_active == True
            ).first()
            return avatar
        avatar = Avatar.query.filter(
            Avatar.id == avatar_id,
            Avatar.is_active == True
        ).first()
        return avatar

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
                LogGroup.month_number == month_number
            ).order_by(
                LogGroup.day_of_year.desc(),
                LogGroup.group_type.desc()
            ).all()
            return log_groups
        log_groups = LogGroup.query.filter(
            LogGroup.avatar_id == avatar_id,
            LogGroup.year_number == year_number,
            LogGroup.week_of_year == week_of_year
        ).order_by(
            LogGroup.day_of_year.desc(),
            LogGroup.group_type.desc()
        ).all()
        return log_groups

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
    def get_tag_sets(super_id: int, sort_type):
        if sort_type == 'eng':
            tag_sets = db_session.query(TagSet).join(TagSet.sub).filter(
                TagSet.super_id == super_id,
                TagSet.is_active == True
            ).order_by(Tag.eng_name).all()
        elif sort_type == 'kor':
            tag_sets = db_session.query(TagSet).join(TagSet.sub).filter(
                TagSet.super_id == super_id,
                TagSet.is_active == True
            ).order_by(Tag.kor_name).all()
        elif sort_type == 'jpn':
            tag_sets = db_session.query(TagSet).join(TagSet.sub).filter(
                TagSet.super_id == super_id,
                TagSet.is_active == True
            ).order_by(Tag.jpn_name).all()
        elif sort_type == 'score':
            tag_sets = db_session.query(TagSet).filter(
                TagSet.super_id == super_id,
                TagSet.is_active == True
            ).order_by(TagSet.score.desc()).all()
        else:
            return False
        return tag_sets

    @staticmethod
    def get_a_profile_tag(profile_tag_id):
        profile_tag = ProfileTag.query.filter(
            ProfileTag.id == profile_tag_id,
            ProfileTag.is_active == True
        ).first()
        return profile_tag

    @staticmethod
    def get_profile_tags(avatar_id: int) -> [ProfileTag]:
        profile_tags = ProfileTag.query.filter(
            ProfileTag.avatar_id == avatar_id,
            ProfileTag.is_active == True
        ).order_by(ProfileTag.score.desc()).all()
        return profile_tags
    
    @staticmethod
    def get_a_tag_log(tag_log_id) -> TagLog:
        tag_log = TagLog.query.filter(
            TagLog.id == tag_log_id,
            TagLog.is_active == True
        ).first()
        return tag_log

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
                profile_type=Helpers.gen_random_profile_color()
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
            has_food = False
            has_act = False
            has_drug = False
            has_cond_score = False
            if tag.tag_type == TagType.food:
                has_food = True
            elif tag.tag_type == TagType.activity:
                has_act = True
            elif tag.tag_type == TagType.drug:
                has_drug = True
            new_log_group = LogGroup(
                avatar_id=data['avatar_id'],
                group_type=data['group_type'],
                year_number=data['year_number'],
                month_number=data['month_number'],
                week_of_year=data['week_of_year'],
                day_of_year=data['day_of_year'],
                log_date=data['log_date'],
                is_active=True,
                has_food=has_food,
                has_act=has_act,
                has_drug=has_drug,
                has_cond_score=has_cond_score
            )
            db_session.add(new_log_group)
            db_session.commit()
            log_group_id = new_log_group.id
        else:
            log_group = LogGroup.query.filter(
                LogGroup.id == log_group_id,
                LogGroup.avatar_id == data['avatar_id'],
                LogGroup.is_active == True
            ).first()
            if tag.tag_type == TagType.food:
                log_group.has_food = True
            elif tag.tag_type == TagType.activity:
                log_group.has_act = True
            elif tag.tag_type == TagType.drug:
                log_group.has_drug = True
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
    def create_profile_tag(avatar_id, tag_id, is_selected, score):
        profile_tag = ProfileTag(
            avatar_id=avatar_id,
            tag_id=tag_id,
            is_active=True,
            is_selected=is_selected,
            score=score
        )
        db_session.add(profile_tag)
        db_session.commit()
        return True

    @staticmethod
    def create_def_profile_tags(avatar_id, language_id):
        tag_sets = Helpers.get_tag_sets(super_id=19, sort_type='score')
        # ID-19: Profile
        for tag_set in tag_sets:
            if tag_set.sub_id == 20:
                # ID-20: Language
                Helpers.create_profile_tag(avatar_id=avatar_id,
                                           tag_id=language_id,
                                           is_selected=True,
                                           score=tag_set.score)
                continue
            Helpers.create_profile_tag(avatar_id=avatar_id,
                                       tag_id=tag_set.sub_id,
                                       is_selected=False,
                                       score=tag_set.score)
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
    def update_avatar_info(avatar_id, target, new_info):
        if target == AvatarInfo.first_name:
            avatar = Avatar.query.filter(
                Avatar.id == avatar_id,
                Avatar.is_active == True
            ).first()
            avatar.first_name = new_info
            avatar.modified_timestamp = text("timezone('utc'::text, now())")
            db_session.commit()
            return True
        elif target == AvatarInfo.last_name:
            avatar = Avatar.query.filter(
                Avatar.id == avatar_id,
                Avatar.is_active == True
            ).first()
            avatar.last_name = new_info
            avatar.modified_timestamp = text("timezone('utc'::text, now())")
            db_session.commit()
            return True
        elif target == AvatarInfo.intro:
            avatar = Avatar.query.filter(
                Avatar.id == avatar_id,
                Avatar.is_active == True
            ).first()
            avatar.introduction = new_info
            avatar.modified_timestamp = text("timezone('utc'::text, now())")
            db_session.commit()
            return True
        else:
            return False

    @staticmethod
    def update_profile_tag(profile_tag: ProfileTag, tag_id, is_selected):
        profile_tag.tag_id = tag_id
        profile_tag.is_selected = is_selected
        profile_tag.modified_timestamp = text("timezone('utc'::text, now())")
        db_session.commit()
        return True

    @staticmethod
    def update_log_group_cond_score(log_group: LogGroup, data):
        log_group.cond_score = data['cond_score']
        log_group.has_cond_score = True
        db_session.commit()
        return True
    
    @staticmethod
    def update_tag_log(tag_log: TagLog):
        tag_log.is_active = False
        db_session.commit()
        return True
