# app/auth/__init__.py
from flask import Blueprint

auth_bp = Blueprint('auth', __name__)

# 必须在创建蓝图后导入路由
from app.auth import routes