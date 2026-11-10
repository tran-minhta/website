from flask import Blueprint

# Khởi tạo Blueprint cho module auth
# template_folder='templates' xác định đường dẫn tới thư mục templates bên trong auth
auth_bp = Blueprint('auth', __name__, template_folder='templates')
