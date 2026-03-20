"""
维修过程记录 API 测试

运行测试:
    cd backend
    source venv/bin/activate
    python -m pytest tests/test_repair_records.py -v
"""

import unittest
import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models import Order, Valve, RepairRecord, CheckItem, MaterialItem, TestDataItem


class RepairRecordAPITestCase(unittest.TestCase):
    """维修过程记录 API 测试用例"""
    
    def setUp(self):
        """测试前准备"""
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.client = self.app.test_client()
        
        with self.app.app_context():
            db.create_all()
            # 创建测试数据：订单和阀门
            order = Order(po_no='REPAIR_TEST', customer_name='测试客户')
            db.session.add(order)
            db.session.flush()
            
            valve = Valve(
                order_id=order.id,
                abn_sn='ABN_SN_TEST',
                customer_sn='CUST_SN_TEST',
                part_no='PART_TEST',
                service_category='NormalRepair'
            )
            db.session.add(valve)
            db.session.commit()
            self.valve_id = valve.id
    
    def tearDown(self):
        """测试后清理"""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
    
    # ========== 获取维修记录测试 ==========
    
    def test_get_repair_record_not_exists(self):
        """测试获取不存在的维修记录（返回阀门基本信息）"""
        response = self.client.get(f'/api/valves/{self.valve_id}/record')
        self.assertEqual(response.status_code, 200)
        
        result = json.loads(response.data)
        self.assertEqual(result['code'], 200)
        self.assertEqual(result['data']['abn_sn'], 'ABN_SN_TEST')
        self.assertEqual(result['data']['customer_sn'], 'CUST_SN_TEST')
        self.assertEqual(len(result['data']['check_items']), 3)  # 默认检测项
        self.assertEqual(len(result['data']['test_data_items']), 3)  # 默认测试数据
    
    def test_get_repair_record_valve_not_found(self):
        """测试获取不存在阀门的维修记录"""
        response = self.client.get('/api/valves/99999/record')
        self.assertEqual(response.status_code, 404)
        
        result = json.loads(response.data)
        self.assertEqual(result['code'], 404)
        self.assertIn('阀门不存在', result['message'])
    
    def test_get_repair_record_exists(self):
        """测试获取已存在的维修记录"""
        # 先创建维修记录
        with self.app.app_context():
            record = RepairRecord(
                valve_id=self.valve_id,
                current_step='维修中',
                repair_engineer='张三'
            )
            db.session.add(record)
            db.session.commit()
        
        response = self.client.get(f'/api/valves/{self.valve_id}/record')
        self.assertEqual(response.status_code, 200)
        
        result = json.loads(response.data)
        self.assertEqual(result['code'], 200)
        self.assertEqual(result['data']['current_step'], '维修中')
        self.assertEqual(result['data']['repair_engineer'], '张三')
    
    # ========== 更新维修记录测试 ==========
    
    def test_update_repair_record_create_new(self):
        """测试更新时创建新记录"""
        data = {
            'current_step': '检测完成',
            'check_operator': '李四',
            'check_date': '2026-03-20',
            'check_items': [
                {'item_no': 1, 'check_item': '运动测试', 'result': 'OK', 'remark': '正常'}
            ],
            'material_items': [
                {'category': '密封圈', 'name': 'O型圈', 'quantity': 2, 'remark': '更换'}
            ],
            'final_test_motion': 'OK',
            'repair_engineer': '王五'
        }
        
        response = self.client.put(f'/api/valves/{self.valve_id}/record',
                                  data=json.dumps(data),
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        result = json.loads(response.data)
        self.assertEqual(result['code'], 200)
        self.assertEqual(result['data']['current_step'], '检测完成')
        self.assertEqual(result['data']['check_operator'], '李四')
        self.assertEqual(len(result['data']['check_items']), 1)
        self.assertEqual(len(result['data']['material_items']), 1)
    
    def test_update_repair_record_update_existing(self):
        """测试更新已存在的记录"""
        # 先创建记录
        with self.app.app_context():
            record = RepairRecord(valve_id=self.valve_id, current_step='旧步骤')
            db.session.add(record)
            db.session.commit()
        
        data = {'current_step': '新步骤', 'repair_engineer': '赵六'}
        
        response = self.client.put(f'/api/valves/{self.valve_id}/record',
                                  data=json.dumps(data),
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        result = json.loads(response.data)
        self.assertEqual(result['code'], 200)
        self.assertEqual(result['data']['current_step'], '新步骤')
        self.assertEqual(result['data']['repair_engineer'], '赵六')
    
    def test_update_repair_record_valve_not_found(self):
        """测试更新不存在阀门的记录"""
        data = {'current_step': '测试'}
        
        response = self.client.put('/api/valves/99999/record',
                                  data=json.dumps(data),
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 404)
        result = json.loads(response.data)
        self.assertEqual(result['code'], 404)
    
    def test_update_repair_record_with_test_data(self):
        """测试更新时保存测试数据"""
        data = {
            'test_data_operator': '测试员',
            'test_data_date': '2026-03-20',
            'test_data_items': [
                {'item_name': '压力测试', 'standard': '10MPa', 'test_value': '10.5MPa', 'result': 'OK'},
                {'item_name': '泄漏测试', 'standard': '0', 'test_value': '0', 'result': 'OK'}
            ]
        }
        
        response = self.client.put(f'/api/valves/{self.valve_id}/record',
                                  data=json.dumps(data),
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        result = json.loads(response.data)
        self.assertEqual(result['code'], 200)
        self.assertEqual(result['data']['test_data_operator'], '测试员')
        self.assertEqual(len(result['data']['test_data_items']), 2)
    
    def test_update_repair_record_replace_items(self):
        """测试更新时替换子项（检测项、物料项等）"""
        # 先创建记录和子项
        with self.app.app_context():
            record = RepairRecord(valve_id=self.valve_id)
            db.session.add(record)
            db.session.flush()
            
            # 添加旧检测项
            db.session.add(CheckItem(
                repair_record_id=record.id,
                item_no=1,
                check_item='旧检测项',
                result='OK'
            ))
            db.session.commit()
        
        # 更新时替换检测项
        data = {
            'check_items': [
                {'item_no': 1, 'check_item': '新检测项1', 'result': 'OK', 'remark': ''},
                {'item_no': 2, 'check_item': '新检测项2', 'result': 'NG', 'remark': '需修复'}
            ]
        }
        
        response = self.client.put(f'/api/valves/{self.valve_id}/record',
                                  data=json.dumps(data),
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        result = json.loads(response.data)
        self.assertEqual(len(result['data']['check_items']), 2)
        self.assertEqual(result['data']['check_items'][0]['check_item'], '新检测项1')
    
    # ========== 添加检测项测试 ==========
    
    def test_add_check_item_success(self):
        """测试成功添加检测项"""
        # 先创建维修记录
        with self.app.app_context():
            record = RepairRecord(valve_id=self.valve_id)
            db.session.add(record)
            db.session.commit()
        
        data = {
            'item_no': 4,
            'check_item': '额外检测项',
            'result': 'OK',
            'remark': '正常'
        }
        
        response = self.client.post(f'/api/valves/{self.valve_id}/check-items',
                                   data=json.dumps(data),
                                   content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        result = json.loads(response.data)
        self.assertEqual(result['code'], 200)
        self.assertEqual(result['data']['check_item'], '额外检测项')
    
    def test_add_check_item_record_not_found(self):
        """测试记录不存在时添加检测项"""
        data = {'check_item': '测试项', 'result': 'OK'}
        
        response = self.client.post(f'/api/valves/{self.valve_id}/check-items',
                                   data=json.dumps(data),
                                   content_type='application/json')
        
        self.assertEqual(response.status_code, 404)
    
    # ========== 添加物料项测试 ==========
    
    def test_add_material_item_success(self):
        """测试成功添加物料项"""
        # 先创建维修记录
        with self.app.app_context():
            record = RepairRecord(valve_id=self.valve_id)
            db.session.add(record)
            db.session.commit()
        
        data = {
            'category': '弹簧',
            'name': '压缩弹簧',
            'quantity': 5,
            'remark': '备用'
        }
        
        response = self.client.post(f'/api/valves/{self.valve_id}/material-items',
                                   data=json.dumps(data),
                                   content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        result = json.loads(response.data)
        self.assertEqual(result['code'], 200)
        self.assertEqual(result['data']['name'], '压缩弹簧')
        self.assertEqual(result['data']['quantity'], 5)
    
    # ========== 质保信息测试 ==========
    
    def test_update_warranty_info(self):
        """测试更新质保信息"""
        data = {
            'product_warranty': '12个月',
            'repair_engineer': '工程师A',
            'reviewer_1': '审核人A',
            'reviewer_2': '审核人B',
            'warranty_operator': '操作员A',
            'warranty_date': '2026-03-25'
        }
        
        response = self.client.put(f'/api/valves/{self.valve_id}/record',
                                  data=json.dumps(data),
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        result = json.loads(response.data)
        self.assertEqual(result['code'], 200)
        self.assertEqual(result['data']['product_warranty'], '12个月')
        self.assertEqual(result['data']['repair_engineer'], '工程师A')
        self.assertEqual(result['data']['reviewer_1'], '审核人A')
        self.assertEqual(result['data']['warranty_date'], '2026-03-25')
    
    # ========== 最终测试测试 ==========
    
    def test_update_final_test(self):
        """测试更新最终测试结果"""
        data = {
            'final_test_motion': 'OK',
            'final_test_pneumatic': 'OK',
            'final_test_helium': 'NG',
            'final_test_operator': '测试员B',
            'final_test_date': '2026-03-22'
        }
        
        response = self.client.put(f'/api/valves/{self.valve_id}/record',
                                  data=json.dumps(data),
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        result = json.loads(response.data)
        self.assertEqual(result['code'], 200)
        self.assertEqual(result['data']['final_test_motion'], 'OK')
        self.assertEqual(result['data']['final_test_pneumatic'], 'OK')
        self.assertEqual(result['data']['final_test_helium'], 'NG')


if __name__ == '__main__':
    unittest.main()
