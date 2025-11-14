from typing import Optional

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from server.extensions import db


class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(20))
    username: Mapped[str] = mapped_column(String(20))
    password_hash: Mapped[Optional[str]] = mapped_column(String(128))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def validate_password(self, password):
        return check_password_hash(self.password_hash, password)


class Movie(db.Model):
    __tablename__ = 'movie'
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(60))
    year: Mapped[str] = mapped_column(String(4))

# 新增：Event 模型，字段依据原始 Open API JSON（culturalEventInfo.row）
class Event(db.Model):
    __tablename__ = 'event'
    id: Mapped[int] = mapped_column(primary_key=True)

    # 原始 JSON 字段（示例：CODENAME、GUNAME、TITLE、...）
    code_name: Mapped[Optional[str]] = mapped_column(String(50))         # CODENAME
    gu_name: Mapped[Optional[str]] = mapped_column(String(50))           # GUNAME
    title: Mapped[str] = mapped_column(String(200))                      # TITLE
    date: Mapped[Optional[str]] = mapped_column(String(50))              # DATE
    place: Mapped[Optional[str]] = mapped_column(String(200))            # PLACE
    org_name: Mapped[Optional[str]] = mapped_column(String(100))         # ORG_NAME
    use_trgt: Mapped[Optional[str]] = mapped_column(String(100))         # USE_TRGT
    use_fee: Mapped[Optional[str]] = mapped_column(String(100))          # USE_FEE
    inquiry: Mapped[Optional[str]] = mapped_column(String(100))          # INQUIRY
    player: Mapped[Optional[str]] = mapped_column(String(255))           # PLAYER
    program: Mapped[Optional[str]] = mapped_column(String(255))          # PROGRAM
    etc_desc: Mapped[Optional[str]] = mapped_column(String(255))         # ETC_DESC
    org_link: Mapped[Optional[str]] = mapped_column(String(255))         # ORG_LINK
    main_img: Mapped[Optional[str]] = mapped_column(String(255))         # MAIN_IMG
    rgstdate: Mapped[Optional[str]] = mapped_column(String(30))          # RGSTDATE
    ticket: Mapped[Optional[str]] = mapped_column(String(50))            # TICKET
    start_date: Mapped[Optional[str]] = mapped_column(String(30))        # STRTDATE
    end_date: Mapped[Optional[str]] = mapped_column(String(30))          # END_DATE
    theme_code: Mapped[Optional[str]] = mapped_column(String(50))        # THEMECODE
    lot: Mapped[Optional[float]] = mapped_column(nullable=True)          # LOT (longitude)
    lat: Mapped[Optional[float]] = mapped_column(nullable=True)          # LAT (latitude)
    is_free: Mapped[Optional[str]] = mapped_column(String(10))           # IS_FREE
    hmpg_addr: Mapped[Optional[str]] = mapped_column(String(255))        # HMPG_ADDR
    pro_time: Mapped[Optional[str]] = mapped_column(String(100))         # PRO_TIME
