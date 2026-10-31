from flask import Blueprint, request, jsonify
from ..models import Device, Measurement, db
from sqlalchemy import desc
from datetime import datetime
from datetime import datetime, timedelta
import math
bp = Blueprint('measurement', __name__)

newData = {
    'rainFall': 0,
    'soil' : 0,
    'isNew': False
}


@bp.route('', methods=['GET'])
def get_measurement():
    """
    Lấy danh sách measurements với phân trang + lọc
    Query params hỗ trợ:
        page=1              → trang hiện tại (mặc định 1)
        per_page=50         → số bản ghi/trang (mặc định 50, tối đa 200)
        client_id=pico_001  → lọc theo thiết bị
        start=2025-04-01    → từ ngày (ISO format hoặc timestamp)
        end=2025-04-02      → đến ngày
        sort=desc           → desc (mới nhất trước) hoặc asc
    """
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    if per_page < 1:
        per_page = 50
    if per_page > 200:
        per_page = 200                      # giới hạn để tránh tải nặng

    client_id = request.args.get('client_id', type=str)
    start_str = request.args.get('start')
    end_str = request.args.get('end')
    sort = request.args.get('sort', 'desc')   # desc hoặc asc

    query = Measurement.query

    if client_id:
        # Kiểm tra device có tồn tại không (tùy chọn)
        if not Device.query.get(client_id):
            return jsonify({"error": "Device not found"}), 404
        query = query.filter(Measurement.client_id == client_id)

    if start_str:
        try:
            start_dt = datetime.fromisoformat(start_str.replace('Z', '+00:00'))
            query = query.filter(Measurement.timestamp >= start_dt)
        except:
            return jsonify({"error": "Invalid 'start' format. Use ISO8601"}), 400

    if end_str:
        try:
            end_dt = datetime.fromisoformat(end_str.replace('Z', '+00:00'))
            query = query.filter(Measurement.timestamp <= end_dt)
        except:
            return jsonify({"error": "Invalid 'end' format. Use ISO8601"}), 400

    if sort == 'asc':
        query = query.order_by(Measurement.timestamp.asc())
    else:
        query = query.order_by(desc(Measurement.timestamp))   # mới nhất trước

    pagination = query.paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )

    measurements = pagination.items

    results = []
    for m in measurements:
        results.append({
            "id": m.id,
            "client_id": m.client_id,
            "rainfall": m.rainfall,
            "humidity": m.humidity,
            "temperature": m.temperature,
            "timestamp": m.timestamp.isoformat() + "Z"
        })

    return jsonify({
        "data": results,
        "pagination": {
            "page": page,
            "per_page": per_page,
            "total": pagination.total,
            "pages": pagination.pages,
            "has_next": pagination.has_next,
            "has_prev": pagination.has_prev,
            "next_page": page + 1 if pagination.has_next else None,
            "prev_page": page - 1 if pagination.has_prev else None
        },
        "filters": {
            "client_id": client_id,
            "start": start_str,
            "end": end_str,
            "sort": sort
        }
    })
#TOdo: add logic to recieve measurements 
@bp.route("/<client_id>", methods=["POST"])
def handle_post_data_from_clientid(client_id):
    data = request.get_json()
    print (data)
    print(client_id)
    measure = Measurement(
        rainfall=data['rainfall'],
        humidity = data['humidity'],
        temperature=data['temperature'],
#ADD here
        client_id=client_id,
    )
    db.session.add(measure)
    db.session.commit()
    newData['isNew'] = True
    newData['rainFall'] = data['rainfall']
    newData['soil'] = data['humidity']
#ADD here
    return jsonify({"msg": "oke"})

@bp.route("/newest", methods=['GET'])
def handle_get_newset():
    if (newData['isNew'] == True) :
        newData['isNew'] = False
        return jsonify(newData)
    else : 
        return jsonify({"msg": "nodata"})
    

@bp.route('/stats', methods=['GET'])
def measurement_stats():
    client_id = request.args.get('client_id')
    query = db.session.query(
        db.func.count(Measurement.id),
        db.func.sum(Measurement.rainfall),
        db.func.avg(Measurement.humidity)
    )
    if client_id:
        query = query.filter(Measurement.client_id == client_id)
    total, total_rain, avg_hum = query.first()
    return jsonify({
        "total_records": total or 0,
        "total_rainfall_mm": round(total_rain or 0, 2),
        "avg_humidity": round(avg_hum or 0, 2) if avg_hum else None
    })

@bp.route('/last_3_days', methods=['GET'])
def measurement_last_3_days():
    client_id = request.args.get('client_id')

    now = datetime.utcnow()
    three_days_ago = now - timedelta(days=3)

    query = db.session.query(
        db.func.count(Measurement.id).label('count'),
        db.func.avg(Measurement.rainfall).label('avg_rainfall'),
        db.func.avg(Measurement.humidity).label('avg_humidity')
    ).filter(Measurement.timestamp >= three_days_ago)

    if client_id:
        query = query.filter(Measurement.client_id == client_id)

    result = query.first()
    return jsonify({
        "records_last_3_days": result.count or 0,
        "avg_rainfall_mm": round(result.avg_rainfall or 0, 2),
        "avg_humidity": round(result.avg_humidity or 0, 2)
    })

@bp.route('/avg_last_24_hours', methods=['GET'])
def get_average_last_24_hours():
   
    client_id = request.args.get('client_id')
    
    # 1. Define the time window (UTC)
    now = datetime.now()
    data_24_hours_ago = now - timedelta(days=1)

    # 2. Build the aggregation query
    query = db.session.query(
        db.func.count(Measurement.id).label('count'),
        db.func.avg(Measurement.rainfall).label('avg_rainfall'),
        db.func.avg(Measurement.humidity).label('avg_humidity'),
        db.func.avg(Measurement.temperature).label('avg_temperature')
    ).filter(Measurement.timestamp >= data_24_hours_ago)

    if client_id:
        query = query.filter(Measurement.client_id == client_id)
    result = query.first()

    response_data = {
        "period": "last_24_hours",
        "end_timestamp": now.isoformat() + "Z",
        "total_records": result.count,
        "averages": {
            "rainfall": round(result.avg_rainfall, 2) if result.avg_rainfall else 0,
            "humidity": round(result.avg_humidity, 2) if result.avg_humidity else 0,
            "temperature": round(result.avg_temperature, 2) if result.avg_temperature else 0
        }
    }

    return jsonify(response_data), 200
