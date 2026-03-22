"""
用户管理 API 路由

包含用户 CRUD 操作
"""

from flask import Blueprint, request, jsonify
from datetime import datetime
from .. import db
from ..models import User

users_bp = Blueprint('users', __name__)


def success_response(data=None, message='操作成功'):
    """统一成功响应格式"""
    return jsonify({
        'code': 200,
        'message': message,
        'data': data
    })


def error_response(message='操作失败', code=400, status_code=400):
    """统一错误响应格式"""
    return jsonify({
        'code': code,
        'message': message,
        'data': None
    }), status_code


@users_bp.route('/users', methods=['GET'])
def get_user_list():
    """获取用户列表

    查询参数:
    - username: 按用户名搜索（可选）
    - page: 页码，默认1
    - per_page: 每页数量，默认10
    """
    try:
        username = request.args.get('username', '').strip()
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)

        if per_page > 100:
            per_page = 100

        query = User.query

        # 用户名搜索
        if username:
            query = query.filter(
                db.or_(
                    User.username.ilike(f'%{username}%'),
                    User.chinese_name.ilike(f'%{username}%')
                )
            )

        # 按创建时间倒序
        query = query.order_by(User.created_at.desc())

        # 分页
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)

        return success_response({
            'items': [item.to_dict() for item in pagination.items],
            'total': pagination.total,
            'page': page,
            'per_page': per_page,
            'pages': pagination.pages
        })
    except Exception as e:
        return error_response(f'获取用户列表失败: {str(e)}', 500, 500)


@users_bp.route('/users', methods=['POST'])
def create_user():
    """新增用户

    请求体:
    - username: 用户名（必填，唯一）
    - chinese_name: 中文名（必填）
    - role: 角色（必填），admin/engineer/operator
    - email: 邮箱（必填）
    - password: 密码（必填）
    """
    try:
        data = request.get_json()
        if not data:
            return error_response('请求体不能为空')

        # 必填字段校验
        required_fields = ['username', 'chinese_name', 'role', 'email', 'password']
        for field in required_fields:
            if not data.get(field):
                return error_response(f'字段 {field} 不能为空')

        # 检查用户名是否已存在
        existing_user = User.query.filter_by(username=data['username'].strip()).first()
        if existing_user:
            return error_response('用户名已存在', 409, 409)

        # 创建用户（密码明文存储，实际项目应使用哈希）
        user = User(
            username=data['username'].strip(),
            chinese_name=data['chinese_name'].strip(),
            role=data['role'],
            email=data['email'].strip(),
            password_hash=data['password']  # 实际应使用 generate_password_hash
        )
        db.session.add(user)
        db.session.commit()
        return success_response(user.to_dict(), '新增用户成功')
    except Exception as e:
        db.session.rollback()
        return error_response(f'新增用户失败: {str(e)}', 500, 500)


@users_bp.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    """更新用户信息"""
    try:
        user = User.query.get(user_id)
        if not user:
            return error_response('用户不存在', 404, 404)

        data = request.get_json()
        if not data:
            return error_response('请求体不能为空')

        # 如果修改用户名，检查是否与其他用户冲突
        if 'username' in data and data['username'] != user.username:
            existing = User.query.filter_by(username=data['username'].strip()).first()
            if existing:
                return error_response('用户名已存在', 409, 409)
            user.username = data['username'].strip()

        if 'chinese_name' in data:
            user.chinese_name = data['chinese_name'].strip()
        if 'role' in data:
            user.role = data['role']
        if 'email' in data:
            user.email = data['email'].strip()
        if 'password' in data and data['password']:
            user.password_hash = data['password']  # 实际应使用 generate_password_hash

        user.updated_at = datetime.utcnow()
        db.session.commit()
        return success_response(user.to_dict(), '更新用户成功')
    except Exception as e:
        db.session.rollback()
        return error_response(f'更新用户失败: {str(e)}', 500, 500)


@users_bp.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    """删除用户"""
    try:
        user = User.query.get(user_id)
        if not user:
            return error_response('用户不存在', 404, 404)

        db.session.delete(user)
        db.session.commit()
        return success_response(None, '删除用户成功')
    except Exception as e:
        db.session.rollback()
        return error_response(f'删除用户失败: {str(e)}', 500, 500)
