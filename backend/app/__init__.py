from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    
    # 配置
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///valve_repair.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JSON_AS_ASCII'] = False
    
    # 初始化扩展
    db.init_app(app)
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    
    # 注册蓝图
    from .routes.orders import orders_bp
    from .routes.repair_records import repair_bp
    from .routes.warehouse import warehouse_bp
    from .routes.quality_control import quality_control_bp
    from .routes.users import users_bp
    app.register_blueprint(orders_bp, url_prefix='/api')
    app.register_blueprint(repair_bp, url_prefix='/api')
    app.register_blueprint(warehouse_bp, url_prefix='/api')
    app.register_blueprint(quality_control_bp, url_prefix='/api')
    app.register_blueprint(users_bp, url_prefix='/api')
    
    # 创建数据库表
    with app.app_context():
        db.create_all()
    
    return app
