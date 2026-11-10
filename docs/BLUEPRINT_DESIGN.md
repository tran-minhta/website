# BLUEPRINT DESIGN — debugs.click

## 1. Sơ Đồ 4 Blueprints

```
                    ┌──────────────┐
                    │   Flask      │
                    │   App        │
                    │  Factory     │
                    └──────┬───────┘
                           │ register
                           ▼
              ┌─────────────────────────────┐
              │        Blueprint Registry    │
              └─────────────────────────────┘
                           │
        ┌────────────────┼────────────────┐
        ▼                ▼                ▼
   ┌────────────┐   ┌────────────┐   ┌────────────┐
   │   auth_bp  │   │  main_bp   │   │ account_bp │
   │ (url='/auth')│   │ (url='/')  │   │ (url='/account') │
   └────────────┘   └────────────┘   └────────────┘
        │                │                │
        ├── /auth/register  │          ├── /account
        ├── /auth/login     │          ├── /account/change-password
        └── /auth/logout    │          ├── /account/change-email
                              │          └── /account/security
                              ▼
                      ┌────────────┐
                      │ recover_bp  │
                      │ (no prefix) │
                      └────────────┘
                            │
                            ├── /forgot-password
                            └── /reset-password/<token>
```

---

## 2. Chi Tiết Blueprint

### 2.1 `auth_bp`

**Import:**
```python
from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from app import db
from app.models import User
from flask_bcrypt import Bcrypt
from datetime import datetime, timedelta
import re
```

**Routes:**
```python
@auth_bp.route('/register', methods=['GET', 'POST'])
def register(): ...

@auth_bp.route('/login', methods=['GET', 'POST'])
def login(): ...

@auth_bp.route('/logout')
def logout(): ...
```

**Keyword:** Auth, register, login, logout, password hashing, lockout

---

### 2.2 `main_bp`

**Import:**
```python
from flask import Blueprint, render_template, redirect, url_for, session, flash
from app import db
from app.models import User
```

**Routes:**
```python
@main_bp.route('/')
def index(): ...

@main_bp.route('/dashboard')
def dashboard(): ...
```

**Keyword:** Main, home, dashboard, index

---

### 2.3 `account_bp`

**Import:**
```python
from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from app import db
from app.models import User
from functools import wraps
from datetime import datetime, timedelta
import re
```

**Decorator:**
```python
def require_login(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        if 'user_id' not in session:
            flash('Vui lòng đăng nhập...', 'warning')
            return redirect(url_for('auth.login'))
        return view(*args, **kwargs)
    return wrapper
```

**Routes:**
```python
@account_bp.route('/')
@require_login
def profile(): ...

@account_bp.route('/change-password', methods=['GET', 'POST'])
@require_login
def change_password(): ...

@account_bp.route('/change-email', methods=['GET', 'POST'])
@require_login
def change_email(): ...

@account_bp.route('/security')
@require_login
def security(): ...
```

**Keyword:** Account, profile, change password, change email, security

---

### 2.4 `recover_bp`

**Import:**
```python
from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from app import db
from app.models import User
from datetime import datetime, timedelta
import secrets
```

**Routes:**
```python
@recover_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password(): ...

@recover_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token): ...
```

**Keyword:** Recover, forgot password, reset password, token, email

---

## 3. Model Methods

### User Security Methods

```python
def is_locked(self):
    """Kiểm tra tài khoản có bị khóa không"""
    if self.lockout_until is None:
        return False
    return datetime.utcnow() < self.lockout_until

def generate_reset_token(self):
    """Tạo token reset mật khẩu"""
    import secrets
    self.reset_token = secrets.token_urlsafe(32)
    self.reset_token_expiry = datetime.utcnow() + timedelta(minutes=30)

def is_reset_token_valid(self):
    """Kiểm tra token có hợp lệ không"""
    if self.reset_token is None or self.reset_token_expiry is None:
        return False
    return datetime.utcnow() < self.reset_token_expiry
```

---

## 4. Route Mapping Tóm Tắt

| Blueprint | Prefix | Routes |
|-----------|--------|--------|
| `auth_bp` | `/auth` | `/register`, `/login`, `/logout` |
| `main_bp` | `/` | `/`, `/dashboard` |
| `account_bp` | `/account` | `/`, `/change-password`, `/change-email`, `/security` |
| `recover_bp` | `None` | `/forgot-password`, `/reset-password/<token>` |

---

## 5. Template Layout

```
base.html (extends: none)
  ├── login.html (extends: base)
  ├── register.html (extends: base)
  ├── main/index.html (extends: base)
  ├── account/profile.html (extends: base)
  ├── account/change_password.html (extends: base)
  ├── account/change_email.html (extends: base)
  ├── account/security.html (extends: base)
  ├── forgot_password.html (extends: base)
  └── reset_password.html (extends: base)
```

---

## 6. Security Model

```
┌─────────────────────────────────────────┐
│           AUTH FLOW                     │
├─────────────────────────────────────────┤
│                                       │
│  Register:                              │
│  1. Validate username/email/password      │
│  2. Check strong password (8+, upper, lower, digit, special)│
│  3. Bcrypt hash → save to DB              │
│  4. Success → redirect to /auth/login       │
│                                       │
│  Login:                                 │
│  1. Query user by email                   │
│  2. Check lockout (5 failed → 15 min)      │
│  3. Check password (Bcrypt check_password)│
│  4. Success → set session, clear attempts   │
│  5. Failed → increment attempts, lock if ≥5│
│                                       │
│  Logout:                                │
│  1. session.clear() → redirect /auth/login  │
│                                       │
├─────────────────────────────────────────┤
│  RECOVERY FLOW                          │
│  1. /forgot-password → POST email         │
│  2. Generate token (30 phút)              │
│  3. Send email (demo: console output)     │
│  4. /reset-password/<token> → GET → POST   │
│  5. Validate token, update password, CLEAR token│
└─────────────────────────────────────────┘
```

---

## 7. Security Checklist

- [x] Password hashing with Bcrypt
- [x] Account lockout (5 failed → 15 min)
- [x] Strong password policy
- [x] Session cookie hardening
- [x] Reset token expiration (30 min)
- [x] No plaintext password storage
- [x] Input validation on all forms
- [ ] Email integration (SMTP) — placeholder ready
