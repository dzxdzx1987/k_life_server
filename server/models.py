from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from server import db


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))
    username = db.Column(db.String(20))
    password_hash = db.Column(db.String(128))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def validate_password(self, password):
        return check_password_hash(self.password_hash, password)


class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(60))
    year = db.Column(db.String(4))

class BusRouteInfo(db.Model):
    busRouteId = db.Column(db.Integer, primary_key=True)
    busRouteNm = db.Column(db.String(30))
    busRouteAbrv = db.Column(db.String(30))
    length = db.Column(db.Float)
    routeType = db.Column(db.Integer)
    stStationNm = db.Column(db.String(128))
    edStationNm = db.Column(db.String(128))
    term = db.Column(db.Integer)
    lastBusYn = db.Column(db.String(1))
    lastBusTm = db.Column(db.Integer)
    firstBusTm = db.Column(db.Integer)
    lastLowTm = db.Column(db.Integer)
    firstLowTm = db.Column(db.Integer)
    corpNm = db.Column(db.String(128))
    createdTm = db.Column(db.DateTime)


