from flask import Blueprint, request, jsonify
from ..models import Device, db

bp = Blueprint('device', __name__)

@bp.route('', methods=['GET'])
def get_devices():
    devices = Device.query.all()
    # hoặc dùng marshmallow để serialize đẹp hơn
    result = []
    for device in devices:
        result.append({
            "id": device.id,
            "name": device.name,
            "longitude": device.longitude,
            "latitude": device.latitude,
            "forest_cover": device.forest_cover,
            "slope": device.slope,
            "is_online": device.is_online,
        })
    return jsonify(result)


@bp.route('/<device_id>', methods=['GET'])
def get_device(device_id):
    device = Device.query.get_or_404(device_id)
    return jsonify({
        "id": device.id,
        "name": device.name,
        "longitude": device.longitude,
        "latitude": device.latitude,
        "forest_cover": device.forest_cover,
        "slope": device.slope,
        "is_online": device.is_online,
    })


@bp.route('', methods=['POST'])
def create_device():
    data = request.get_json()
    device = Device(
        id=data['id'],
        name=data['name'],
        longitude=data.get('longitude'),
        latitude=data.get('latitude'),
        forest_cover=data.get('forest_cover'),
        slope=data.get('slope')
    )
    db.session.add(device)
    db.session.commit()
    return jsonify({"success": True, "device_id": device.id}), 201


@bp.route('/<device_id>', methods=['PUT'])
def update_device(device_id):
    device = Device.query.get_or_404(device_id)
    data = request.get_json()
    for key in ['name', 'longitude', 'latitude', 'forest_cover', 'slope']:
        if key in data:
            setattr(device, key, data[key])
    db.session.commit()
    return jsonify({"success": True})


@bp.route('/<device_id>', methods=['DELETE'])
def delete_device(device_id):
    device = Device.query.get_or_404(device_id)
    db.session.delete(device)
    db.session.commit()
    return jsonify({"success": True}), 204
