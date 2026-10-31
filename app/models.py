from . import db
from datetime import datetime


class Device(db.Model):
    __tablename__ = "devices"
    id = db.Column(db.String(50), primary_key=True)  # UUID hoặc MAC
    name = db.Column(db.String(100), nullable=False)
    longitude = db.Column(db.Float)
    latitude = db.Column(db.Float)
    forest_cover = db.Column(db.Float)      # % che phủ rừng
    slope = db.Column(db.Float)             # độ dốc
    is_online = db.Column(db.Boolean, default=False)

    measurements = db.relationship(
        "Measurement", backref="device", lazy=True, cascade="all, delete-orphan")
    analysis = db.relationship(
        "Analysis", backref="device", lazy=True, cascade="all, delete-orphan")


class Measurement(db.Model):
    __tablename__ = "measurements"
    id = db.Column(db.Integer, primary_key=True)
    rainfall = db.Column(db.Float)           # mm
    humidity = db.Column(db.Float)           # %
    temperature = db.Column(db.Float, nullable=True)  # nếu có
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    client_id = db.Column(db.String(50), db.ForeignKey(
        "devices.id"), nullable=False)
#add thêm: pm2.5, pm10, wind speed

class Analysis(db.Model):
    __tablename__ = "analysis"
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.String(50), db.ForeignKey(
        "devices.id"), nullable=False)
    risk_level = db.Column(db.String(20))    # low / medium / high / critical
    alert = db.Column(db.Text)
    calculated_at = db.Column(db.DateTime, default=datetime.utcnow)
    # Thêm các trường phân tích sau này: dự báo lũ, xói mòn...
