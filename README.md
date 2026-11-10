# debugs.click — Flask Web Application

Tích hợp **Modular Blueprint Architecture** với 4 blueprints chính:
- `auth` — Đăng nhập, đăng ký, đăng xuất
- `account` — Quản lý tài khoản (profile, đổi mật khẩu, đổi email, bảo mật)
- `recover` — Khôi phục mật khẩu (forgot, reset)
- `main` — Trang chủ, Dashboard

Để lại **sổ tay làm việc** đầy đủ: nguyên bản plan, thực thi, test, debug.

---

## 1. Cấu trúc thư mục

```
.
├── app/
│   ├── __init__.py              # App factory + cấu hình bảo mật
│   ├── models.py                # User model (có cột bảo vệ tài khoản)
│   ├── auth/                    # Blueprint đăng nhập/đăng ký
│   ├── account/                 # Blueprint quản lý tài khoản (MỚI)
│   │   ├── __init__.py
│   │   └── routes.py
│   ├── recover/                 # Blueprint khôi phục mật khẩu (MỚI)
│   │   ├── __init__.py
│   │   └── routes.py
│   ├── main/                    # Blueprint trang chính
│   └── templates/
│       ├── base.html
│       ├── auth/
│       │   ├── login.html
│       │   └── register.html
│       ├── main/
│       │   └── index.html
│       ├── account/             # Templates bảo mật
│       │   ├── profile.html
│       │   ├── change_password.html
│       │   ├── change_email.html
│       │   └── security.html
│       ├── forgot_password.html
│       └── reset_password.html
├── docs/
│   ├── ARCHITECTURE.md          # Thiết kế kiến trúc (bản gốc)
│   ├── PLAN.md                  # Gốc requirement Bước 1-6
│   ├── IMPLEMENTATION.md        # Thực thi, test, fix lỗi
│   └── BLUEPRINT_DESIGN.md      # Chi tiết 4 blueprints
├── .env.example
├── requirements.txt
└── run.py
```

---

## 2. Cấu hình

Copy `.env.example` thành `.env` và điền:

```env
SECRET_KEY=your-random-secret-key
DATABASE_URL=sqlite:///site.db
```

---

## 3. Chạy ứng dụng

```bash
cd /home/talon/PROJECT/Web-source
source .venv/bin/activate
python run.py
open http://localhost:5000
```

**Tài khoản mặc định:**
- Email: `admin@example.com`
- Mật khẩu: `admin123`

---

## 4. Danh sách Route

| Route | Endpoint | Mô tả |
|-------|----------|-------|
| `/` | `main.index` | Trang chủ |
| `/dashboard` | `main.dashboard` | Dashboard (cần đăng nhập) |
| `/auth/register` | `auth.register` | Đăng ký |
| `/auth/login` | `auth.login` | Đăng nhập |
| `/auth/logout` | `auth.logout` | Đăng xuất |
| `/account` | `account.profile` | Thông tin tài khoản |
| `/account/change-password` | `account.change_password` | Đổi mật khẩu |
| `/account/change-email` | `account.change_email` | Đổi email |
| `/account/security` | `account.security` | Bảo mật tài khoản |
| `/forgot-password` | `recover.forgot_password` | Quên mật khẩu |
| `/reset-password/<token>` | `recover.reset_password` | Đặt lại mật khẩu |

---

## 5. Security Features

- **Bcrypt**: Mật khẩu được băm an toàn
- **Lockout**: 5 lần sai → khóa 15 phút
- **Strong password**: 8+ ký tự, có chữ hoa, chữ thường, số, ký tự đặc biệt
- **Session secure**: `HTTPONLY`, `SAMESITE=Lax`
- **Token reset**: 30 phút, link chỉ dùng một lần
- **SQLite**: KV SQLite (hoặc PostgreSQL thay thế)

---

## 6. Quyền sở hữu

- Mã nguồn thuộc sở hữu **Nous Research** (Hermes Agent)
- Dự án dùng cho **debugs.click**
- Dùng cho mục đích học thuật, phát triển cá nhân
