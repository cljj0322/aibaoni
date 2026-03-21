"""
质量控制 API 路由

包含：
- 质量检查记录管理 CRUD
- 维修工单管理 CRUD
"""

from flask import Blueprint, request, jsonify
from datetime import datetime
from .. import db
from ..models import QualityInspection, InspectionDefect, RepairWorkorder

quality_control_bp = Blueprint('quality_control', __name__)


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


# ========================================
# 质量检查记录 CRUD
# ========================================

@quality_control_bp.route('/quality-control/inspection', methods=['GET'])
def get_inspection_list():
    """获取质量检查记录列表

    查询参数:
    - keyword: 搜索关键词（匹配生产计划ID或产品代码）
    - result: 检查结果筛选（pass/fail/recheck/all）
    - page: 页码，默认1
    - per_page: 每页数量，默认10
    """
    try:
        keyword = request.args.get('keyword', '').strip()
        result_filter = request.args.get('result', 'all')
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)

        if per_page > 100:
            per_page = 100

        query = QualityInspection.query

        # 关键词搜索
        if keyword:
            query = query.filter(
                db.or_(
                    QualityInspection.plan_id.ilike(f'%{keyword}%'),
                    QualityInspection.product_code.ilike(f'%{keyword}%')
                )
            )

        # 结果筛选
        if result_filter and result_filter != 'all':
            query = query.filter(QualityInspection.result == result_filter)

        # 按创建时间倒序
        query = query.order_by(QualityInspection.created_at.desc())

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
        return error_response(f'获取质量检查记录列表失败: {str(e)}', 500, 500)


@quality_control_bp.route('/quality-control/inspection', methods=['POST'])
def create_inspection():
    """新增质量检查记录

    请求体:
    - plan_id: 生产计划ID（必填）
    - product_code: 产品代码（必填）
    - inspect_time: 检查时间（必填）
    - result: 检查结果（必填）
    - remark: 备注（选填）
    - defects: 缺陷列表（选填），每项包含 type、description、quantity
    """
    try:
        data = request.get_json()
        if not data:
            return error_response('请求体不能为空')

        # 必填字段校验
        required_fields = ['plan_id', 'product_code', 'inspect_time', 'result']
        for field in required_fields:
            if not data.get(field):
                return error_response(f'字段 {field} 不能为空')

        # 创建主记录
        inspection = QualityInspection(
            plan_id=data['plan_id'].strip(),
            product_code=data['product_code'].strip(),
            inspect_time=data['inspect_time'],
            result=data['result'],
            remark=data.get('remark', '')
        )
        db.session.add(inspection)
        db.session.flush()  # 获取 inspection.id

        # 创建缺陷列表
        defects_data = data.get('defects', [])
        for d in defects_data:
            if not d.get('type'):
                continue
            defect = InspectionDefect(
                inspection_id=inspection.id,
                type=d['type'].strip(),
                description=d.get('description', ''),
                quantity=str(d.get('quantity', '1'))
            )
            db.session.add(defect)

        db.session.commit()
        return success_response(inspection.to_dict(), '新增质量检查记录成功')
    except Exception as e:
        db.session.rollback()
        return error_response(f'新增质量检查记录失败: {str(e)}', 500, 500)


@quality_control_bp.route('/quality-control/inspection/<int:inspection_id>', methods=['PUT'])
def update_inspection(inspection_id):
    """更新质量检查记录

    请求体同新增，缺陷列表将全量替换
    """
    try:
        inspection = QualityInspection.query.get(inspection_id)
        if not inspection:
            return error_response('质量检查记录不存在', 404, 404)

        data = request.get_json()
        if not data:
            return error_response('请求体不能为空')

        # 更新字段
        if 'plan_id' in data:
            inspection.plan_id = data['plan_id'].strip()
        if 'product_code' in data:
            inspection.product_code = data['product_code'].strip()
        if 'inspect_time' in data:
            inspection.inspect_time = data['inspect_time']
        if 'result' in data:
            inspection.result = data['result']
        if 'remark' in data:
            inspection.remark = data.get('remark', '')

        inspection.updated_at = datetime.utcnow()

        # 全量替换缺陷列表
        if 'defects' in data:
            # 删除旧缺陷
            InspectionDefect.query.filter_by(inspection_id=inspection_id).delete()
            # 新增新缺陷
            for d in data['defects']:
                if not d.get('type'):
                    continue
                defect = InspectionDefect(
                    inspection_id=inspection.id,
                    type=d['type'].strip(),
                    description=d.get('description', ''),
                    quantity=str(d.get('quantity', '1'))
                )
                db.session.add(defect)

        db.session.commit()
        return success_response(inspection.to_dict(), '更新质量检查记录成功')
    except Exception as e:
        db.session.rollback()
        return error_response(f'更新质量检查记录失败: {str(e)}', 500, 500)


@quality_control_bp.route('/quality-control/inspection/<int:inspection_id>', methods=['DELETE'])
def delete_inspection(inspection_id):
    """删除质量检查记录（级联删除缺陷列表）"""
    try:
        inspection = QualityInspection.query.get(inspection_id)
        if not inspection:
            return error_response('质量检查记录不存在', 404, 404)

        db.session.delete(inspection)
        db.session.commit()
        return success_response(None, '删除质量检查记录成功')
    except Exception as e:
        db.session.rollback()
        return error_response(f'删除质量检查记录失败: {str(e)}', 500, 500)


@quality_control_bp.route('/quality-control/inspection/<int:inspection_id>', methods=['GET'])
def get_inspection_detail(inspection_id):
    """获取单条质量检查记录详情"""
    try:
        inspection = QualityInspection.query.get(inspection_id)
        if not inspection:
            return error_response('质量检查记录不存在', 404, 404)
        return success_response(inspection.to_dict())
    except Exception as e:
        return error_response(f'获取详情失败: {str(e)}', 500, 500)


# ========================================
# 维修工单 CRUD
# ========================================

@quality_control_bp.route('/quality-control/workorder', methods=['GET'])
def get_workorder_list():
    """获取维修工单列表

    查询参数:
    - keyword: 搜索关键词（匹配产品代码或产品名称）
    - status: 状态筛选（pending/in_progress/completed/all）
    - page: 页码，默认1
    - per_page: 每页数量，默认10
    """
    try:
        keyword = request.args.get('keyword', '').strip()
        status_filter = request.args.get('status', 'all')
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)

        if per_page > 100:
            per_page = 100

        query = RepairWorkorder.query

        # 关键词搜索
        if keyword:
            query = query.filter(
                db.or_(
                    RepairWorkorder.product_code.ilike(f'%{keyword}%'),
                    RepairWorkorder.product_name.ilike(f'%{keyword}%')
                )
            )

        # 状态筛选
        if status_filter and status_filter != 'all':
            query = query.filter(RepairWorkorder.status == status_filter)

        # 按创建时间倒序
        query = query.order_by(RepairWorkorder.created_at.desc())

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
        return error_response(f'获取维修工单列表失败: {str(e)}', 500, 500)


@quality_control_bp.route('/quality-control/workorder', methods=['POST'])
def create_workorder():
    """新增维修工单

    请求体:
    - product_code: 产品代码（必填）
    - product_name: 产品名称（必填）
    - quantity: 数量（必填）
    - plan_start: 计划开始时间（必填）
    - plan_end: 计划结束时间（必填）
    - status: 状态（必填），pending/in_progress/completed
    - actual_start: 实际开始时间（选填）
    - actual_end: 实际结束时间（选填）
    """
    try:
        data = request.get_json()
        if not data:
            return error_response('请求体不能为空')

        required_fields = ['product_code', 'product_name', 'quantity', 'plan_start', 'plan_end', 'status']
        for field in required_fields:
            if not data.get(field) and data.get(field) != 0:
                return error_response(f'字段 {field} 不能为空')

        workorder = RepairWorkorder(
            product_code=data['product_code'].strip(),
            product_name=data['product_name'].strip(),
            quantity=int(data['quantity']),
            plan_start=data['plan_start'],
            plan_end=data['plan_end'],
            actual_start=data.get('actual_start'),
            actual_end=data.get('actual_end'),
            status=data['status']
        )
        db.session.add(workorder)
        db.session.commit()
        return success_response(workorder.to_dict(), '新增维修工单成功')
    except Exception as e:
        db.session.rollback()
        return error_response(f'新增维修工单失败: {str(e)}', 500, 500)


@quality_control_bp.route('/quality-control/workorder/<int:workorder_id>', methods=['PUT'])
def update_workorder(workorder_id):
    """更新维修工单"""
    try:
        workorder = RepairWorkorder.query.get(workorder_id)
        if not workorder:
            return error_response('维修工单不存在', 404, 404)

        data = request.get_json()
        if not data:
            return error_response('请求体不能为空')

        if 'product_code' in data:
            workorder.product_code = data['product_code'].strip()
        if 'product_name' in data:
            workorder.product_name = data['product_name'].strip()
        if 'quantity' in data:
            workorder.quantity = int(data['quantity'])
        if 'plan_start' in data:
            workorder.plan_start = data['plan_start']
        if 'plan_end' in data:
            workorder.plan_end = data['plan_end']
        if 'actual_start' in data:
            workorder.actual_start = data.get('actual_start')
        if 'actual_end' in data:
            workorder.actual_end = data.get('actual_end')
        if 'status' in data:
            workorder.status = data['status']

        workorder.updated_at = datetime.utcnow()
        db.session.commit()
        return success_response(workorder.to_dict(), '更新维修工单成功')
    except Exception as e:
        db.session.rollback()
        return error_response(f'更新维修工单失败: {str(e)}', 500, 500)


@quality_control_bp.route('/quality-control/workorder/<int:workorder_id>', methods=['DELETE'])
def delete_workorder(workorder_id):
    """删除维修工单"""
    try:
        workorder = RepairWorkorder.query.get(workorder_id)
        if not workorder:
            return error_response('维修工单不存在', 404, 404)

        db.session.delete(workorder)
        db.session.commit()
        return success_response(None, '删除维修工单成功')
    except Exception as e:
        db.session.rollback()
        return error_response(f'删除维修工单失败: {str(e)}', 500, 500)
