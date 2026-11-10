from app import db, bcrypt
from datetime import datetime, timedelta


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    # ===== CỘT BẢO VỆ TÀI KHOẢN =====
    login_attempts = db.Column(db.Integer, default=0)   # Số lần đăng nhập sai
    lockout_until = db.Column(db.DateTime, nullable=True)  # Thời gian khóa
    reset_token = db.Column(db.String(128), nullable=True)   # Token reset mật khẩu
    reset_token_expiry = db.Column(db.DateTime, nullable=True)  # Hạn dùng token

    def set_password(self, password):
        """Băm mật khẩu trước khi lưu vào database"""
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        """Kiểm tra mật khẩu"""
        return bcrypt.check_password_hash(self.password_hash, password)

    def increment_login_attempts(self):
        """Tăng số lần đăng nhập thất bại"""
        self.login_attempts += 1

    def reset_login_attempts(self):
        """Reset số lần đăng nhập thất bại"""
        self.login_attempts = 0

    def lock_account(self):
        """Khóa tài khoản 15 phút"""
        self.lockout_until = datetime.utcnow() + timedelta(minutes=15)

    def unlock_account(self):
        """Mở khóa tài khoản"""
        self.lockout_until = None

    def is_locked(self):
        """Kiểm tra tài khoản có bị khóa không"""
        if self.lockout_until is None:
            return False
        return datetime.utcnow() < self.lockout_until

    def generate_reset_token(self):
        """Tạo token reset mật khẩu (hạn 30 phút)"""
        import secrets
        self.reset_token = secrets.token_urlsafe(32)
        self.reset_token_expiry = datetime.utcnow() + timedelta(minutes=30)

    def is_reset_token_valid(self):
        """Kiểm tra token reset có hợp lệ không"""
        if self.reset_token is None or self.reset_token_expiry is None:
            return False
        return datetime.utcnow() < self.reset_token_expiry

    def update_password(self, new_password):
        """Cập nhật mật khẩu mới"""
        self.set_password(new_password)

    def update_email(self, new_email):
        """Cập nhật email"""
        self.email = new_email

    def __repr__(self):
        return f"<User {self.username}>"
