from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
import os
from dotenv import load_dotenv
from datetime import timedelta

# Tải các biến môi trường từ file .env
load_dotenv()

# Khởi tạo các extension
db = SQLAlchemy()
bcrypt = Bcrypt()


def create_app(config_class=None):
    """
    Application factory pattern.
    Cho phép tạo nhiều cấu hình (development, production, test).
    """
    app = Flask(__name__)

    # Cấu hình ứng dụng
    app.config['SECRET_KEY'] = os.getenv(
        'SECRET_KEY', 'default-secret-key-change-in-production'
    )
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
        'DATABASE_URL', 'sqlite:///site.db'
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    # Thời hạn phiên (30 phút = 1800 giây)
    app.config['PERMANENT_SESSION_LIFETIME'] = 1800
    # Bảo mật cookie session
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

    # Khởi tạo Extension với App
    db.init_app(app)
    bcrypt.init_app(app)

    # Đăng ký Blueprint
    from app.auth.routes import auth_bp
    from app.main.routes import main_bp
    from app.account.routes import account_bp
    from app.recover.routes import recover_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(main_bp, url_prefix='/')
    app.register_blueprint(account_bp, url_prefix='/account')
    app.register_blueprint(recover_bp)

    # Tự động tạo database và seed dữ liệu
    with app.app_context():
        db.create_all()

        # Kiểm tra và tạo admin mặc định nếu chưa có
        from app.models import User
        admin_exists = User.query.filter_by(email='admin@example.com').first()
        if not admin_exists:
            admin = User(username='admin', email='admin@example.com')
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print('=== Admin mặc định đã được tạo ===')
            print('Email: admin@example.com | Password: admin123')

    return app
