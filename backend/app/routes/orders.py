from flask import Blueprint, request, jsonify
from datetime import datetime
from .. import db
from ..models import Order, Valve

orders_bp = Blueprint('orders', __name__)


def success_response(data=None, message='操作成功'):
    """统一成功响应格式"""
    response = {
        'code': 200,
        'message': message,
        'data': data
    }
    return jsonify(response)


def error_response(message='操作失败', code=400, status_code=400):
    """统一错误响应格式"""
    response = {
        'code': code,
        'message': message,
        'data': None
    }
    return jsonify(response), status_code


@orders_bp.route('/orders/', methods=['GET'])
def get_orders():
    """获取订单列表
    
    查询参数:
    - search_type: 搜索类型 ('po' 或 'time')
    - keyword: 关键词（PO号搜索时使用）
    - start_date: 开始日期
    - end_date: 结束日期
    - page: 页码（默认1）
    - per_page: 每页数量（默认10）
    """
    try:
        # 获取查询参数
        search_type = request.args.get('search_type', 'po')
        keyword = request.args.get('keyword', '')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        # 构建查询
        query = Order.query
        
        # 根据搜索类型过滤
        if search_type == 'po' and keyword:
            query = query.filter(Order.po_no.contains(keyword))
        elif search_type == 'time':
            if start_date:
                try:
                    start = datetime.strptime(start_date, '%Y-%m-%d').date()
                    query = query.filter(Order.receive_date >= start)
                except ValueError:
                    pass
            if end_date:
                try:
                    end = datetime.strptime(end_date, '%Y-%m-%d').date()
                    query = query.filter(Order.receive_date <= end)
                except ValueError:
                    pass
        
        # 按创建时间倒序排列
        query = query.order_by(Order.created_at.desc())
        
        # 分页
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        orders = pagination.items
        
        # 构建响应数据
        items = [order.to_list_dict() for order in orders]
        total = pagination.total
        
        return success_response({
            'items': items,
            'total': total,
            'page': page,
            'per_page': per_page,
            'pages': pagination.pages
        })
        
    except Exception as e:
        return error_response(f'获取订单列表失败: {str(e)}', 500, 500)


@orders_bp.route('/orders/<int:id>', methods=['GET'])
def get_order(id):
    """获取单个订单详情"""
    try:
        order = Order.query.get(id)
        if not order:
            return error_response('订单不存在', 404, 404)
        
        return success_response(order.to_dict())
        
    except Exception as e:
        return error_response(f'获取订单详情失败: {str(e)}', 500, 500)


@orders_bp.route('/orders/', methods=['POST'])
def create_order():
    """创建新订单
    
    请求体参数:
    - po_no: 订单号（必填）
    - receive_date: 收货日期
    - finish_date: 完成日期
    - repair_status: 维修状态
    - customer_name: 客户姓名（必填）
    - contact_phone: 联系电话
    - email: 电子邮箱
    - address: 联系地址
    - remark: 备注
    - valves: 阀门列表（可选）
    """
    try:
        data = request.get_json()
        
        # 验证必填字段
        if not data.get('po_no'):
            return error_response('订单号不能为空', 400, 400)
        if not data.get('customer_name'):
            return error_response('客户姓名不能为空', 400, 400)
        
        # 解析日期
        receive_date = None
        finish_date = None
        
        if data.get('receive_date'):
            try:
                receive_date = datetime.strptime(data['receive_date'], '%Y-%m-%d').date()
            except ValueError:
                return error_response('收货日期格式错误', 400, 400)
        
        if data.get('finish_date'):
            try:
                finish_date = datetime.strptime(data['finish_date'], '%Y-%m-%d').date()
            except ValueError:
                return error_response('完成日期格式错误', 400, 400)
        
        # 创建订单
        order = Order(
            po_no=data['po_no'],
            receive_date=receive_date,
            finish_date=finish_date,
            repair_status=data.get('repair_status', 'not_started'),
            customer_name=data['customer_name'],
            contact_phone=data.get('contact_phone'),
            email=data.get('email'),
            address=data.get('address'),
            remark=data.get('remark')
        )
        
        db.session.add(order)
        db.session.flush()  # 获取订单ID
        
        # 处理阀门列表（如果提供）
        valves_data = data.get('valves', [])
        if valves_data and isinstance(valves_data, list):
            for valve_data in valves_data:
                valve = Valve(
                    order_id=order.id,
                    customer_sn=valve_data.get('customer_sn'),
                    abn_sn=valve_data.get('abn_sn'),
                    part_no=valve_data.get('part_no'),
                    description=valve_data.get('description'),
                    model_no=valve_data.get('model_no'),
                    fault_description=valve_data.get('fault_description'),
                    current_step=valve_data.get('current_step'),
                    service_category=valve_data.get('service_category', 'NormalRepair')
                )
                db.session.add(valve)
        
        db.session.commit()
        
        return success_response(order.to_dict(), '订单创建成功')
        
    except Exception as e:
        db.session.rollback()
        return error_response(f'创建订单失败: {str(e)}', 500, 500)


@orders_bp.route('/orders/<int:id>', methods=['PUT'])
def update_order(id):
    """更新订单"""
    try:
        order = Order.query.get(id)
        if not order:
            return error_response('订单不存在', 404, 404)
        
        data = request.get_json()
        
        # 更新字段
        if 'po_no' in data:
            order.po_no = data['po_no']
        if 'receive_date' in data:
            try:
                order.receive_date = datetime.strptime(data['receive_date'], '%Y-%m-%d').date() if data['receive_date'] else None
            except ValueError:
                return error_response('收货日期格式错误', 400, 400)
        if 'finish_date' in data:
            try:
                order.finish_date = datetime.strptime(data['finish_date'], '%Y-%m-%d').date() if data['finish_date'] else None
            except ValueError:
                return error_response('完成日期格式错误', 400, 400)
        if 'repair_status' in data:
            order.repair_status = data['repair_status']
        if 'customer_name' in data:
            order.customer_name = data['customer_name']
        if 'contact_phone' in data:
            order.contact_phone = data['contact_phone']
        if 'email' in data:
            order.email = data['email']
        if 'address' in data:
            order.address = data['address']
        if 'remark' in data:
            order.remark = data['remark']
        
        order.updated_at = datetime.utcnow()
        db.session.commit()
        
        return success_response(order.to_dict(), '订单更新成功')
        
    except Exception as e:
        db.session.rollback()
        return error_response(f'更新订单失败: {str(e)}', 500, 500)


@orders_bp.route('/orders/<int:id>', methods=['DELETE'])
def delete_order(id):
    """删除订单"""
    try:
        order = Order.query.get(id)
        if not order:
            return error_response('订单不存在', 404, 404)
        
        db.session.delete(order)
        db.session.commit()
        
        return success_response(None, '订单删除成功')
        
    except Exception as e:
        db.session.rollback()
        return error_response(f'删除订单失败: {str(e)}', 500, 500)


# ========== 阀门相关接口 ==========

@orders_bp.route('/orders/<int:order_id>/valves', methods=['POST'])
def create_valve(order_id):
    """为订单添加阀门"""
    try:
        order = Order.query.get(order_id)
        if not order:
            return error_response('订单不存在', 404, 404)
        
        data = request.get_json()
        
        valve = Valve(
            order_id=order_id,
            customer_sn=data.get('customer_sn'),
            abn_sn=data.get('abn_sn'),
            part_no=data.get('part_no'),
            description=data.get('description'),
            model_no=data.get('model_no'),
            fault_description=data.get('fault_description'),
            current_step=data.get('current_step'),
            service_category=data.get('service_category', 'NormalRepair')
        )
        
        db.session.add(valve)
        db.session.commit()
        
        return success_response(valve.to_dict(), '阀门添加成功')
        
    except Exception as e:
        db.session.rollback()
        return error_response(f'添加阀门失败: {str(e)}', 500, 500)


@orders_bp.route('/orders/<int:order_id>/valves/<int:valve_id>', methods=['PUT'])
def update_valve(order_id, valve_id):
    """更新阀门信息"""
    try:
        order = Order.query.get(order_id)
        if not order:
            return error_response('订单不存在', 404, 404)
        
        valve = Valve.query.filter_by(id=valve_id, order_id=order_id).first()
        if not valve:
            return error_response('阀门不存在', 404, 404)
        
        data = request.get_json()
        
        if 'customer_sn' in data:
            valve.customer_sn = data['customer_sn']
        if 'abn_sn' in data:
            valve.abn_sn = data['abn_sn']
        if 'part_no' in data:
            valve.part_no = data['part_no']
        if 'description' in data:
            valve.description = data['description']
        if 'model_no' in data:
            valve.model_no = data['model_no']
        if 'fault_description' in data:
            valve.fault_description = data['fault_description']
        if 'current_step' in data:
            valve.current_step = data['current_step']
        if 'service_category' in data:
            valve.service_category = data['service_category']
        
        valve.updated_at = datetime.utcnow()
        db.session.commit()
        
        return success_response(valve.to_dict(), '阀门更新成功')
        
    except Exception as e:
        db.session.rollback()
        return error_response(f'更新阀门失败: {str(e)}', 500, 500)


@orders_bp.route('/orders/<int:order_id>/valves/<int:valve_id>', methods=['DELETE'])
def delete_valve(order_id, valve_id):
    """删除阀门"""
    try:
        order = Order.query.get(order_id)
        if not order:
            return error_response('订单不存在', 404, 404)
        
        valve = Valve.query.filter_by(id=valve_id, order_id=order_id).first()
        if not valve:
            return error_response('阀门不存在', 404, 404)
        
        db.session.delete(valve)
        db.session.commit()
        
        return success_response(None, '阀门删除成功')
        
    except Exception as e:
        db.session.rollback()
        return error_response(f'删除阀门失败: {str(e)}', 500, 500)
