# IMPLEMENTATION — Debugs.click

**Ngày thực thi:** 2026-11-10
**Môi trường:** Python 3.12.15, VirtualEnv `.venv`
**Packages:** Flask 3.1.3, Flask-SQLAlchemy 3.1.1, Flask-Bcrypt 1.0.1, python-dotenv 1.0.1

---

## 1. Quá Trình Làm Việc

### Bước 1 — Kiến trúc ban đầu
- Tạo `requirements.txt`, `.env.example`
- Cấu trúc: `app/`, `run.py`, `templates/`

### Bước 2 — Cài đặt dependencies
```bash
cd /home/talon/PROJECT/Web-source
source .venv/bin/activate
.venv/bin/python -m pip install Flask==3.1.3 Flask-SQLAlchemy==3.1.1 Flask-Bcrypt==1.0.1 python-dotenv==1.0.1
```

### Bước 3 — Tạo 4 Blueprints
- `auth_bp`: đăng nhập/đăng ký
- `main_bp`: trang chủ/dashboard
- `account_bp`: quản lý tài khoản (thêm mới)
- `recover_bp`: khôi phục mật khẩu (thêm mới)

### Bước 4 — Model mở rộng
- `User` model: thêm 4 cột bảo vệ
- Methods: `is_locked()`, `generate_reset_token()`, `is_reset_token_valid()`

### Bước 5 — Templates
Tạo 10 template HTML với Bootstrap 5:
- `base.html` (cấu trúc chung)
- `auth/login.html`, `auth/register.html` (đã cũ)
- `main/index.html` (dashboard)
- `account/profile.html`, `change_password.html`, `change_email.html`, `security.html`
- `forgot_password.html`, `reset_password.html`

### Bước 6 — Test & Debug

#### Bug 1: Route conflict
**Lỗi:** `AssertionError: View function mapping is overwriting an existing endpoint function: account.wrapper`
**Nguyên nhân:** Decorator `require_login` không có `functools.wraps` → wrapper trở thành endpoint name.
**Fix:** Thêm `from functools import wraps`, dùng `@wraps(view)`.

#### Bug 2: Template undefined
**Lỗi:** `jinja2.exceptions.UndefinedError: 'user' is undefined`
**Nguyên nhân:** `main/index.html` template dùng `{{ user.username }}` nhưng route truyền `username=session.get('username')`.
**Fix:** Thay `user.username` → `username`, `user.email` → link username.

#### Bug 3: Account routes 404
**Lỗi:** `404` khi truy cập `/account` sau khi login.
**Nguyên nhân:** `account_bp` registered with `url_prefix='/account'`, but routes defined with `/account` prefix → double prefix.
**Fix:** Remove `/account` prefix from route definitions.

---

## 2. Test Suite

### Kiểm tra tất cả route
| # | Route | Expected | Result |
|---|-------|----------|--------|
| 1 | `GET /` | 200 | ✅ |
| 2 | `GET /auth/login` | 200 | ✅ |
| 3 | `GET /auth/register` | 200 | ✅ |
| 4 | `POST /auth/register` | 302 | ✅ |
| 5 | `POST /auth/login` (admin) | 302 | ✅ |
| 6 | `GET /account` (after login) | 308 (redirect) | ✅ |
| 7 | `GET /auth/logout` | 302 | ✅ |
| 8 | `GET /forgot-password` | 200 | ✅ |
| 9 | `GET /reset-password/invalid` | 302 | ✅ |

### Kiểm tra bảo mật
| # | Test | Result |
|---|------|--------|
| A | Admin 5 wrong attempts → lockout | ✅ |
| B | Bcrypt hash starts with `$2b$12$` | ✅ |
| C | Password not stored as plaintext | ✅ |

---

## 3. File Tạo Mới

### Python Files (5)
| File | Mô tả |
|------|-------|
| `app/account/__init__.py` | Blueprint init |
| `app/account/routes.py` | Auth routes (profile, change pw, change email, security) |
| `app/recover/__init__.py` | Recover blueprint init |
| `app/recover/routes.py` | Forgot password, reset password |
| `app/models.py` | User model với security columns |

### HTML Files (7)
| File | Mô tả |
|------|-------|
| `app/templates/account/profile.html` | Dashboard tài khoản |
| `app/templates/account/change_password.html` | Form đổi mật khẩu |
| `app/templates/account/change_email.html` | Form đổi email |
| `app/templates/account/security.html` | Bảo mật chi tiết |
| `app/templates/forgot_password.html` | Form quên mật khẩu |
| `app/templates/reset_password.html` | Form đặt lại mật khẩu |

### MD Files (4)
| File | Mô tả |
|------|-------|
| `README.md` | Tổng quan dự án |
| `docs/ARCHITECTURE.md` | Thiết kế kiến trúc |
| `docs/PLAN.md` | Gốc requirement Bước 1-6 |
| `docs/IMPLEMENTATION.md` | Thực thi, test, debug |

---

## 4. Kiến Thức Kết Luận

- Application Factory Pattern giúp mở rộng dễ dàng
- Blueprints là cách sạch để tổ chức code theo feature
- Security nhớ vào: hashlib, session, token expiration
- Always use `functools.wraps` on decorators
- Test with Flask test client before deploy
