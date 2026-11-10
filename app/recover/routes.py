from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from app import db
from app.models import User
from datetime import datetime, timedelta
import secrets

recover_bp = Blueprint('recover', __name__, template_folder='templates')


def send_password_reset_email(email, reset_url):
    """
    Gửi email khôi phục mật khẩu.
    Trong production, thay bằng SMTP (Flask-Mail hoặc SendGrid).
    Hiện tại chỉ in ra console để demo.
    """
    print(f"[EMAIL RESET] Đến: {email}")
    print(f"[EMAIL RESET] Link: {reset_url}")
    print(f"[EMAIL RESET] Gửi thành công!")
    return True


@recover_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """
    Trang quên mật khẩu:
    - Người dùng nhập email
    - Hệ thống tạo token reset và gửi email (demo)
    - Sau đó redirect về login với thông báo
    """
    if request.method == 'POST':
        email = request.form.get('email', '').strip()

        if not email:
            flash('Vui lòng nhập email!', 'danger')
            return redirect(url_for('recover.forgot_password'))

        user = User.query.filter_by(email=email).first()

        # Luôn hiển thị thành công để tránh tiềm lực scan email
        if user:
            # Tạo và lưu token
            user.generate_reset_token()
            db.session.commit()

            # Xây dựng URL reset (sử dụng domain debugs.click)
            reset_url = f"http://debugs.click/auth/reset-password/{user.reset_token}"
            send_password_reset_email(email, reset_url)

        flash('Nếu email tồn tại, chúng tôi sẽ gửi hướng dẫn khôi phục!', 'success')
        return redirect(url_for('auth.login'))

    return render_template('forgot_password.html')


@recover_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """
    Trang đặt lại mật khẩu:
    - Nhận token từ URL
    - Kiểm tra token hợp lệ và chưa hết hạn
    - Người dùng nhập mật khẩu mới
    - Cập nhật mật khẩu và xóa token
    """
    # Tìm user có token này
    user = User.query.filter_by(reset_token=token).first()

    if not user:
        flash('Token không hợp lệ hoặc đã hết hạn.', 'danger')
        return redirect(url_for('recover.forgot_password'))

    # Kiểm tra token hết hạn
    if not user.is_reset_token_valid():
        flash('Link đã hết hạn. Vui lòng yêu cầu lại.', 'danger')
        user.reset_token = None
        user.reset_token_expiry = None
        db.session.commit()
        return redirect(url_for('recover.forgot_password'))

    if request.method == 'POST':
        new_password = request.form.get('password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()

        if not new_password:
            flash('Vui lòng nhập mật khẩu mới!', 'danger')
            return redirect(url_for('recover.reset_password', token=token))

        # Import is_strong_password từ account module
        from app.account.routes import is_strong_password
        is_strong, msg = is_strong_password(new_password)
        if not is_strong:
            flash(f"Mật khẩu yếu: {msg}", 'warning')
            return redirect(url_for('recover.reset_password', token=token))

        if new_password != confirm_password:
            flash('Mật khẩu xác nhận không khớp!', 'danger')
            return redirect(url_for('recover.reset_password', token=token))

        # Cập nhật mật khẩu mới
        user.set_password(new_password)
        user.reset_token = None
        user.reset_token_expiry = None
        user.reset_login_attempts()
        db.session.commit()

        flash('Mật khẩu đã được thay đổi thành công!', 'success')
        return redirect(url_for('auth.login'))

    return render_template('reset_password.html', token=token)
