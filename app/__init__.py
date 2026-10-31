from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_socketio import SocketIO
from .config import Config
import os

db = SQLAlchemy()
migrate = Migrate()
# socketio = SocketIO(cors_allowed_origins="*", async_mode="eventlet")
socketio = SocketIO(async_mode="threading")

def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(Config)

    os.makedirs(app.instance_path, exist_ok=True)
    print(f"Instance path: {app.instance_path}")

    db_path = os.path.join(app.instance_path, 'app.db')
    if not os.path.exists(db_path):
        open(db_path, 'a').close()
        os.chmod(db_path, 0o666)
        print(f"Tạo database file: {db_path}")

    db.init_app(app)
    migrate.init_app(app, db)
    socketio.init_app(app)

    # Register blueprints
    from .routes.device import bp as device_bp
    from .routes.measurement import bp as measurement_bp
    from .routes.analysis import bp as analysis_bp
    from .routes.data import bp as data_bp

    app.register_blueprint(device_bp, url_prefix="/api/devices")
    app.register_blueprint(measurement_bp, url_prefix="/api/measurements")
    app.register_blueprint(analysis_bp, url_prefix="/api/analysis")
    app.register_blueprint(data_bp, url_prefix="/api/data")

    @app.route("/")
    def index():
        return render_template("index.html")

    # Register socket events WebSocket
    from .sockets.socket import register_pico_events
    register_pico_events(socketio)

    return app
