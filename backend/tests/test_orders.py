"""
客户订单系统 API 测试

运行测试:
    cd backend
    source venv/bin/activate
    python -m pytest tests/test_orders.py -v

或者:
    python -m pytest tests/test_orders.py::OrderAPITestCase::test_create_order -v
"""

import unittest
import json
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models import Order, Valve


class OrderAPITestCase(unittest.TestCase):
    """订单 API 测试用例"""
    
    def setUp(self):
        """测试前准备"""
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.client = self.app.test_client()
        
        with self.app.app_context():
            db.create_all()
    
    def tearDown(self):
        """测试后清理"""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
    
    # ========== 订单列表测试 ==========
    
    def test_get_orders_list_empty(self):
        """测试获取空订单列表"""
        response = self.client.get('/api/orders/?page=1&per_page=10')
        self.assertEqual(response.status_code, 200)
        
        result = json.loads(response.data)
        self.assertEqual(result['code'], 200)
        self.assertEqual(result['data']['items'], [])
        self.assertEqual(result['data']['total'], 0)
    
    def test_get_orders_list_with_data(self):
        """测试获取有数据的订单列表"""
        # 先创建订单
        with self.app.app_context():
            order = Order(
                po_no='PO001',
                customer_name='客户A',
                repair_status='not_started'
            )
            db.session.add(order)
            db.session.commit()
        
        response = self.client.get('/api/orders/?page=1&per_page=10')
        self.assertEqual(response.status_code, 200)
        
        result = json.loads(response.data)
        self.assertEqual(result['code'], 200)
        self.assertEqual(len(result['data']['items']), 1)
        self.assertEqual(result['data']['items'][0]['po_no'], 'PO001')
    
    def test_get_orders_list_with_search(self):
        """测试按PO号搜索订单"""
        # 创建两个订单
        with self.app.app_context():
            db.session.add_all([
                Order(po_no='ABC001', customer_name='客户A'),
                Order(po_no='XYZ002', customer_name='客户B')
            ])
            db.session.commit()
        
        # 搜索包含 ABC 的订单
        response = self.client.get('/api/orders/?search_type=po&keyword=ABC&page=1&per_page=10')
        self.assertEqual(response.status_code, 200)
        
        result = json.loads(response.data)
        self.assertEqual(len(result['data']['items']), 1)
        self.assertEqual(result['data']['items'][0]['po_no'], 'ABC001')
    
    # ========== 创建订单测试 ==========
    
    def test_create_order_success(self):
        """测试成功创建订单"""
        data = {
            'po_no': 'TEST001',
            'customer_name': '测试客户',
            'receive_date': '2026-03-20',
            'repair_status': 'not_started',
            'contact_phone': '13800138000',
            'email': 'test@example.com',
            'address': '测试地址',
            'remark': '测试备注'
        }
        
        response = self.client.post('/api/orders/',
                                   data=json.dumps(data),
                                   content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        result = json.loads(response.data)
        self.assertEqual(result['code'], 200)
        self.assertEqual(result['data']['po_no'], 'TEST001')
        self.assertEqual(result['data']['customer_name'], '测试客户')
        self.assertEqual(result['message'], '订单创建成功')
    
    def test_create_order_without_po_no(self):
        """测试创建订单缺少订单号"""
        data = {
            'customer_name': '测试客户'
        }
        
        response = self.client.post('/api/orders/',
                                   data=json.dumps(data),
                                   content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        result = json.loads(response.data)
        self.assertEqual(result['code'], 400)
        self.assertIn('订单号不能为空', result['message'])
    
    def test_create_order_without_customer_name(self):
        """测试创建订单缺少客户姓名"""
        data = {
            'po_no': 'TEST002'
        }
        
        response = self.client.post('/api/orders/',
                                   data=json.dumps(data),
                                   content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        result = json.loads(response.data)
        self.assertEqual(result['code'], 400)
        self.assertIn('客户姓名不能为空', result['message'])
    
    def test_create_order_with_invalid_date(self):
        """测试创建订单日期格式错误"""
        data = {
            'po_no': 'TEST003',
            'customer_name': '测试客户',
            'receive_date': 'invalid-date'
        }
        
        response = self.client.post('/api/orders/',
                                   data=json.dumps(data),
                                   content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        result = json.loads(response.data)
        self.assertEqual(result['code'], 400)
        self.assertIn('收货日期格式错误', result['message'])
    
    def test_create_order_with_valves(self):
        """测试创建订单同时添加阀门"""
        data = {
            'po_no': 'TEST004',
            'customer_name': '测试客户',
            'valves': [
                {
                    'customer_sn': 'SN001',
                    'abn_sn': 'ABN001',
                    'part_no': 'PART001',
                    'service_category': 'NormalRepair'
                }
            ]
        }
        
        response = self.client.post('/api/orders/',
                                   data=json.dumps(data),
                                   content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        result = json.loads(response.data)
        self.assertEqual(result['code'], 200)
        self.assertEqual(len(result['data']['valves']), 1)
        self.assertEqual(result['data']['valves'][0]['customer_sn'], 'SN001')
    
    # ========== 订单详情测试 ==========
    
    def test_get_order_detail_success(self):
        """测试获取订单详情成功"""
        # 先创建订单
        with self.app.app_context():
            order = Order(po_no='DETAIL001', customer_name='客户C')
            db.session.add(order)
            db.session.commit()
            order_id = order.id
        
        response = self.client.get(f'/api/orders/{order_id}')
        self.assertEqual(response.status_code, 200)
        
        result = json.loads(response.data)
        self.assertEqual(result['code'], 200)
        self.assertEqual(result['data']['po_no'], 'DETAIL001')
    
    def test_get_order_detail_not_found(self):
        """测试获取不存在的订单详情"""
        response = self.client.get('/api/orders/99999')
        self.assertEqual(response.status_code, 404)
        
        result = json.loads(response.data)
        self.assertEqual(result['code'], 404)
        self.assertIn('订单不存在', result['message'])
    
    # ========== 更新订单测试 ==========
    
    def test_update_order_success(self):
        """测试成功更新订单"""
        # 先创建订单
        with self.app.app_context():
            order = Order(po_no='UPDATE001', customer_name='原客户')
            db.session.add(order)
            db.session.commit()
            order_id = order.id
        
        data = {
            'customer_name': '新客户',
            'repair_status': 'in_progress'
        }
        
        response = self.client.put(f'/api/orders/{order_id}',
                                  data=json.dumps(data),
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        result = json.loads(response.data)
        self.assertEqual(result['code'], 200)
        self.assertEqual(result['data']['customer_name'], '新客户')
        self.assertEqual(result['data']['repair_status'], 'in_progress')
    
    def test_update_order_not_found(self):
        """测试更新不存在的订单"""
        data = {'customer_name': '新客户'}
        
        response = self.client.put('/api/orders/99999',
                                  data=json.dumps(data),
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 404)
        result = json.loads(response.data)
        self.assertEqual(result['code'], 404)
    
    # ========== 删除订单测试 ==========
    
    def test_delete_order_success(self):
        """测试成功删除订单"""
        # 先创建订单
        with self.app.app_context():
            order = Order(po_no='DELETE001', customer_name='客户D')
            db.session.add(order)
            db.session.commit()
            order_id = order.id
        
        response = self.client.delete(f'/api/orders/{order_id}')
        self.assertEqual(response.status_code, 200)
        
        result = json.loads(response.data)
        self.assertEqual(result['code'], 200)
        self.assertEqual(result['message'], '订单删除成功')
        
        # 验证已删除
        response = self.client.get(f'/api/orders/{order_id}')
        self.assertEqual(response.status_code, 404)
    
    def test_delete_order_not_found(self):
        """测试删除不存在的订单"""
        response = self.client.delete('/api/orders/99999')
        self.assertEqual(response.status_code, 404)
        
        result = json.loads(response.data)
        self.assertEqual(result['code'], 404)
        self.assertIn('订单不存在', result['message'])
    
    def test_delete_order_with_valves(self):
        """测试删除订单同时删除关联阀门"""
        with self.app.app_context():
            order = Order(po_no='DELETE002', customer_name='客户E')
            db.session.add(order)
            db.session.flush()
            
            valve = Valve(
                order_id=order.id,
                customer_sn='SN_DELETE',
                service_category='NormalRepair'
            )
            db.session.add(valve)
            db.session.commit()
            
            order_id = order.id
        
        response = self.client.delete(f'/api/orders/{order_id}')
        self.assertEqual(response.status_code, 200)
        
        # 验证订单已删除
        response = self.client.get(f'/api/orders/{order_id}')
        self.assertEqual(response.status_code, 404)
    
    # ========== 阀门相关测试 ==========
    
    def test_create_valve_success(self):
        """测试为订单添加阀门"""
        # 先创建订单
        with self.app.app_context():
            order = Order(po_no='VALVE001', customer_name='客户F')
            db.session.add(order)
            db.session.commit()
            order_id = order.id
        
        data = {
            'customer_sn': 'SN_VALVE',
            'abn_sn': 'ABN_VALVE',
            'part_no': 'PART_VALVE',
            'service_category': 'Warranty'
        }
        
        response = self.client.post(f'/api/orders/{order_id}/valves',
                                   data=json.dumps(data),
                                   content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        result = json.loads(response.data)
        self.assertEqual(result['code'], 200)
        self.assertEqual(result['data']['customer_sn'], 'SN_VALVE')
    
    def test_create_valve_order_not_found(self):
        """测试为不存在的订单添加阀门"""
        data = {'customer_sn': 'SN_TEST'}
        
        response = self.client.post('/api/orders/99999/valves',
                                   data=json.dumps(data),
                                   content_type='application/json')
        
        self.assertEqual(response.status_code, 404)
        result = json.loads(response.data)
        self.assertEqual(result['code'], 404)


if __name__ == '__main__':
    unittest.main()
