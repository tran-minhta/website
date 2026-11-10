# ARCHITECTURE DESIGN — debugs.click

## 1. Giới thiệu

Ứng dụng **debugs.click** được xây dựng theo **Modular Blueprint Architecture** chuẩn Flask.
Định hình từ requirement ban đầu, áp dụng **Application Factory Pattern** để tối ưu khả năng mở rộng.

---

## 2. Kiến trúc tổng quan

```
┌─────────────────────────────────────────────────────────────┐
│                      Flask App Factory                       │
│  create_app() → config → db.init → bcrypt.init → register   │
└─────────────────────────────────────────────────────────────┘
          │
          ├── register → auth_bp  (url_prefix='/auth')
          │     ├── /auth/register  (GET/POST)
          │     ├── /auth/login     (GET/POST)
          │     └── /auth/logout    (GET)
          │
          ├── register → main_bp  (url_prefix='/')
          │     ├── /             (GET)
          │     └── /dashboard    (GET)
          │
          ├── register → account_bp (url_prefix='/account')
          │     ├── /account       (GET) — Profile
          │     ├── /account/change-password  (GET/POST)
          │     ├── /account/change-email     (GET/POST)
          │     └── /account/security         (GET)
          │
          └── register → recover_bp (no prefix)
                ├── /forgot-password     (GET/POST)
                └── /reset-password/<token> (GET/POST)
```

---

## 3. 4 Blueprints Chi Tiết

### 3.1 `auth_bp` — Module Auth

**File:** `app/auth/routes.py`

| Route | Method | Endpoint | Mô tả |
|-------|--------|----------|---------|
| `/auth/register` | GET/POST | `auth.register` | Form đăng ký tài khoản |
| `/auth/login` | GET/POST | `auth.login` | Form đăng nhập |
| `/auth/logout` | GET | `auth.logout` | Đăng xuất |

**Đặc điểm:**
- Thông báo lỗi/success qua `flash`
- Bcrypt kiểm tra mật khẩu
- Lockout sau 5 lần sai

---

### 3.2 `main_bp` — Module Trang Chủ

**File:** `app/main/routes.py`

| Route | Method | Endpoint | Mô tả |
|-------|--------|----------|---------|
| `/` | GET | `main.index` | Trang chủ |
| `/dashboard` | GET | `main.dashboard` | Thống kê sau khi login |

**Đặc điểm:**
- Kiểm tra session `user_id` trước khi render dashboard
- Chỉ hiển thị khi người dùng đã đăng nhập

---

### 3.3 `account_bp` — Module Quản Lý Tài Khoản

**File:** `app/account/routes.py`

| Route | Method | Endpoint | Mô tả |
|-------|--------|----------|---------|
| `/account` | GET | `account.profile` | Thông tin tài khoản |
| `/account/change-password` | GET/POST | `account.change_password` | Đổi mật khẩu |
| `/account/change-email` | GET/POST | `account.change_email` | Đổi email |
| `/account/security` | GET | `account.security` | Bảo mật tài khoản |

**Decorators:**
```python
from functools import wraps

def require_login(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        if 'user_id' not in session:
            flash('Vui lòng đăng nhập...', 'warning')
            return redirect(url_for('auth.login'))
        return view(*args, **kwargs)
    return wrapper
```

---

### 3.4 `recover_bp` — Module Khôi Phục Mật Khẩu

**File:** `app/recover/routes.py`

| Route | Method | Endpoint | Mô tả |
|-------|--------|----------|---------|
| `/forgot-password` | GET/POST | `recover.forgot_password` | Form quên mật khẩu |
| `/reset-password/<token>` | GET/POST | `recover.reset_password` | Xác nhận và đặt lại mật khẩu |

**Flow:**
```
User → /forgot-password → → POST → Tạo token (30 phút) → Gửi email
                                        ↓
User → /reset-password/<token> → GET → Form nhập mật khẩu mới
                                     POST → Cập nhật + Xóa token
```

---

## 4. User Model Cơ Sở Dữ Liệu

**File:** `app/models.py`

| Cột | Kiểu | Mô tả |
|-----|------|---------|
| `id` | INTEGER PK | Primary key |
| `username` | VARCHAR(80) UNIQUE | Tên đăng nhập |
| `email` | VARCHAR(120) UNIQUE | Email liên kết |
| `password_hash` | VARCHAR(128) | Bcrypt hash |
| `login_attempts` | INT DEFAULT 0 | Số lần đăng nhập sai |
| `lockout_until` | DATETIME | Thời gian khóa |
| `reset_token` | VARCHAR(128) | Token reset mật khẩu |
| `reset_token_expiry` | DATETIME | Hạn dùng token |

---

## 5. Cấu Hình Bảo Mật

| Config | Value | Mục đích |
|--------|-------|----------|
| `SECRET_KEY` | `os.getenv('SECRET_KEY')` | Mã hóa session |
| `PERMANENT_SESSION_LIFETIME` | `1800` giây (30 phút) | Hết hạn phiên |
| `SESSION_COOKIE_HTTPONLY` | `True` | Chống XSS |
| `SESSION_COOKIE_SAMESITE` | `'Lax'` | Chống CSRF |
| `MAX_CONTENT_LENGTH` | `16MB` | Giới hạn upload |

---

## 6. Linh Hoạt

- Dùng **SQLite** (có thể thay bằng PostgreSQL, MySQL trong production)
- Dùng **Application Factory** để tạo nhiều môi trường
- Tự động seed admin nếu chưa có (chạy `db.create_all()`)
- Email reset chỉ in ra console (có thể tích hợp SMTP sau)
