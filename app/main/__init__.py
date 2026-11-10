from flask import Blueprint

# Khởi tạo Blueprint cho module main
main_bp = Blueprint('main', __name__, template_folder='templates')
