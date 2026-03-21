"""
仓储管理 API 路由
"""

from flask import Blueprint, request, jsonify
from datetime import datetime
from .. import db
from ..models import Inventory, InventoryRecord, MaterialCode

warehouse_bp = Blueprint('warehouse', __name__)


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


# ========== 库存管理 ==========

@warehouse_bp.route('/warehouse/inventory', methods=['GET'])
def get_inventory_list():
    """获取库存列表

    查询参数:
    - search_type: 搜索类型，'code'(按编码) 或 'exact'(精确查询编码@批次)
    - keyword: 搜索关键词
    - page: 页码，默认1
    - per_page: 每页数量，默认10
    """
    try:
        search_type = request.args.get('search_type', 'code')
        keyword = request.args.get('keyword', '').strip()
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)

        # 限制每页最大数量
        if per_page > 100:
            per_page = 100

        # 构建查询
        query = Inventory.query

        # 根据搜索条件过滤
        if keyword:
            if search_type == 'exact':
                # 精确查询：编码@批次
                if '@' in keyword:
                    code, batch = keyword.split('@', 1)
                    query = query.filter(
                        Inventory.code == code.strip(),
                        Inventory.batch == batch.strip()
                    )
                else:
                    query = query.filter(Inventory.code == keyword)
            else:
                # 按编码模糊查询
                query = query.filter(Inventory.code.ilike(f'%{keyword}%'))

        # 按创建时间倒序
        query = query.order_by(Inventory.created_at.desc())

        # 分页
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        items = pagination.items

        return success_response({
            'items': [item.to_dict() for item in items],
            'total': pagination.total,
            'page': page,
            'per_page': per_page,
            'pages': pagination.pages
        })

    except Exception as e:
        return error_response(f'获取库存列表失败: {str(e)}', 500, 500)


@warehouse_bp.route('/warehouse/inventory', methods=['POST'])
def create_inventory():
    """新增库存"""
    try:
        data = request.get_json()

        # 验证必填字段
        if not data.get('code'):
            return error_response('编码不能为空', 400, 400)
        if not data.get('name'):
            return error_response('品目名不能为空', 400, 400)

        # 检查编码+批次是否已存在
        existing = Inventory.query.filter_by(
            code=data.get('code'),
            batch=data.get('batch', '')
        ).first()
        if existing:
            return error_response('该编码和批次的库存已存在', 400, 400)

        # 创建库存记录
        inventory = Inventory(
            code=data.get('code'),
            name=data.get('name'),
            spec=data.get('spec', ''),
            material=data.get('material', ''),
            material_category=data.get('material_category', ''),
            color=data.get('color', ''),
            warehouse=data.get('warehouse', 'A'),
            unit=data.get('unit', ''),
            origin=data.get('origin', ''),
            category=data.get('category', ''),
            stock=data.get('stock', 0),
            batch=data.get('batch', '')
        )

        db.session.add(inventory)
        db.session.commit()

        return success_response(inventory.to_dict(), '新增库存成功')

    except Exception as e:
        db.session.rollback()
        return error_response(f'新增库存失败: {str(e)}', 500, 500)


@warehouse_bp.route('/warehouse/inventory/<int:inventory_id>', methods=['PUT'])
def update_inventory(inventory_id):
    """更新库存"""
    try:
        inventory = Inventory.query.get(inventory_id)
        if not inventory:
            return error_response('库存记录不存在', 404, 404)

        data = request.get_json()

        # 更新字段
        if 'code' in data:
            inventory.code = data['code']
        if 'name' in data:
            inventory.name = data['name']
        if 'spec' in data:
            inventory.spec = data['spec']
        if 'material' in data:
            inventory.material = data['material']
        if 'material_category' in data:
            inventory.material_category = data['material_category']
        if 'color' in data:
            inventory.color = data['color']
        if 'warehouse' in data:
            inventory.warehouse = data['warehouse']
        if 'unit' in data:
            inventory.unit = data['unit']
        if 'origin' in data:
            inventory.origin = data['origin']
        if 'category' in data:
            inventory.category = data['category']
        if 'stock' in data:
            inventory.stock = data['stock']
        if 'batch' in data:
            inventory.batch = data['batch']

        inventory.updated_at = datetime.utcnow()
        db.session.commit()

        return success_response(inventory.to_dict(), '更新库存成功')

    except Exception as e:
        db.session.rollback()
        return error_response(f'更新库存失败: {str(e)}', 500, 500)


@warehouse_bp.route('/warehouse/inventory/<int:inventory_id>', methods=['DELETE'])
def delete_inventory(inventory_id):
    """删除库存"""
    try:
        inventory = Inventory.query.get(inventory_id)
        if not inventory:
            return error_response('库存记录不存在', 404, 404)

        db.session.delete(inventory)
        db.session.commit()

        return success_response(None, '删除库存成功')

    except Exception as e:
        db.session.rollback()
        return error_response(f'删除库存失败: {str(e)}', 500, 500)


@warehouse_bp.route('/warehouse/inventory/<int:inventory_id>/inbound', methods=['POST'])
def inbound_inventory(inventory_id):
    """入库操作"""
    try:
        inventory = Inventory.query.get(inventory_id)
        if not inventory:
            return error_response('库存记录不存在', 404, 404)

        data = request.get_json()
        quantity = data.get('quantity', 0)

        if not isinstance(quantity, int) or quantity <= 0:
            return error_response('入库数量必须大于0', 400, 400)

        # 更新库存数量
        inventory.stock += quantity
        inventory.updated_at = datetime.utcnow()

        # 创建入库记录
        record = InventoryRecord(
            inventory_id=inventory_id,
            operation_type='inbound',
            quantity=quantity,
            operator=data.get('operator', ''),
            remark=data.get('remark', '')
        )

        db.session.add(record)
        db.session.commit()

        return success_response({
            'inventory': inventory.to_dict(),
            'record': record.to_dict()
        }, '入库成功')

    except Exception as e:
        db.session.rollback()
        return error_response(f'入库失败: {str(e)}', 500, 500)


@warehouse_bp.route('/warehouse/inventory/<int:inventory_id>/outbound', methods=['POST'])
def outbound_inventory(inventory_id):
    """出库操作"""
    try:
        inventory = Inventory.query.get(inventory_id)
        if not inventory:
            return error_response('库存记录不存在', 404, 404)

        data = request.get_json()
        quantity = data.get('quantity', 0)

        if not isinstance(quantity, int) or quantity <= 0:
            return error_response('出库数量必须大于0', 400, 400)

        if inventory.stock < quantity:
            return error_response(f'库存不足，当前库存: {inventory.stock}', 400, 400)

        # 更新库存数量
        inventory.stock -= quantity
        inventory.updated_at = datetime.utcnow()

        # 创建出库记录
        record = InventoryRecord(
            inventory_id=inventory_id,
            operation_type='outbound',
            quantity=quantity,
            operator=data.get('operator', ''),
            remark=data.get('remark', '')
        )

        db.session.add(record)
        db.session.commit()

        return success_response({
            'inventory': inventory.to_dict(),
            'record': record.to_dict()
        }, '出库成功')

    except Exception as e:
        db.session.rollback()
        return error_response(f'出库失败: {str(e)}', 500, 500)


# ========== 物料编码管理 ==========

@warehouse_bp.route('/warehouse/materials', methods=['GET'])
def get_material_list():
    """获取物料编码列表

    查询参数:
    - keyword: 搜索关键词（物料编码或名称）
    - page: 页码，默认1
    - per_page: 每页数量，默认10
    """
    try:
        keyword = request.args.get('keyword', '').strip()
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)

        # 限制每页最大数量
        if per_page > 100:
            per_page = 100

        # 构建查询
        query = MaterialCode.query

        # 根据搜索条件过滤
        if keyword:
            query = query.filter(
                (MaterialCode.material_code.ilike(f'%{keyword}%')) |
                (MaterialCode.material_name.ilike(f'%{keyword}%'))
            )

        # 按创建时间倒序
        query = query.order_by(MaterialCode.created_at.desc())

        # 分页
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        items = pagination.items

        return success_response({
            'items': [item.to_dict() for item in items],
            'total': pagination.total,
            'page': page,
            'per_page': per_page,
            'pages': pagination.pages
        })

    except Exception as e:
        return error_response(f'获取物料编码列表失败: {str(e)}', 500, 500)


@warehouse_bp.route('/warehouse/materials', methods=['POST'])
def create_material():
    """新增物料编码"""
    try:
        data = request.get_json()

        # 验证必填字段
        if not data.get('material_code'):
            return error_response('物料编码不能为空', 400, 400)
        if not data.get('material_name'):
            return error_response('物料名称不能为空', 400, 400)

        # 检查物料编码是否已存在
        existing = MaterialCode.query.filter_by(
            material_code=data.get('material_code')
        ).first()
        if existing:
            return error_response('该物料编码已存在', 400, 400)

        # 创建物料编码记录
        material = MaterialCode(
            material_code=data.get('material_code'),
            material_name=data.get('material_name'),
            specification=data.get('specification', ''),
            category=data.get('category', ''),
            unit=data.get('unit', ''),
            brand=data.get('brand', ''),
            supplier=data.get('supplier', ''),
            remark=data.get('remark', '')
        )

        db.session.add(material)
        db.session.commit()

        return success_response(material.to_dict(), '新增物料编码成功')

    except Exception as e:
        db.session.rollback()
        return error_response(f'新增物料编码失败: {str(e)}', 500, 500)


@warehouse_bp.route('/warehouse/materials/<int:material_id>', methods=['PUT'])
def update_material(material_id):
    """更新物料编码"""
    try:
        material = MaterialCode.query.get(material_id)
        if not material:
            return error_response('物料编码不存在', 404, 404)

        data = request.get_json()

        # 如果修改了物料编码，检查是否与其他记录冲突
        if 'material_code' in data and data['material_code'] != material.material_code:
            existing = MaterialCode.query.filter_by(
                material_code=data['material_code']
            ).first()
            if existing:
                return error_response('该物料编码已存在', 400, 400)
            material.material_code = data['material_code']

        # 更新字段
        if 'material_name' in data:
            material.material_name = data['material_name']
        if 'specification' in data:
            material.specification = data['specification']
        if 'category' in data:
            material.category = data['category']
        if 'unit' in data:
            material.unit = data['unit']
        if 'brand' in data:
            material.brand = data['brand']
        if 'supplier' in data:
            material.supplier = data['supplier']
        if 'remark' in data:
            material.remark = data['remark']

        material.updated_at = datetime.utcnow()
        db.session.commit()

        return success_response(material.to_dict(), '更新物料编码成功')

    except Exception as e:
        db.session.rollback()
        return error_response(f'更新物料编码失败: {str(e)}', 500, 500)


@warehouse_bp.route('/warehouse/materials/<int:material_id>', methods=['DELETE'])
def delete_material(material_id):
    """删除物料编码"""
    try:
        material = MaterialCode.query.get(material_id)
        if not material:
            return error_response('物料编码不存在', 404, 404)

        db.session.delete(material)
        db.session.commit()

        return success_response(None, '删除物料编码成功')

    except Exception as e:
        db.session.rollback()
        return error_response(f'删除物料编码失败: {str(e)}', 500, 500)
