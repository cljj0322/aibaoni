from . import db
from datetime import datetime

class Order(db.Model):
    """订单模型"""
    __tablename__ = 'orders'
    
    id = db.Column(db.Integer, primary_key=True)
    po_no = db.Column(db.String(50), nullable=False, index=True)
    receive_date = db.Column(db.Date, nullable=True)
    finish_date = db.Column(db.Date, nullable=True)
    repair_status = db.Column(db.String(20), default='not_started')
    customer_name = db.Column(db.String(100), nullable=False)
    contact_phone = db.Column(db.String(50), nullable=True)
    email = db.Column(db.String(100), nullable=True)
    address = db.Column(db.String(200), nullable=True)
    remark = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关联关系
    valves = db.relationship('Valve', backref='order', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'po_no': self.po_no,
            'receive_date': self.receive_date.strftime('%Y-%m-%d') if self.receive_date else None,
            'finish_date': self.finish_date.strftime('%Y-%m-%d') if self.finish_date else None,
            'repair_status': self.repair_status,
            'customer_name': self.customer_name,
            'contact_phone': self.contact_phone,
            'email': self.email,
            'address': self.address,
            'remark': self.remark,
            'valve_count': len(self.valves),
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None,
            'valves': [valve.to_dict() for valve in self.valves]
        }
    
    def to_list_dict(self):
        """列表展示用的简化字典"""
        return {
            'id': self.id,
            'po_no': self.po_no,
            'receive_date': self.receive_date.strftime('%Y-%m-%d') if self.receive_date else None,
            'finish_date': self.finish_date.strftime('%Y-%m-%d') if self.finish_date else None,
            'repair_status': self.repair_status,
            'customer_name': self.customer_name,
            'contact_phone': self.contact_phone,
            'valve_count': len(self.valves)
        }


class Valve(db.Model):
    """阀门模型"""
    __tablename__ = 'valves'
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    customer_sn = db.Column(db.String(100), nullable=True)
    abn_sn = db.Column(db.String(100), nullable=True)
    part_no = db.Column(db.String(100), nullable=True)
    description = db.Column(db.String(200), nullable=True)
    model_no = db.Column(db.String(100), nullable=True)
    fault_description = db.Column(db.Text, nullable=True)
    current_step = db.Column(db.String(100), nullable=True)
    service_category = db.Column(db.String(50), default='NormalRepair')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'order_id': self.order_id,
            'customer_sn': self.customer_sn,
            'abn_sn': self.abn_sn,
            'part_no': self.part_no,
            'description': self.description,
            'model_no': self.model_no,
            'fault_description': self.fault_description,
            'current_step': self.current_step,
            'service_category': self.service_category,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None
        }


class RepairRecord(db.Model):
    """维修过程记录主表"""
    __tablename__ = 'repair_records'
    
    id = db.Column(db.Integer, primary_key=True)
    valve_id = db.Column(db.Integer, db.ForeignKey('valves.id'), nullable=False, unique=True)
    
    # 基本信息
    current_step = db.Column(db.Text, nullable=True)
    
    # 维修前准备
    prepare_operator = db.Column(db.String(100), nullable=True)
    prepare_date = db.Column(db.Date, nullable=True)
    
    # 维修步骤
    repair_step_operator = db.Column(db.String(100), nullable=True)
    repair_step_date = db.Column(db.Date, nullable=True)
    
    # 检测信息
    check_operator = db.Column(db.String(100), nullable=True)
    check_date = db.Column(db.Date, nullable=True)
    
    # 物料信息
    material_operator = db.Column(db.String(100), nullable=True)
    material_date = db.Column(db.Date, nullable=True)
    
    # 最终测试
    final_test_motion = db.Column(db.String(10), nullable=True)
    final_test_pneumatic = db.Column(db.String(10), nullable=True)
    final_test_helium = db.Column(db.String(10), nullable=True)
    final_test_operator = db.Column(db.String(100), nullable=True)
    final_test_date = db.Column(db.Date, nullable=True)
    
    # 质保信息
    product_warranty = db.Column(db.String(100), nullable=True)
    repair_engineer = db.Column(db.String(100), nullable=True)
    reviewer_1 = db.Column(db.String(100), nullable=True)
    reviewer_2 = db.Column(db.String(100), nullable=True)
    warranty_operator = db.Column(db.String(100), nullable=True)
    warranty_date = db.Column(db.Date, nullable=True)
    
    # 测试数据
    test_data_operator = db.Column(db.String(100), nullable=True)
    test_data_date = db.Column(db.Date, nullable=True)
    
    # 附件
    attachment_operator = db.Column(db.String(100), nullable=True)
    attachment_date = db.Column(db.Date, nullable=True)
    
    # 包装
    packaging_operator = db.Column(db.String(100), nullable=True)
    packaging_date = db.Column(db.Date, nullable=True)
    
    # 发货
    shipment_tracking_no = db.Column(db.String(100), nullable=True)
    shipment_operator = db.Column(db.String(100), nullable=True)
    shipment_date = db.Column(db.Date, nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关联关系
    prepare_items = db.relationship('PrepareItem', backref='repair_record', lazy=True, cascade='all, delete-orphan')
    repair_steps = db.relationship('RepairStep', backref='repair_record', lazy=True, cascade='all, delete-orphan')
    check_items = db.relationship('CheckItem', backref='repair_record', lazy=True, cascade='all, delete-orphan')
    material_items = db.relationship('MaterialItem', backref='repair_record', lazy=True, cascade='all, delete-orphan')
    test_data_items = db.relationship('TestDataItem', backref='repair_record', lazy=True, cascade='all, delete-orphan')
    attachments = db.relationship('Attachment', backref='repair_record', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'valve_id': self.valve_id,
            'current_step': self.current_step,
            'prepare_operator': self.prepare_operator,
            'prepare_date': self.prepare_date.strftime('%Y-%m-%d') if self.prepare_date else None,
            'repair_step_operator': self.repair_step_operator,
            'repair_step_date': self.repair_step_date.strftime('%Y-%m-%d') if self.repair_step_date else None,
            'check_operator': self.check_operator,
            'check_date': self.check_date.strftime('%Y-%m-%d') if self.check_date else None,
            'material_operator': self.material_operator,
            'material_date': self.material_date.strftime('%Y-%m-%d') if self.material_date else None,
            'final_test_motion': self.final_test_motion,
            'final_test_pneumatic': self.final_test_pneumatic,
            'final_test_helium': self.final_test_helium,
            'final_test_operator': self.final_test_operator,
            'final_test_date': self.final_test_date.strftime('%Y-%m-%d') if self.final_test_date else None,
            'product_warranty': self.product_warranty,
            'repair_engineer': self.repair_engineer,
            'reviewer_1': self.reviewer_1,
            'reviewer_2': self.reviewer_2,
            'warranty_operator': self.warranty_operator,
            'warranty_date': self.warranty_date.strftime('%Y-%m-%d') if self.warranty_date else None,
            'test_data_operator': self.test_data_operator,
            'test_data_date': self.test_data_date.strftime('%Y-%m-%d') if self.test_data_date else None,
            'attachment_operator': self.attachment_operator,
            'attachment_date': self.attachment_date.strftime('%Y-%m-%d') if self.attachment_date else None,
            'packaging_operator': self.packaging_operator,
            'packaging_date': self.packaging_date.strftime('%Y-%m-%d') if self.packaging_date else None,
            'shipment_tracking_no': self.shipment_tracking_no,
            'shipment_operator': self.shipment_operator,
            'shipment_date': self.shipment_date.strftime('%Y-%m-%d') if self.shipment_date else None,
            'prepare_items': [item.to_dict() for item in self.prepare_items],
            'repair_steps': [step.to_dict() for step in self.repair_steps],
            'check_items': [item.to_dict() for item in self.check_items],
            'material_items': [item.to_dict() for item in self.material_items],
            'test_data_items': [item.to_dict() for item in self.test_data_items],
            'attachments': [att.to_dict() for att in self.attachments],
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None
        }


class PrepareItem(db.Model):
    """维修前准备项"""
    __tablename__ = 'prepare_items'
    
    id = db.Column(db.Integer, primary_key=True)
    repair_record_id = db.Column(db.Integer, db.ForeignKey('repair_records.id'), nullable=False)
    item_name = db.Column(db.String(200), nullable=True)
    requirement = db.Column(db.String(200), nullable=True)
    result = db.Column(db.String(10), nullable=True)
    remark = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'item_name': self.item_name,
            'requirement': self.requirement,
            'result': self.result,
            'remark': self.remark
        }


class RepairStep(db.Model):
    """维修步骤"""
    __tablename__ = 'repair_steps'
    
    id = db.Column(db.Integer, primary_key=True)
    repair_record_id = db.Column(db.Integer, db.ForeignKey('repair_records.id'), nullable=False)
    content = db.Column(db.Text, nullable=True)
    materials = db.Column(db.String(500), nullable=True)
    result = db.Column(db.String(10), nullable=True)
    remark = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'content': self.content,
            'materials': self.materials,
            'result': self.result,
            'remark': self.remark
        }


class CheckItem(db.Model):
    """检测项"""
    __tablename__ = 'check_items'
    
    id = db.Column(db.Integer, primary_key=True)
    repair_record_id = db.Column(db.Integer, db.ForeignKey('repair_records.id'), nullable=False)
    item_no = db.Column(db.Integer, nullable=True)
    check_item = db.Column(db.String(200), nullable=True)
    result = db.Column(db.String(10), nullable=True)
    remark = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'item_no': self.item_no,
            'check_item': self.check_item,
            'result': self.result,
            'remark': self.remark
        }


class MaterialItem(db.Model):
    """物料项"""
    __tablename__ = 'material_items'
    
    id = db.Column(db.Integer, primary_key=True)
    repair_record_id = db.Column(db.Integer, db.ForeignKey('repair_records.id'), nullable=False)
    category = db.Column(db.String(200), nullable=True)
    name = db.Column(db.String(200), nullable=True)
    quantity = db.Column(db.Integer, default=1)
    remark = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'category': self.category,
            'name': self.name,
            'quantity': self.quantity,
            'remark': self.remark
        }


class TestDataItem(db.Model):
    """测试数据项"""
    __tablename__ = 'test_data_items'
    
    id = db.Column(db.Integer, primary_key=True)
    repair_record_id = db.Column(db.Integer, db.ForeignKey('repair_records.id'), nullable=False)
    item_name = db.Column(db.String(200), nullable=True)
    standard = db.Column(db.String(200), nullable=True)
    test_value = db.Column(db.String(200), nullable=True)
    result = db.Column(db.String(10), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'item_name': self.item_name,
            'standard': self.standard,
            'test_value': self.test_value,
            'result': self.result
        }


class Attachment(db.Model):
    """附件"""
    __tablename__ = 'attachments'

    id = db.Column(db.Integer, primary_key=True)
    repair_record_id = db.Column(db.Integer, db.ForeignKey('repair_records.id'), nullable=False)
    type = db.Column(db.String(50), nullable=True)
    file_name = db.Column(db.String(200), nullable=True)
    file_path = db.Column(db.String(500), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'type': self.type,
            'file_name': self.file_name,
            'file_path': self.file_path
        }


class Inventory(db.Model):
    """库存管理"""
    __tablename__ = 'inventory'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(100), nullable=False, index=True)
    name = db.Column(db.String(200), nullable=False)
    spec = db.Column(db.String(200), nullable=True)
    material = db.Column(db.String(100), nullable=True)
    material_category = db.Column(db.String(100), nullable=True)
    color = db.Column(db.String(50), nullable=True)
    warehouse = db.Column(db.String(50), default='A')
    unit = db.Column(db.String(50), nullable=True)
    origin = db.Column(db.String(100), nullable=True)
    category = db.Column(db.String(100), nullable=True)
    stock = db.Column(db.Integer, default=0)
    batch = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关联关系
    records = db.relationship('InventoryRecord', backref='inventory', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'code': self.code,
            'name': self.name,
            'spec': self.spec,
            'material': self.material,
            'material_category': self.material_category,
            'color': self.color,
            'warehouse': self.warehouse,
            'unit': self.unit,
            'origin': self.origin,
            'category': self.category,
            'stock': self.stock,
            'batch': self.batch,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None
        }


class InventoryRecord(db.Model):
    """库存操作记录（入库/出库）"""
    __tablename__ = 'inventory_records'

    id = db.Column(db.Integer, primary_key=True)
    inventory_id = db.Column(db.Integer, db.ForeignKey('inventory.id'), nullable=False)
    operation_type = db.Column(db.String(20), nullable=False)  # 'inbound' 或 'outbound'
    quantity = db.Column(db.Integer, nullable=False)
    operator = db.Column(db.String(100), nullable=True)
    remark = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'inventory_id': self.inventory_id,
            'operation_type': self.operation_type,
            'quantity': self.quantity,
            'operator': self.operator,
            'remark': self.remark,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }


class MaterialCode(db.Model):
    """物料编码管理"""
    __tablename__ = 'material_codes'

    id = db.Column(db.Integer, primary_key=True)
    material_code = db.Column(db.String(100), nullable=False, unique=True, index=True)
    material_name = db.Column(db.String(200), nullable=False)
    specification = db.Column(db.String(200), nullable=True)
    category = db.Column(db.String(100), nullable=True)
    unit = db.Column(db.String(50), nullable=True)
    brand = db.Column(db.String(100), nullable=True)
    supplier = db.Column(db.String(200), nullable=True)
    remark = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'material_code': self.material_code,
            'material_name': self.material_name,
            'specification': self.specification,
            'category': self.category,
            'unit': self.unit,
            'brand': self.brand,
            'supplier': self.supplier,
            'remark': self.remark,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None
        }


class User(db.Model):
    """用户管理"""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False, unique=True, index=True)
    chinese_name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='operator')  # admin / engineer / operator
    email = db.Column(db.String(100), nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'chinese_name': self.chinese_name,
            'role': self.role,
            'email': self.email,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None
        }


class QualityInspection(db.Model):
    """质量检查记录"""
    __tablename__ = 'quality_inspections'

    id = db.Column(db.Integer, primary_key=True)
    plan_id = db.Column(db.String(100), nullable=False)
    product_code = db.Column(db.String(100), nullable=False, index=True)
    inspect_time = db.Column(db.String(30), nullable=False)
    result = db.Column(db.String(20), nullable=False)  # pass / fail / recheck
    remark = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关联缺陷列表
    defects = db.relationship('InspectionDefect', backref='inspection', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'plan_id': self.plan_id,
            'product_code': self.product_code,
            'inspect_time': self.inspect_time,
            'result': self.result,
            'remark': self.remark,
            'defects': [d.to_dict() for d in self.defects],
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None
        }


class InspectionDefect(db.Model):
    """质量检查缺陷项"""
    __tablename__ = 'inspection_defects'

    id = db.Column(db.Integer, primary_key=True)
    inspection_id = db.Column(db.Integer, db.ForeignKey('quality_inspections.id'), nullable=False)
    type = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    quantity = db.Column(db.String(50), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'type': self.type,
            'description': self.description,
            'quantity': self.quantity
        }


class RepairWorkorder(db.Model):
    """维修工单"""
    __tablename__ = 'repair_workorders'

    id = db.Column(db.Integer, primary_key=True)
    product_code = db.Column(db.String(100), nullable=False, index=True)
    product_name = db.Column(db.String(200), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    plan_start = db.Column(db.String(20), nullable=False)
    plan_end = db.Column(db.String(20), nullable=False)
    actual_start = db.Column(db.String(20), nullable=True)
    actual_end = db.Column(db.String(20), nullable=True)
    status = db.Column(db.String(20), nullable=False, default='pending')  # pending / in_progress / completed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'product_code': self.product_code,
            'product_name': self.product_name,
            'quantity': self.quantity,
            'plan_start': self.plan_start,
            'plan_end': self.plan_end,
            'actual_start': self.actual_start,
            'actual_end': self.actual_end,
            'status': self.status,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None
        }


class EquipmentMaintenance(db.Model):
    """设备维护记录"""
    __tablename__ = 'equipment_maintenance'

    id = db.Column(db.Integer, primary_key=True)
    equipment_id = db.Column(db.String(100), nullable=False, index=True)
    equipment_name = db.Column(db.String(200), nullable=False)
    maintenance_type = db.Column(db.String(100), nullable=False)
    plan_time = db.Column(db.String(30), nullable=False)
    actual_time = db.Column(db.String(30), nullable=True)
    status = db.Column(db.String(20), nullable=False, default='pending')  # pending / in_progress / completed
    remark = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'equipment_id': self.equipment_id,
            'equipment_name': self.equipment_name,
            'maintenance_type': self.maintenance_type,
            'plan_time': self.plan_time,
            'actual_time': self.actual_time,
            'status': self.status,
            'remark': self.remark,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None
        }

