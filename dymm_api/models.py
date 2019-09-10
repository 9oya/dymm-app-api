from sqlalchemy import (Boolean, Column, Date, DateTime, ForeignKey, Integer,
                        SmallInteger, String, text, Text, CHAR)
from sqlalchemy.orm import relationship
from dymm_api import db

Base = db.Model


class Avatar(Base):
    __tablename__ = 'avatar'

    id = Column(Integer, primary_key=True)
    is_active = Column(Boolean, nullable=False)
    is_admin = Column(Boolean, nullable=False)
    is_blocked = Column(Boolean, nullable=False)
    is_confirmed = Column(Boolean, nullable=False)
    email = Column(String(255), nullable=False)
    password_hash = Column(String(200), nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    ph_number = Column(String(50))
    profile_type = Column(Integer, nullable=False)
    introduction = Column(String(200))
    created_timestamp = Column(DateTime, server_default=text("timezone('utc'::text, now())"))
    modified_timestamp = Column(DateTime)
    date_of_birth = Column(CHAR(10))


class Banner(Base):
    __tablename__ = 'banner'

    id = Column(Integer, primary_key=True)
    is_active = Column(Boolean, nullable=False)
    priority = Column(SmallInteger, nullable=False, server_default=text("0"))
    eng_title = Column(String(200))
    kor_title = Column(String(200))
    jpn_title = Column(String(200))
    eng_subtitle = Column(String(300))
    kor_subtitle = Column(String(300))
    jpn_subtitle = Column(String(300))
    img_name = Column(String(100))
    txt_color = Column(String(100))
    bg_color = Column(String(100))
    created_timestamp = Column(DateTime, server_default=text("timezone('utc'::text, now())"))
    modified_timestamp = Column(DateTime)


class Tag(Base):
    __tablename__ = 'tag'

    id = Column(Integer, primary_key=True)
    tag_type = Column(Integer)
    is_active = Column(Boolean, nullable=False)
    has_set = Column(Boolean, nullable=False)
    eng_name = Column(String(200))
    kor_name = Column(String(200))
    jpn_name = Column(String(200))
    class1 = Column(SmallInteger)
    division1 = Column(SmallInteger)
    division2 = Column(SmallInteger)
    division3 = Column(SmallInteger)
    division4 = Column(SmallInteger)
    division5 = Column(SmallInteger)
    has_low_div = Column(Boolean)
    has_icon = Column(Boolean)
    created_timestamp = Column(DateTime, server_default=text("timezone('utc'::text, now())"))
    modified_timestamp = Column(DateTime)


class AdminLog(Base):
    __tablename__ = 'admin_log'

    id = Column(Integer, primary_key=True)
    admin_id = Column(ForeignKey('avatar.id', ondelete='CASCADE'), nullable=False, index=True)
    crud_table_name = Column(String(100), nullable=False)
    crud_type = Column(SmallInteger, nullable=False, comment='1: Create, 2: Reference, 3: Update, 4: Delete')
    crud_timestamp = Column(DateTime, nullable=False, server_default=text("timezone('utc'::text, now())"))
    ip_address = Column(String(100))

    admin = relationship('Avatar')


class AvatarCond(Base):
    __tablename__ = 'avatar_cond'

    id = Column(Integer, primary_key=True)
    avatar_id = Column(ForeignKey('avatar.id', ondelete='CASCADE'), nullable=False, index=True)
    tag_id = Column(ForeignKey('tag.id', ondelete='CASCADE'), nullable=False, index=True)
    is_active = Column(Boolean, nullable=False)
    start_date = Column(Date)
    end_date = Column(Date)
    created_timestamp = Column(DateTime, server_default=text("timezone('utc'::text, now())"))
    modified_timestamp = Column(DateTime)

    avatar = relationship('Avatar')
    tag = relationship('Tag')


class Bookmark(Base):
    __tablename__ = 'bookmark'

    id = Column(Integer, primary_key=True)
    avatar_id = Column(ForeignKey('avatar.id', ondelete='CASCADE'), nullable=False, index=True)
    super_tag_id = Column(ForeignKey('tag.id', ondelete='CASCADE'), nullable=False, index=True)
    sub_tag_id = Column(ForeignKey('tag.id', ondelete='CASCADE'), nullable=False, index=True)
    is_active = Column(Boolean, nullable=False)
    created_timestamp = Column(DateTime, server_default=text("timezone('utc'::text, now())"))
    modified_timestamp = Column(DateTime)

    avatar = relationship('Avatar')
    sub_tag = relationship('Tag', primaryjoin='Bookmark.sub_tag_id == Tag.id')
    super_tag = relationship('Tag', primaryjoin='Bookmark.super_tag_id == Tag.id')


class LogGroup(Base):
    __tablename__ = 'log_group'

    id = Column(Integer, primary_key=True)
    avatar_id = Column(ForeignKey('avatar.id', ondelete='CASCADE'), nullable=False, index=True)
    year_number = Column(SmallInteger, nullable=False)
    month_number = Column(SmallInteger, nullable=False)
    week_of_year = Column(SmallInteger, nullable=False)
    day_of_year = Column(SmallInteger, nullable=False)
    group_type = Column(SmallInteger, nullable=False, comment='1: Morning, 2: Daytime, 3: Evening, 4: Nighttime')
    is_active = Column(Boolean, nullable=False)
    log_date = Column(Date)
    food_cnt = Column(SmallInteger, nullable=False)
    act_cnt = Column(SmallInteger, nullable=False)
    drug_cnt = Column(SmallInteger, nullable=False)
    cond_score = Column(SmallInteger)
    created_timestamp = Column(DateTime, server_default=text("timezone('utc'::text, now())"))
    modified_timestamp = Column(DateTime)
    note = Column(Text)

    avatar = relationship('Avatar')


class LogHistory(Base):
    __tablename__ = 'log_history'

    id = Column(Integer, primary_key=True)
    avatar_id = Column(ForeignKey('avatar.id', ondelete='CASCADE'), nullable=False, index=True)
    tag_id = Column(ForeignKey('tag.id', ondelete='CASCADE'), nullable=False, index=True)
    is_active = Column(Boolean, nullable=False)
    created_timestamp = Column(DateTime, server_default=text("timezone('utc'::text, now())"))
    modified_timestamp = Column(DateTime)

    avatar = relationship('Avatar')
    tag = relationship('Tag')


class ProfileTag(Base):
    __tablename__ = 'profile_tag'

    id = Column(Integer, primary_key=True)
    avatar_id = Column(ForeignKey('avatar.id', ondelete='CASCADE'), nullable=False, index=True)
    tag_id = Column(ForeignKey('tag.id', ondelete='CASCADE'), nullable=False, index=True)
    is_active = Column(Boolean, nullable=False)
    is_selected = Column(Boolean, nullable=False)
    priority = Column(SmallInteger, nullable=False, server_default=text("0"))
    created_timestamp = Column(DateTime, server_default=text("timezone('utc'::text, now())"))
    modified_timestamp = Column(DateTime)

    avatar = relationship('Avatar')
    tag = relationship('Tag')


class TagSet(Base):
    __tablename__ = 'tag_set'

    id = Column(Integer, primary_key=True)
    super_id = Column(ForeignKey('tag.id', ondelete='CASCADE'), nullable=False, index=True)
    sub_id = Column(ForeignKey('tag.id', ondelete='CASCADE'), nullable=False, index=True)
    is_active = Column(Boolean, nullable=False)
    priority = Column(Integer, nullable=False, server_default=text("0"))
    created_timestamp = Column(DateTime, server_default=text("timezone('utc'::text, now())"))
    modified_timestamp = Column(DateTime)

    sub = relationship('Tag', primaryjoin='TagSet.sub_id == Tag.id')
    super = relationship('Tag', primaryjoin='TagSet.super_id == Tag.id')


class TagLog(Base):
    __tablename__ = 'tag_log'

    id = Column(Integer, primary_key=True)
    group_id = Column(ForeignKey('log_group.id', ondelete='CASCADE'), nullable=False, index=True)
    tag_id = Column(ForeignKey('tag.id', ondelete='CASCADE'), nullable=False, index=True)
    is_active = Column(Boolean, nullable=False)
    x_val = Column(SmallInteger)
    y_val = Column(SmallInteger)
    create_timestamp = Column(DateTime, server_default=text("timezone('utc'::text, now())"))
    modified_timestamp = Column(DateTime)

    group = relationship('LogGroup')
    tag = relationship('Tag')
