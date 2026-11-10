from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from app import db
from app.models import User
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()
auth_bp = Blueprint('auth', __name__, template_folder='../templates')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        # Kiểm tra thông tin đầu vào
        if not username or not email or not password:
            flash('Vui lòng điền đầy đủ thông tin!', 'danger')
            return redirect(url_for('auth.register'))

        if len(password) < 6:
            flash('Mật khẩu phải có ít nhất 6 ký tự!', 'danger')
            return redirect(url_for('auth.register'))

        if password != confirm_password:
            flash('Mật khẩu xác nhận không khớp!', 'danger')
            return redirect(url_for('auth.register'))

        # Kiểm tra xem username hoặc email đã tồn tại chưa
        existing_user = User.query.filter(
            (User.username == username) | (User.email == email)
        ).first()

        if existing_user:
            if existing_user.username == username:
                flash('Tên đăng nhập đã được sử dụng!', 'danger')
            else:
                flash('Email đã được sử dụng!', 'danger')
            return redirect(url_for('auth.register'))

        # Tạo user mới và băm mật khẩu
        new_user = User(username=username, email=email)
        new_user.set_password(password)

        db.session.add(new_user)
        db.session.commit()

        flash('Đăng ký tài khoản thành công! Hãy đăng nhập.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')

        if not email or not password:
            flash('Vui lòng nhập email và mật khẩu!', 'danger')
            return redirect(url_for('auth.login'))

        user = User.query.filter_by(email=email).first()

        if user and bcrypt.check_password_hash(user.password_hash, password):
            # Xóa session cũ và tạo session mới
            session.clear()
            session['user_id'] = user.id
            session['username'] = user.username
            session['email'] = user.email
            session.permanent = True

            flash('Đăng nhập thành công!', 'success')
            return redirect(url_for('main.dashboard'))
        else:
            flash('Email hoặc mật khẩu không đúng!', 'danger')

    return render_template('auth/login.html')


@auth_bp.route('/logout')
def logout():
    # Xóa toàn bộ dữ liệu phiên
    session.clear()
    flash('Đăng xuất thành công!', 'success')
    return redirect(url_for('auth.login'))
