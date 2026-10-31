from flask import Blueprint, request, jsonify
from ..models import Device, Measurement, Analysis, db
from sqlalchemy import desc
from datetime import datetime, timedelta

bp = Blueprint('data', __name__)


@bp.route('', methods=['GET'])
def get_data():
    data = {
        "rain": [123, 100],
        "soil": [123, 20],
        "time" : ["01-29-2026", "01-29-2026", ]
    }
    return data


@bp.route('', methods=['POST'])
def create_analysis():
    """
    lấy thông tin ngày nào cần tạo phân tích từ args
    lấy thông tin clientid nào cần phân tích từ args
    lấy thông tin slope, che phủ, tọa độm ... của client thông qua Device class
    lấy thông tin measurement từ Measurement (xem cách query)
    => phân tích nguy cơ sạt lở 
    => lưu lại vào trong Analysis db (xem create_device)
    """
    return


@bp.route("/device", methods=['GET'])
def get_devices():
    device = Device.query.get_or_404("pico_001")

    now = datetime.now()
    data_24_hours_ago = now - timedelta(days=100)

    # 2. Build the aggregation query
    query = db.session.query(
        db.func.count(Measurement.id).label('count'),
        db.func.avg(Measurement.rainfall).label('avg_rainfall'),
        db.func.avg(Measurement.humidity).label('avg_humidity'),
        db.func.avg(Measurement.temperature).label('avg_temperature')
    ).filter(Measurement.timestamp >= data_24_hours_ago)

    query = query.filter(Measurement.client_id == "pico_001")
    result = query.first()

    slope_norm = min(device.slope, 60) / 60
    slope_factor = slope_norm ** 2

    rain_factor = min(result.avg_rainfall / 300, 1)

    soil_norm = min(result.avg_humidity / 100, 1)

    if soil_norm > 0.8:
        soil_norm = soil_norm * 1.2  # Artificial boost for "liquid limit"
        soil_norm = min(soil_norm, 1) # Clamp back to 1

    tree_norm = min(device.forest_cover / 100, 1)
    water_stress = (rain_factor * 0.65) + (soil_norm * 0.35)
    raw_risk = slope_factor * water_stress
    raw_risk = raw_risk * (1 - (tree_norm * 0.3))
    probability = raw_risk * 4.5
    probability = min(max(probability, 0), 1)
    if device.slope < 1: #change this
        probability = 0.0
    if result.avg_rainfall < 10 and result.avg_humidity < 20:
        probability = 0.0,
    zone = ""
    if probability < 0.20:
        zone = "SAFE"
    elif probability < 0.40:
        zone = "CAUTION"
    elif probability < 0.70:
        zone = "WARNING"
    else:
        zone = "DANGER – EVACUATE"

    return {
        "name": device.name,
        "place": device.id,
        "rain" : result.avg_rainfall,
        "soil": result.avg_humidity,
        "cautionText": zone,
        "prob": probability,
        "slope": device.slope
    }
#thêm tốc độ gió, vào phân tích