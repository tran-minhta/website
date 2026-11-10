# PLAN — debugs.click (Bản Gốc từ Requirement)

**Phiên bản:** 1.0
**Ngày tạo:** 2026-11-09
**Công nghệ:** Python 3.10+, Flask, Blueprint, SQLAlchemy, Bcrypt, Dotenv, Bootstrap 5

---

## BƯỚC 1 — requirements.txt & .env.example

**requirements.txt:**
```
Flask==3.1.3
Flask-SQLAlchemy==3.1.1
Flask-Bcrypt==1.0.1
python-dotenv==1.0.1
```

**.env.example:**
```
SECRET_KEY=change_this_to_a_random_secret_key
DATABASE_URL=sqlite:///site.db
```

---

## BƯỚC 2 — app/__init__.py (App Factory Pattern)

- `db = SQLAlchemy()`
- `bcrypt = Bcrypt()`
- `create_app()` — Factory hàm tạo ứng dụng
- Config:
  - `SECRET_KEY` từ `.env`
  - `SQLALCHEMY_DATABASE_URI` từ `.env`
  - `SQLALCHEMY_TRACK_MODIFICATIONS = False`
  - `PERMANENT_SESSION_LIFETIME = 1800` (30 phút)
  - `SESSION_COOKIE_HTTPONLY = True`
  - `SESSION_COOKIE_SAMESITE = 'Lax'`
- Khởi tạo ext: `db.init_app(app)`, `bcrypt.init_app(app)`
- Đăng ký blueprints: `auth_bp`, `main_bp`
- Tự động `db.create_all()`, seed admin

---

## BƯỚC 3 — app/models.py (User Model)

```python
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    # Security columns (thêm sau)
    login_attempts = db.Column(db.Integer, default=0)
    lockout_until = db.Column(db.DateTime, nullable=True)
    reset_token = db.Column(db.String(128), nullable=True)
    reset_token_expiry = db.Column(db.DateTime, nullable=True)

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

    # Security methods
    def is_locked(self): ...
    def generate_reset_token(self): ...
    def is_reset_token_valid(self): ...
```

---

## BƯỚC 4 — Auth Blueprint

**File:** `app/auth/routes.py`

| Route | Method | Endpoint | Mô tả |
|-------|--------|----------|---------|
| `/auth/register` | GET/POST | `auth.register` | Đăng ký (mật khẩu mạnh) |
| `/auth/login` | GET/POST | `auth.login` | Đăng nhập (lockout) |
| `/auth/logout` | GET | `auth.logout` | Đăng xuất |

---

## BƯỚC 5 — Templates

| Template | Mô tả |
|----------|-------|
| `base.html` | Layout chung Bootstrap 5 |
| `auth/login.html` | Form đăng nhập + link quên mậtkhẩu |
| `auth/register.html` | Form đăng ký |
| `main/index.html` | Dashboard |

---

## BƯỚC 6 — run.py

```python
from app import create_app
app = create_app()
if __name__ == '__main__':
    app.run(debug=True)
```

---

## THÊM TÍNH NĂNG MỚI (Đã thực hiện sau)

### Account Blueprint (Quản lý tài khoản)
| Route | Method | Endpoint | Mô tả |
|-------|--------|----------|---------|
| `/account` | GET | `account.profile` | Profile |
| `/account/change-password` | GET/POST | `account.change_password` | Đổi mật khẩu |
| `/account/change-email` | GET/POST | `account.change_email` | Đổi email |
| `/account/security` | GET | `account.security` | Bảo mật |

### Recover Blueprint (Khôi phục mật khẩu)
| Route | Method | Endpoint | Mô tả |
|-------|--------|----------|---------|
| `/forgot-password` | GET/POST | `recover.forgot_password` | Quên mật khẩu |
| `/reset-password/<token>` | GET/POST | `recover.reset_password` | Đặt lại mật khẩu |

### Bảo vệ tài khoản
- **Lockout**: 5 lần sai → 15 phút
- **Strong password**: regex check (8+ chars, upper, lower, digit, special)
- **Session secure**: HTTPONLY, SAMESITE
- **Token reset**: 30 phút, unique per request
