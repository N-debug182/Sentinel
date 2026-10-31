from flask_socketio import emit, disconnect
from flask import request
from ..models import Device, Measurement, db
from datetime import datetime
import json

def register_pico_events(socketio):
    @socketio.on('connect', namespace='/pico')
    def handle_connect():
        print('Pi Pico connected:', request.sid)

    @socketio.on('disconnect', namespace='/pico')
    def handle_disconnect():
        print('Pi Pico disconnected:', request.sid)

    @socketio.on('pico_data', namespace='/pico')
    def handle_pico_data(data):
        try:
            # data mẫu từ Pico: {"id": "pico_01", "rain": 12.5, "hum": 87.3, "temp": 24.1}
            device_id = data["id"]

            # Cập nhật trạng thái online + last_update
            device = Device.query.get(device_id)
            if not device:
                # Tự động tạo nếu chưa có (tuỳ nhu cầu)
                device = Device(id=device_id, name=device_id, is_online=True)
                db.session.add(device)
            device.is_online = True

            # Lưu measurement
            meas = Measurement(
                rainfall=data.get("rain"),
                humidity=data.get("hum"),
                temperature=data.get("temp"),
                client_id=device_id
            )
            db.session.add(meas)
            db.session.commit()

            # Phát lại cho các client web (nếu cần)
            socketio.emit('new_measurement', {
                "device_id": device_id,
                "rainfall": data.get("rain"),
                "humidity": data.get("hum"),
                "temperature": data.get("temp"),
                "timestamp": datetime.utcnow().isoformat()
            }, namespace='/web')

            emit('ack', {'status': "ok"})  # xác nhận cho Pico
        except Exception as e:
            print("Error processing pico data:", e)
            emit('error', {'msg': str(e)})