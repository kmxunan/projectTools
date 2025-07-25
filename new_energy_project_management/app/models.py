from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import db, login

class User(UserMixin, db.Model):
    """用户模型，用于身份认证和权限控制。"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    role = db.Column(db.String(20), default='普通员工') # 角色: 管理员, 项目经理, 财务/管理层, 普通员工

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

class Project(db.Model):
    """项目模型，用于存储项目的核心信息。"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), index=True, unique=True)
    project_type = db.Column(db.String(64)) # e.g., '集中式光伏', '陆上风电'
    capacity_mw = db.Column(db.Float) # 装机容量 (MW)
    current_stage = db.Column(db.String(64), default='机会挖掘') # 当前生命周期阶段
    manager_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    # 地理信息字段
    longitude = db.Column(db.Float) # 经度
    latitude = db.Column(db.Float) # 纬度
    address = db.Column(db.String(500)) # 详细地址
    province = db.Column(db.String(50)) # 省份
    city = db.Column(db.String(50)) # 城市
    district = db.Column(db.String(50)) # 区县
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    manager = db.relationship('User', backref='projects')

    def __repr__(self):
        return f'<Project {self.name}>'

class CostModel(db.Model):
    """标准化造价模型参数 - 严格按照计算模型技术文档V2.0实现。"""
    id = db.Column(db.Integer, primary_key=True)
    project_type = db.Column(db.String(64), unique=True) # '集中式光伏' or '陆上风电'
    cost_items = db.Column(db.JSON) # 存储成本构成总览，例如：{'设备费': 2.0, '工程费': 1.5, ...}
    cost_details = db.Column(db.JSON) # 存储详细成本构成，例如：{'设备费': {'光伏组件': 1.10, '逆变器': 0.15, ...}, ...}
    unit_cost_label = db.Column(db.String(20)) # '元/W' or '万元/MW'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def calculate_total_cost(self, capacity_mw):
        """
        根据装机容量计算总造价 - 严格按照技术文档Model B实现
        
        Args:
            capacity_mw (float): 项目装机容量，单位为兆瓦(MW)
            
        Returns:
            float: 项目工程总量P_total，单位为万元
        """
        from decimal import Decimal, ROUND_HALF_UP
        
        # 使用高精度计算避免浮点数误差
        capacity_mw = Decimal(str(capacity_mw))
        
        # 计算单位造价总和
        unit_cost_total = sum(Decimal(str(cost)) for cost in self.cost_items.values())
        
        if self.unit_cost_label == '元/W':
            # 集中式光伏电站成本模型
            # P_total_PV (万元) = (Capacity_PV * 1,000,000 * Unit_Cost_PV) / 10,000
            p_total = (capacity_mw * Decimal('1000000') * unit_cost_total) / Decimal('10000')
        elif self.unit_cost_label == '万元/MW':
            # 陆上风电项目成本模型
            # P_total_Wind (万元) = Capacity_Wind * Unit_Cost_Wind
            p_total = capacity_mw * unit_cost_total
        else:
            return 0.0
        
        # 返回浮点数结果，保留2位小数
        return float(p_total.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))
    
    def get_cost_breakdown(self, capacity_mw):
        """
        获取详细的成本构成分解
        
        Args:
            capacity_mw (float): 项目装机容量，单位为兆瓦(MW)
            
        Returns:
            dict: 详细的成本构成，包括各项成本的具体金额
        """
        from decimal import Decimal, ROUND_HALF_UP
        
        capacity_mw = Decimal(str(capacity_mw))
        breakdown = {}
        
        for category, cost_value in self.cost_items.items():
            cost_value = Decimal(str(cost_value))
            
            if self.unit_cost_label == '元/W':
                # 光伏项目：元/W -> 万元
                category_cost = (capacity_mw * Decimal('1000000') * cost_value) / Decimal('10000')
            elif self.unit_cost_label == '万元/MW':
                # 风电项目：万元/MW -> 万元
                category_cost = capacity_mw * cost_value
            else:
                category_cost = Decimal('0')
            
            breakdown[category] = float(category_cost.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))
        
        return breakdown

    def __repr__(self):
        return f'<CostModel {self.project_type}>'

class ProjectCostDetail(db.Model):
    """项目独立成本明细模型，用于存储每个项目的自定义成本构成。"""
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    cost_category = db.Column(db.String(64), nullable=False)  # 成本类别，如'设备费'、'工程费'等
    cost_item = db.Column(db.String(128), nullable=False)  # 具体成本项，如'光伏组件'、'逆变器'等
    unit_cost = db.Column(db.Float, nullable=False)  # 单位成本
    unit_label = db.Column(db.String(20), nullable=False)  # 单位标签，如'元/W'、'万元/MW'
    total_cost = db.Column(db.Float)  # 该项的总成本（万元）
    description = db.Column(db.Text)  # 成本项描述
    is_custom = db.Column(db.Boolean, default=True)  # 是否为项目自定义成本项
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    project = db.relationship('Project', backref='cost_details')
    
    def calculate_total_cost(self, capacity_mw):
        """
        根据装机容量计算该成本项的总成本
        
        Args:
            capacity_mw (float): 项目装机容量，单位为兆瓦(MW)
            
        Returns:
            float: 该成本项的总成本，单位为万元
        """
        from decimal import Decimal, ROUND_HALF_UP
        
        capacity_mw = Decimal(str(capacity_mw))
        unit_cost = Decimal(str(self.unit_cost))
        
        if self.unit_label == '元/W':
            # 元/W -> 万元
            total = (capacity_mw * Decimal('1000000') * unit_cost) / Decimal('10000')
        elif self.unit_label == '万元/MW':
            # 万元/MW -> 万元
            total = capacity_mw * unit_cost
        elif self.unit_label == '万元':
            # 固定成本
            total = unit_cost
        else:
            total = Decimal('0')
        
        self.total_cost = float(total.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))
        return self.total_cost
    
    def __repr__(self):
        return f'<ProjectCostDetail {self.cost_item} for Project {self.project_id}>'

class ProfitAnalysis(db.Model):
    """收益与盈利能力分析结果 - 严格按照计算模型技术文档V2.0实现。"""
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))
    
    # 基础参数
    total_project_cost = db.Column(db.Float) # 项目工程总造价 (P_total, 万元)
    
    # 委托费收益计算参数
    dev_fee_rate = db.Column(db.Float, default=0.1) # 项目开发收益费率 (元/W)
    extra_investment = db.Column(db.Float, default=0) # 政府要求额外投资 (万元)
    
    # 资源费分成计算参数
    resource_fee_total = db.Column(db.Float, default=0) # 预计/实际资源费总额 (万元)
    
    # ROI计算参数
    dengpin_cost = db.Column(db.Float, default=0) # 登品自身投入成本 (万元)
    
    # 计算结果
    commission_income = db.Column(db.Float) # 登品收益_委托费 (万元)
    resource_income = db.Column(db.Float) # 登品收益_资源费分成 (万元)
    total_income = db.Column(db.Float) # 项目总收益 (万元)
    net_profit = db.Column(db.Float) # 净利润 (万元)
    roi_percentage = db.Column(db.Float) # 投资回报率 (%)
    
    # 兼容性字段（废弃，保留用于数据迁移）
    market_profit_rate = db.Column(db.Float) # 已废弃：市场公允利润率 (%)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    project = db.relationship('Project', backref='analyses')
    
    def calculate_profit_analysis(self):
        """
        执行完整的收益分析计算 - 使用技术文档定义的算法
        
        Returns:
            dict: 包含所有计算结果的字典
        """
        from app.profit_calculator import ProfitCalculator
        
        if not self.project or not self.project.capacity_mw:
            raise ValueError("项目容量信息缺失，无法进行收益分析")
        
        # 执行综合收益分析计算
        results = ProfitCalculator.calculate_comprehensive_profit_analysis(
            capacity_mw=self.project.capacity_mw,
            dev_fee_rate=self.dev_fee_rate,
            extra_investment=self.extra_investment or 0,
            resource_fee_total=self.resource_fee_total or 0,
            dengpin_cost=self.dengpin_cost or 0
        )
        
        # 更新计算结果
        self.commission_income = results['commission_revenue']
        self.resource_income = results['resource_share_revenue']
        self.total_income = results['total_revenue']
        self.net_profit = results['net_profit']
        
        # 处理ROI结果
        if isinstance(results['roi'], str):
            self.roi_percentage = None  # ROI为'N/A'时设为None
        else:
            self.roi_percentage = results['roi']
        
        self.updated_at = datetime.utcnow()
        
        return results
    
    def get_analysis_summary(self):
        """
        获取收益分析摘要信息
        
        Returns:
            dict: 收益分析摘要
        """
        return {
            'project_name': self.project.name if self.project else 'Unknown',
            'project_capacity': self.project.capacity_mw if self.project else 0,
            'total_project_cost': self.total_project_cost or 0,
            'dev_fee_rate': self.dev_fee_rate or 0.1,
            'extra_investment': self.extra_investment or 0,
            'resource_fee_total': self.resource_fee_total or 0,
            'dengpin_cost': self.dengpin_cost or 0,
            'commission_income': self.commission_income or 0,
            'resource_income': self.resource_income or 0,
            'total_income': self.total_income or 0,
            'net_profit': self.net_profit or 0,
            'roi_percentage': self.roi_percentage,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

    def __repr__(self):
        return f'<ProfitAnalysis for Project {self.project_id}>'

class ProjectDocument(db.Model):
    """项目文档模型，用于存储项目相关文档。"""
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)  # 原始文件名
    stored_filename = db.Column(db.String(255), nullable=False)  # 存储的文件名（包含时间戳）
    file_path = db.Column(db.String(500), nullable=False)  # 文件存储路径
    file_size = db.Column(db.Integer)  # 文件大小（字节）
    file_type = db.Column(db.String(50))  # 文件类型/扩展名
    stage = db.Column(db.String(64))  # 关联的项目阶段
    description = db.Column(db.Text)  # 文档描述
    uploaded_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 关系
    project = db.relationship('Project', backref='documents')
    uploader = db.relationship('User', backref='uploaded_documents')
    
    def __repr__(self):
        return f'<ProjectDocument {self.filename} for Project {self.project_id}>'