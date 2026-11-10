from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from app import db
from app.models import User
from datetime import datetime, timedelta
import re
from functools import wraps

account_bp = Blueprint('account', __name__, template_folder='templates')


def is_strong_password(password):
    """
    Kiểm tra độ mạnh của mật khẩu
    Yêu cầu: >= 8 ký tự, có chữ hoa, chữ thường, số, ký tự đặc biệt
    """
    checks = {
        'length': len(password) >= 8,
        'upper': re.search(r'[A-Z]', password) is not None,
        'lower': re.search(r'[a-z]', password) is not None,
        'digit': re.search(r'[0-9]', password) is not None,
        'special': re.search(r'[!@#$%^&*(),.?":{}|<>]', password) is not None,
    }
    if not all(checks.values()):
        missing = [k for k, v in checks.items() if not v]
        return False, "Thiếu: " + ", ".join(missing)
    return True, "OK"


def require_login(view):
    """Decorator: yêu cầu đăng nhập mới được truy cập"""
    @wraps(view)
    def wrapper(*args, **kwargs):
        if 'user_id' not in session:
            flash('Vui lòng đăng nhập để tiếp tục.', 'warning')
            return redirect(url_for('auth.login'))
        return view(*args, **kwargs)
    return wrapper


@account_bp.route('/')
@require_login
def profile():
    """Trang thông tin tài khoản cá nhân"""
    user = User.query.get(session['user_id'])
    if not user:
        session.clear()
        return redirect(url_for('auth.login'))
    return render_template('account/profile.html', user=user)


@account_bp.route('/change-password', methods=['GET', 'POST'])
@require_login
def change_password():
    """Đổi mật khẩu: yêu cầu mật khẩu hiện tại + mật khẩu mới (mạnh)"""
    if request.method == 'POST':
        current_password = request.form.get('current_password', '').strip()
        new_password = request.form.get('new_password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()

        user = User.query.get(session['user_id'])
        if not user.check_password(current_password):
            flash('Mật khẩu hiện tại không đúng!', 'danger')
            return redirect(url_for('account.change_password'))

        if new_password != confirm_password:
            flash('Mật khẩu xác nhận không khớp!', 'danger')
            return redirect(url_for('account.change_password'))

        is_strong, msg = is_strong_password(new_password)
        if not is_strong:
            flash(f"Mật khẩu yếu: {msg}", 'warning')
            return redirect(url_for('account.change_password'))

        user.set_password(new_password)
        db.session.commit()
        flash('Đổi mật khẩu thành công!', 'success')
        return redirect(url_for('account.profile'))

    return render_template('account/change_password.html')


@account_bp.route('/change-email', methods=['GET', 'POST'])
@require_login
def change_email():
    """Đổi email: yêu cầu mật khẩu hiện tại + email mới"""
    if request.method == 'POST':
        new_email = request.form.get('new_email', '').strip()
        password = request.form.get('password', '').strip()

        user = User.query.get(session['user_id'])
        if not user.check_password(password):
            flash('Mật khẩu hiện tại không đúng!', 'danger')
            return redirect(url_for('account.change_email'))

        if not new_email or '@' not in new_email:
            flash('Email không hợp lệ!', 'danger')
            return redirect(url_for('account.change_email'))

        if new_email == user.email:
            flash('Email mới trùng với email hiện tại!', 'warning')
            return redirect(url_for('account.change_email'))

        existing = User.query.filter_by(email=new_email).first()
        if existing:
            flash('Email đã được sử dụng!', 'danger')
            return redirect(url_for('account.change_email'))

        user.update_email(new_email)
        user.reset_login_attempts()
        db.session.commit()
        flash('Đổi email thành công! Vui lòng đăng nhập lại.', 'success')
        session.clear()
        return redirect(url_for('auth.login'))

    return render_template('account/change_email.html')


@account_bp.route('/security')
@require_login
def security():
    """Trang bảo mật tài khoản: tổng quan trạng thái bảo vệ"""
    user = User.query.get(session['user_id'])
    if not user:
        session.clear()
        return redirect(url_for('auth.login'))

    return render_template('account/security.html', user=user)
