# 顶部导入处（添加标准库依赖）
from flask import Blueprint, jsonify, request, abort
from flask_login import current_user
from sqlalchemy import select

from server.extensions import db
from server.models import Movie
from server.models import Event

import json
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
import os

# 新增：Open API 相关常量（支持通过环境变量覆盖）
SEOUL_API_SCHEME = os.getenv("SEOUL_API_SCHEME", "http")
SEOUL_API_HOST = os.getenv("SEOUL_API_HOST", "openapi.seoul.go.kr")
SEOUL_API_PORT = int(os.getenv("SEOUL_API_PORT", "8088"))
SEOUL_API_KEY = os.getenv("SEOUL_API_KEY", "55536d594f647a783131315245495256")
SEOUL_API_FORMAT = os.getenv("SEOUL_API_FORMAT", "json")
SEOUL_API_RESOURCE = os.getenv("SEOUL_API_RESOURCE", "culturalEventInfo")
SEOUL_DEFAULT_START = int(os.getenv("SEOUL_DEFAULT_START", "1"))
SEOUL_DEFAULT_END = int(os.getenv("SEOUL_DEFAULT_END", "5"))

api_bp = Blueprint('api', __name__)

# 新增：调用首尔文化活动 Open API 的示例端点
@api_bp.get('/external/seoul-events')
def seoul_events():
    # 构建 Open API 请求 URL
    url = f"{SEOUL_API_SCHEME}://{SEOUL_API_HOST}:{SEOUL_API_PORT}/{SEOUL_API_KEY}/{SEOUL_API_FORMAT}/{SEOUL_API_RESOURCE}/{SEOUL_DEFAULT_START}/{SEOUL_DEFAULT_END}"
    try:
        req = Request(url, headers={"User-Agent": "k_life_server/1.0"})
        with urlopen(req, timeout=5) as resp:
            status = getattr(resp, "status", 200)  # Py3.10+ 有 resp.status
            if status != 200:
                return jsonify({"error": "Upstream error", "status": status}), 502
            raw = resp.read()
            payload = json.loads(raw.decode("utf-8"))
    except (HTTPError, URLError) as e:
        return jsonify({"error": "Failed to fetch external API", "detail": str(e)}), 502
    except Exception as e:
        return jsonify({"error": "Unexpected error", "detail": str(e)}), 500

    return jsonify(payload), 200

def event_to_dict(e: Event) -> dict:
    return {
        "id": e.id,
        "CODENAME": e.code_name,
        "GUNAME": e.gu_name,
        "TITLE": e.title,
        "DATE": e.date,
        "PLACE": e.place,
        "ORG_NAME": e.org_name,
        "USE_TRGT": e.use_trgt,
        "USE_FEE": e.use_fee,
        "INQUIRY": e.inquiry,
        "PLAYER": e.player,
        "PROGRAM": e.program,
        "ETC_DESC": e.etc_desc,
        "ORG_LINK": e.org_link,
        "MAIN_IMG": e.main_img,
        "RGSTDATE": e.rgstdate,
        "TICKET": e.ticket,
        "STRTDATE": e.start_date,
        "END_DATE": e.end_date,
        "THEMECODE": e.theme_code,
        "LOT": e.lot,
        "LAT": e.lat,
        "IS_FREE": e.is_free,
        "HMPG_ADDR": e.hmpg_addr,
        "PRO_TIME": e.pro_time,
    }

# 新增：Event 列表
@api_bp.get('/events')
def list_events():
    events = db.session.execute(select(Event)).scalars().all()
    return jsonify([event_to_dict(e) for e in events]), 200

# 新增：Event 创建（写操作需登录）
@api_bp.post('/events')
def create_event():
    if not current_user.is_authenticated:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json(silent=True) or {}

    # 允许使用原始 Open API 的键来创建
    def pick(key, default=None):
        return data.get(key, default)

    # 经纬度尝试解析为 float
    def to_float(x):
        try:
            return float(x) if x is not None and x != "" else None
        except Exception:
            return None

    title = pick("TITLE")
    if not title:
        return jsonify({"error": "TITLE is required"}), 400

    e = Event(
        code_name=pick("CODENAME"),
        gu_name=pick("GUNAME"),
        title=title,
        date=pick("DATE"),
        place=pick("PLACE"),
        org_name=pick("ORG_NAME"),
        use_trgt=pick("USE_TRGT"),
        use_fee=pick("USE_FEE"),
        inquiry=pick("INQUIRY"),
        player=pick("PLAYER"),
        program=pick("PROGRAM"),
        etc_desc=pick("ETC_DESC"),
        org_link=pick("ORG_LINK"),
        main_img=pick("MAIN_IMG"),
        rgstdate=pick("RGSTDATE"),
        ticket=pick("TICKET"),
        start_date=pick("STRTDATE"),
        end_date=pick("END_DATE"),
        theme_code=pick("THEMECODE"),
        lot=to_float(pick("LOT")),
        lat=to_float(pick("LAT")),
        is_free=pick("IS_FREE"),
        hmpg_addr=pick("HMPG_ADDR"),
        pro_time=pick("PRO_TIME"),
    )
    db.session.add(e)
    db.session.commit()
    return jsonify(event_to_dict(e)), 201

# 新增：Event 查询
@api_bp.get('/events/<int:event_id>')
def get_event(event_id: int):
    e = db.session.get(Event, event_id)
    if not e:
        return jsonify({"error": "Not found"}), 404
    return jsonify(event_to_dict(e)), 200

# 新增：Event 更新（按提供的键更新）
@api_bp.put('/events/<int:event_id>')
def update_event(event_id: int):
    if not current_user.is_authenticated:
        return jsonify({"error": "Unauthorized"}), 401

    e = db.session.get(Event, event_id)
    if not e:
        return jsonify({"error": "Not found"}), 404

    data = request.get_json(silent=True) or {}

    def maybe_set(attr, key, transform=lambda x: x):
        if key in data:
            setattr(e, attr, transform(data[key]))

    maybe_set("code_name", "CODENAME")
    maybe_set("gu_name", "GUNAME")
    maybe_set("title", "TITLE")
    maybe_set("date", "DATE")
    maybe_set("place", "PLACE")
    maybe_set("org_name", "ORG_NAME")
    maybe_set("use_trgt", "USE_TRGT")
    maybe_set("use_fee", "USE_FEE")
    maybe_set("inquiry", "INQUIRY")
    maybe_set("player", "PLAYER")
    maybe_set("program", "PROGRAM")
    maybe_set("etc_desc", "ETC_DESC")
    maybe_set("org_link", "ORG_LINK")
    maybe_set("main_img", "MAIN_IMG")
    maybe_set("rgstdate", "RGSTDATE")
    maybe_set("ticket", "TICKET")
    maybe_set("start_date", "STRTDATE")
    maybe_set("end_date", "END_DATE")
    maybe_set("theme_code", "THEMECODE")
    maybe_set("lot", "LOT", lambda v: float(v) if v not in (None, "") else None)
    maybe_set("lat", "LAT", lambda v: float(v) if v not in (None, "") else None)
    maybe_set("is_free", "IS_FREE")
    maybe_set("hmpg_addr", "HMPG_ADDR")
    maybe_set("pro_time", "PRO_TIME")

    db.session.commit()
    return jsonify(event_to_dict(e)), 200

# 新增：Event 删除
@api_bp.delete('/events/<int:event_id>')
def delete_event(event_id: int):
    if not current_user.is_authenticated:
        return jsonify({"error": "Unauthorized"}), 401

    e = db.session.get(Event, event_id)
    if not e:
        return jsonify({"error": "Not found"}), 404

    db.session.delete(e)
    db.session.commit()
    return "", 204
        
def movie_to_dict(movie: Movie) -> dict:
    return {
        "id": movie.id,
        "title": movie.title,
        "year": movie.year,
    }

@api_bp.get('/movies')
def list_movies():
    movies = db.session.execute(select(Movie)).scalars().all()
    return jsonify([movie_to_dict(m) for m in movies]), 200

@api_bp.post('/movies')
def create_movie():
    if not current_user.is_authenticated:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json(silent=True) or {}
    title = data.get("title")
    year = data.get("year")

    if not title or not year or len(str(year)) != 4 or len(title) > 60:
        return jsonify({"error": "Invalid input"}), 400

    movie = Movie(title=title, year=str(year))
    db.session.add(movie)
    db.session.commit()
    return jsonify(movie_to_dict(movie)), 201

@api_bp.get('/movies/<int:movie_id>')
def get_movie(movie_id: int):
    movie = db.session.get(Movie, movie_id)
    if not movie:
        return jsonify({"error": "Not found"}), 404
    return jsonify(movie_to_dict(movie)), 200

@api_bp.put('/movies/<int:movie_id>')
def update_movie(movie_id: int):
    if not current_user.is_authenticated:
        return jsonify({"error": "Unauthorized"}), 401

    movie = db.session.get(Movie, movie_id)
    if not movie:
        return jsonify({"error": "Not found"}), 404

    data = request.get_json(silent=True) or {}
    title = data.get("title")
    year = data.get("year")

    if not title or not year or len(str(year)) != 4 or len(title) > 60:
        return jsonify({"error": "Invalid input"}), 400

    movie.title = title
    movie.year = str(year)
    db.session.commit()
    return jsonify(movie_to_dict(movie)), 200

@api_bp.delete('/movies/<int:movie_id>')
def delete_movie(movie_id: int):
    if not current_user.is_authenticated:
        return jsonify({"error": "Unauthorized"}), 401

    movie = db.session.get(Movie, movie_id)
    if not movie:
        return jsonify({"error": "Not found"}), 404

    db.session.delete(movie)
    db.session.commit()
    return "", 204

# 新增：批量导入首尔 Open API 的事件（需登录，含去重）
# @api_bp.post('/events/import-seoul')
@api_bp.get('/events/import-seoul')
def import_seoul_events():
    if not current_user.is_authenticated:
        return jsonify({"error": "Unauthorized"}), 401

    # 支持从 POST JSON 传入 start/end，否则使用默认常量
    start = SEOUL_DEFAULT_START
    end = SEOUL_DEFAULT_END
    if request.is_json:
        body = request.get_json(silent=True) or {}
        start = int(body.get("start", start))
        end = int(body.get("end", end))

    url = (
        f"{SEOUL_API_SCHEME}://{SEOUL_API_HOST}:{SEOUL_API_PORT}/"
        f"{SEOUL_API_KEY}/{SEOUL_API_FORMAT}/{SEOUL_API_RESOURCE}/{start}/{end}"
    )

    try:
        req = Request(url, headers={"User-Agent": "k_life_server/1.0"})
        with urlopen(req, timeout=5) as resp:
            status = getattr(resp, "status", 200)
            if status != 200:
                return jsonify({"error": "Upstream error", "status": status}), 502
            raw = resp.read()
            payload = json.loads(raw.decode("utf-8"))
    except (HTTPError, URLError) as e:
        return jsonify({"error": "Failed to fetch external API", "detail": str(e)}), 502
    except Exception as e:
        return jsonify({"error": "Unexpected error", "detail": str(e)}), 500

    from server.models import Event  # 局部导入以减少上方改动

    def to_float(x):
        try:
            return float(x) if x not in (None, "") else None
        except Exception:
            return None

    rows = (payload.get("culturalEventInfo") or {}).get("row") or []
    to_create = []
    imported = 0
    skipped = 0

    for r in rows:
        title = r.get("TITLE")
        place = r.get("PLACE")
        strtdate = r.get("STRTDATE")
        if not title:
            skipped += 1
            continue

        # 去重依据：TITLE + PLACE + STRTDATE
        existing = db.session.execute(
            select(Event).filter_by(title=title, place=place, start_date=strtdate)
        ).scalar()

        if existing:
            skipped += 1
            continue

        e = Event(
            code_name=r.get("CODENAME"),
            gu_name=r.get("GUNAME"),
            title=title,
            date=r.get("DATE"),
            place=place,
            org_name=r.get("ORG_NAME"),
            use_trgt=r.get("USE_TRGT"),
            use_fee=r.get("USE_FEE"),
            inquiry=r.get("INQUIRY"),
            player=r.get("PLAYER"),
            program=r.get("PROGRAM"),
            etc_desc=r.get("ETC_DESC"),
            org_link=r.get("ORG_LINK"),
            main_img=r.get("MAIN_IMG"),
            rgstdate=r.get("RGSTDATE"),
            ticket=r.get("TICKET"),
            start_date=strtdate,
            end_date=r.get("END_DATE"),
            theme_code=r.get("THEMECODE"),
            lot=to_float(r.get("LOT")),
            lat=to_float(r.get("LAT")),
            is_free=r.get("IS_FREE"),
            hmpg_addr=r.get("HMPG_ADDR"),
            pro_time=r.get("PRO_TIME"),
        )
        to_create.append(e)

    if to_create:
        db.session.add_all(to_create)
        db.session.commit()
        imported = len(to_create)

    return jsonify({
        "imported": imported,
        "skipped_duplicates_or_invalid": skipped,
        "requested_range": {"start": start, "end": end}
    }), 200