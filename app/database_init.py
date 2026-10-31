# app/database_init.py
import os
import sys
from datetime import datetime

# Thêm đường dẫn dự án vào sys.path để import được app
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from app import create_app, db
from app.models import Device, Measurement, Analysis

def init_db():
    app = create_app()
    with app.app_context():
        print("Đang tạo các bảng trong database...")
        db.create_all()  # Tạo tất cả bảng từ models nếu chưa tồn tại

        # Kiểm tra xem đã có dữ liệu mẫu chưa
        if Device.query.first():
            print("Database đã có dữ liệu rồi, bỏ qua việc tạo mẫu.")
            return

        print("Tạo dữ liệu mẫu...")

        # === Tạo một vài thiết bị mẫu ===
        devices = [
            Device(
                id="pico_001",
                name="Trạm An Lão",
                longitude=108.745,
                latitude=14.823,
                forest_cover=78.5,
                slope=12.3,
                is_online=True,
            ),
            Device(
                id="pico_002",
                name="Trạm Kon Plông",
                longitude=108.312,
                latitude=14.678,
                forest_cover=92.0,
                slope=28.7,
                is_online=False,
            ),
            Device(
                id="pico_003",
                name="Trạm Sa Thầy",
                longitude=107.891,
                latitude=14.412,
                forest_cover=45.2,
                slope=5.1,
                is_online=True,
            )
        ]

        db.session.bulk_save_objects(devices)

        # === Tạo một vài bản ghi đo mẫu cho pico_001 ===
        from datetime import timedelta
        now = datetime.utcnow()
        measurements = []
        for i in range(20):
            ts = now - timedelta(minutes=10 * i)
            measurements.append(Measurement(
                rainfall=round(0.0 + i * 2.3, 2) if i > 10 else 0.0,
                humidity=round(65 + i * 1.5, 1),
                temperature=round(24 + i * 0.3, 1),
                timestamp=ts,
                client_id="pico_001"
            ))

        db.session.bulk_save_objects(measurements)

        # === Tạo một bản ghi phân tích mẫu ===
        analysis = Analysis(
            client_id="pico_001",
            risk_level="high",
            alert="Lượng mưa vượt ngưỡng 150mm/12h, nguy cơ lũ quét cao!",
            calculated_at=datetime.utcnow()
        )
        db.session.add(analysis)

        db.session.commit()
        print("Khởi tạo database thành công! Đã tạo 3 thiết bị và dữ liệu mẫu.")
        print("   → Truy cập: http://127.0.0.1:5000")
        print("   → WebSocket cho Pico: ws://your-ip:5000/pico")
        print("   → WebSocket cho client web: ws://your-ip:5000/web")

if __name__ == "__main__":
    init_db()