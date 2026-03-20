"""
维修过程记录 API 路由
"""

from flask import Blueprint, request, jsonify
from datetime import datetime
from .. import db
from ..models import Valve, RepairRecord, PrepareItem, RepairStep, CheckItem, MaterialItem, TestDataItem, Attachment

repair_bp = Blueprint('repair', __name__)


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


@repair_bp.route('/valves/search', methods=['GET'])
def search_valve_by_sn():
    """通过SN查询阀门

    查询参数:
    - sn: 艾宝尼SN或客户SN
    """
    try:
        sn = request.args.get('sn', '').strip()
        if not sn:
            return error_response('SN不能为空', 400, 400)

        # 通过艾宝尼SN或客户SN查询阀门
        valve = Valve.query.filter(
            (Valve.abn_sn == sn) | (Valve.customer_sn == sn)
        ).first()

        if not valve:
            return error_response('未找到该SN对应的阀门', 404, 404)

        # 获取订单号
        po_no = valve.order.po_no if valve.order else None

        return success_response({
            'id': valve.id,
            'order_id': valve.order_id,
            'po_no': po_no,
            'abn_sn': valve.abn_sn,
            'customer_sn': valve.customer_sn,
            'part_no': valve.part_no,
            'description': valve.description,
            'model_no': valve.model_no,
            'fault_description': valve.fault_description,
            'service_category': valve.service_category,
            'current_step': valve.current_step
        })

    except Exception as e:
        return error_response(f'查询阀门失败: {str(e)}', 500, 500)


@repair_bp.route('/valves/<int:valve_id>/record', methods=['GET'])
def get_repair_record(valve_id):
    """获取阀门维修记录
    
    如果记录不存在，返回阀门的基本信息
    """
    try:
        # 检查阀门是否存在
        valve = Valve.query.get(valve_id)
        if not valve:
            return error_response('阀门不存在', 404, 404)
        
        # 获取或创建维修记录
        record = RepairRecord.query.filter_by(valve_id=valve_id).first()
        
        if not record:
            # 返回阀门基本信息，前端可以基于此创建新记录
            return success_response({
                'valve_id': valve_id,
                'abn_sn': valve.abn_sn,
                'customer_sn': valve.customer_sn,
                'po_no': valve.order.po_no if valve.order else None,
                'part_no': valve.part_no,
                'description': valve.description,
                'model_no': valve.model_no,
                'fault_description': valve.fault_description,
                'service_category': valve.service_category,
                'current_step': valve.current_step,
                'prepare_items': [],
                'repair_steps': [],
                'check_items': [
                    {'item_no': 1, 'check_item': '运动测试', 'result': '', 'remark': ''},
                    {'item_no': 2, 'check_item': '气动泄漏', 'result': '', 'remark': ''},
                    {'item_no': 3, 'check_item': '氦检', 'result': '', 'remark': ''}
                ],
                'material_items': [],
                'test_data_items': [
                    {'item_name': '空气压降(60sec)', 'standard': '', 'test_value': '', 'result': ''},
                    {'item_name': 'Internal Leak Test', 'standard': '', 'test_value': '', 'result': ''},
                    {'item_name': 'External Leak Test', 'standard': '', 'test_value': '', 'result': ''}
                ],
                'attachments': []
            })
        
        # 返回完整记录
        data = record.to_dict()
        # 添加阀门信息
        data['abn_sn'] = valve.abn_sn
        data['customer_sn'] = valve.customer_sn
        data['po_no'] = valve.order.po_no if valve.order else None
        data['part_no'] = valve.part_no
        data['description'] = valve.description
        data['model_no'] = valve.model_no
        data['fault_description'] = valve.fault_description
        data['service_category'] = valve.service_category
        
        return success_response(data)
        
    except Exception as e:
        return error_response(f'获取维修记录失败: {str(e)}', 500, 500)


@repair_bp.route('/valves/<int:valve_id>/record', methods=['PUT'])
def update_repair_record(valve_id):
    """更新阀门维修记录
    
    如果记录不存在则创建，存在则更新
    """
    try:
        # 检查阀门是否存在
        valve = Valve.query.get(valve_id)
        if not valve:
            return error_response('阀门不存在', 404, 404)
        
        data = request.get_json()
        
        # 获取或创建记录
        record = RepairRecord.query.filter_by(valve_id=valve_id).first()
        
        if not record:
            record = RepairRecord(valve_id=valve_id)
            db.session.add(record)
            db.session.flush()
        
        # 更新基本信息
        if 'current_step' in data:
            record.current_step = data['current_step']
        
        # 更新维修前准备信息
        if 'prepare_operator' in data:
            record.prepare_operator = data['prepare_operator']
        if 'prepare_date' in data:
            record.prepare_date = parse_date(data['prepare_date'])
        
        # 更新维修步骤信息
        if 'repair_step_operator' in data:
            record.repair_step_operator = data['repair_step_operator']
        if 'repair_step_date' in data:
            record.repair_step_date = parse_date(data['repair_step_date'])
        
        # 更新检测信息
        if 'check_operator' in data:
            record.check_operator = data['check_operator']
        if 'check_date' in data:
            record.check_date = parse_date(data['check_date'])
        
        # 更新物料信息
        if 'material_operator' in data:
            record.material_operator = data['material_operator']
        if 'material_date' in data:
            record.material_date = parse_date(data['material_date'])
        
        # 更新最终测试
        if 'final_test_motion' in data:
            record.final_test_motion = data['final_test_motion']
        if 'final_test_pneumatic' in data:
            record.final_test_pneumatic = data['final_test_pneumatic']
        if 'final_test_helium' in data:
            record.final_test_helium = data['final_test_helium']
        if 'final_test_operator' in data:
            record.final_test_operator = data['final_test_operator']
        if 'final_test_date' in data:
            record.final_test_date = parse_date(data['final_test_date'])
        
        # 更新质保信息
        if 'product_warranty' in data:
            record.product_warranty = data['product_warranty']
        if 'repair_engineer' in data:
            record.repair_engineer = data['repair_engineer']
        if 'reviewer_1' in data:
            record.reviewer_1 = data['reviewer_1']
        if 'reviewer_2' in data:
            record.reviewer_2 = data['reviewer_2']
        if 'warranty_operator' in data:
            record.warranty_operator = data['warranty_operator']
        if 'warranty_date' in data:
            record.warranty_date = parse_date(data['warranty_date'])
        
        # 更新测试数据
        if 'test_data_operator' in data:
            record.test_data_operator = data['test_data_operator']
        if 'test_data_date' in data:
            record.test_data_date = parse_date(data['test_data_date'])
        
        # 更新附件信息
        if 'attachment_operator' in data:
            record.attachment_operator = data['attachment_operator']
        if 'attachment_date' in data:
            record.attachment_date = parse_date(data['attachment_date'])
        
        # 更新包装信息
        if 'packaging_operator' in data:
            record.packaging_operator = data['packaging_operator']
        if 'packaging_date' in data:
            record.packaging_date = parse_date(data['packaging_date'])
        
        # 更新发货信息
        if 'shipment_tracking_no' in data:
            record.shipment_tracking_no = data['shipment_tracking_no']
        if 'shipment_operator' in data:
            record.shipment_operator = data['shipment_operator']
        if 'shipment_date' in data:
            record.shipment_date = parse_date(data['shipment_date'])
        
        # 更新维修前准备项
        if 'prepare_items' in data and isinstance(data['prepare_items'], list):
            PrepareItem.query.filter_by(repair_record_id=record.id).delete()
            for item_data in data['prepare_items']:
                item = PrepareItem(
                    repair_record_id=record.id,
                    item_name=item_data.get('item_name'),
                    requirement=item_data.get('requirement'),
                    result=item_data.get('result'),
                    remark=item_data.get('remark')
                )
                db.session.add(item)
        
        # 更新维修步骤
        if 'repair_steps' in data and isinstance(data['repair_steps'], list):
            RepairStep.query.filter_by(repair_record_id=record.id).delete()
            for step_data in data['repair_steps']:
                step = RepairStep(
                    repair_record_id=record.id,
                    content=step_data.get('content'),
                    materials=step_data.get('materials'),
                    result=step_data.get('result'),
                    remark=step_data.get('remark')
                )
                db.session.add(step)
        
        # 更新检测项
        if 'check_items' in data and isinstance(data['check_items'], list):
            # 删除旧记录
            CheckItem.query.filter_by(repair_record_id=record.id).delete()
            # 添加新记录
            for item_data in data['check_items']:
                item = CheckItem(
                    repair_record_id=record.id,
                    item_no=item_data.get('item_no'),
                    check_item=item_data.get('check_item'),
                    result=item_data.get('result'),
                    remark=item_data.get('remark')
                )
                db.session.add(item)
        
        # 更新物料项
        if 'material_items' in data and isinstance(data['material_items'], list):
            MaterialItem.query.filter_by(repair_record_id=record.id).delete()
            for item_data in data['material_items']:
                item = MaterialItem(
                    repair_record_id=record.id,
                    category=item_data.get('category'),
                    name=item_data.get('name'),
                    quantity=item_data.get('quantity', 1),
                    remark=item_data.get('remark')
                )
                db.session.add(item)
        
        # 更新测试数据项
        if 'test_data_items' in data and isinstance(data['test_data_items'], list):
            TestDataItem.query.filter_by(repair_record_id=record.id).delete()
            for item_data in data['test_data_items']:
                item = TestDataItem(
                    repair_record_id=record.id,
                    item_name=item_data.get('item_name'),
                    standard=item_data.get('standard'),
                    test_value=item_data.get('test_value'),
                    result=item_data.get('result')
                )
                db.session.add(item)
        
        db.session.commit()
        
        return success_response(record.to_dict(), '保存成功')
        
    except Exception as e:
        db.session.rollback()
        return error_response(f'保存维修记录失败: {str(e)}', 500, 500)


@repair_bp.route('/valves/<int:valve_id>/check-items', methods=['POST'])
def add_check_item(valve_id):
    """添加检测项"""
    try:
        record = RepairRecord.query.filter_by(valve_id=valve_id).first()
        if not record:
            return error_response('维修记录不存在', 404, 404)
        
        data = request.get_json()
        
        item = CheckItem(
            repair_record_id=record.id,
            item_no=data.get('item_no'),
            check_item=data.get('check_item'),
            result=data.get('result'),
            remark=data.get('remark')
        )
        
        db.session.add(item)
        db.session.commit()
        
        return success_response(item.to_dict(), '添加成功')
        
    except Exception as e:
        db.session.rollback()
        return error_response(f'添加检测项失败: {str(e)}', 500, 500)


@repair_bp.route('/valves/<int:valve_id>/material-items', methods=['POST'])
def add_material_item(valve_id):
    """添加物料项"""
    try:
        record = RepairRecord.query.filter_by(valve_id=valve_id).first()
        if not record:
            return error_response('维修记录不存在', 404, 404)
        
        data = request.get_json()
        
        item = MaterialItem(
            repair_record_id=record.id,
            category=data.get('category'),
            name=data.get('name'),
            quantity=data.get('quantity', 1),
            remark=data.get('remark')
        )
        
        db.session.add(item)
        db.session.commit()
        
        return success_response(item.to_dict(), '添加成功')
        
    except Exception as e:
        db.session.rollback()
        return error_response(f'添加物料项失败: {str(e)}', 500, 500)


@repair_bp.route('/valves/<int:valve_id>/attachments', methods=['POST'])
def upload_attachment(valve_id):
    """上传附件
    
    简化实现：仅保存文件信息，实际文件存储需要额外配置
    """
    try:
        record = RepairRecord.query.filter_by(valve_id=valve_id).first()
        if not record:
            return error_response('维修记录不存在', 404, 404)
        
        # 获取上传的文件
        file = request.files.get('file')
        file_type = request.form.get('type', 'product')
        
        if not file:
            return error_response('没有上传文件', 400, 400)
        
        # 简化处理：仅保存文件信息
        # 实际项目中应该保存文件到存储服务
        attachment = Attachment(
            repair_record_id=record.id,
            type=file_type,
            file_name=file.filename,
            file_path=f'/uploads/{valve_id}/{file.filename}'  # 模拟路径
        )
        
        db.session.add(attachment)
        db.session.commit()
        
        return success_response(attachment.to_dict(), '上传成功')
        
    except Exception as e:
        db.session.rollback()
        return error_response(f'上传附件失败: {str(e)}', 500, 500)


@repair_bp.route('/attachments/<int:attachment_id>', methods=['DELETE'])
def delete_attachment(attachment_id):
    """删除附件"""
    try:
        attachment = Attachment.query.get(attachment_id)
        if not attachment:
            return error_response('附件不存在', 404, 404)
        
        db.session.delete(attachment)
        db.session.commit()
        
        return success_response(None, '删除成功')
        
    except Exception as e:
        db.session.rollback()
        return error_response(f'删除附件失败: {str(e)}', 500, 500)


def parse_date(date_str):
    """解析日期字符串"""
    if not date_str:
        return None
    try:
        return datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return None
