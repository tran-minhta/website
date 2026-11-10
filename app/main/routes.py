from flask import Blueprint, render_template, redirect, url_for, session, flash

# Khởi tạo Blueprint cho trang chính
main_bp = Blueprint('main', __name__, template_folder='../templates')


@main_bp.route('/')
def index():
    """Trang chủ của ứng dụng."""
    return render_template('main/index.html')


@main_bp.route('/dashboard')
def dashboard():
    """
    Trang Dashboard.
    Chỉ hiển thị khi người dùng đã đăng nhập (có session user_id).
    Ngược lại sẽ chuyển hướng đến trang đăng nhập.
    """
    if 'user_id' not in session:
        flash('Vui lòng đăng nhập để xem trang này.', 'warning')
        return redirect(url_for('auth.login'))

    return render_template('main/index.html', username=session.get('username'))
