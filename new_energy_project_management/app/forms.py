from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, FloatField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError, Optional, Length, NumberRange
from app.models import User

class LoginForm(FlaskForm):
    """用户登录表单。"""
    username = StringField('用户名', validators=[DataRequired()])
    password = PasswordField('密码', validators=[DataRequired()])
    remember_me = BooleanField('记住我')
    submit = SubmitField('登录')

class RegistrationForm(FlaskForm):
    """用户注册表单。"""
    username = StringField('用户名', validators=[DataRequired()])
    email = StringField('电子邮箱', validators=[DataRequired(), Email()])
    password = PasswordField('密码', validators=[DataRequired()])
    password2 = PasswordField(
        '重复密码', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('注册')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('用户名已被使用。')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('电子邮箱已被注册。')

class ProjectForm(FlaskForm):
    """创建和编辑项目的表单。"""
    name = StringField('项目名称', validators=[DataRequired()])
    project_type = SelectField('项目类型', choices=[
        ('集中式光伏', '集中式光伏'), 
        ('陆上风电', '陆上风电')
    ], validators=[DataRequired()])
    capacity_mw = FloatField('装机容量 (MW)', validators=[DataRequired()])
    current_stage = SelectField('当前阶段', choices=[
        ('机会挖掘', '机会挖掘'),
        ('前期开发', '前期开发'),
        ('投资决策', '投资决策'),
        ('建设执行', '建设执行'),
        ('并网运营', '并网运营')
    ], validators=[DataRequired()])
    
    # 地理信息字段
    longitude = FloatField('经度', validators=[Optional(), NumberRange(min=-180, max=180)])
    latitude = FloatField('纬度', validators=[Optional(), NumberRange(min=-90, max=90)])
    address = StringField('详细地址', validators=[Optional(), Length(max=500)])
    province = StringField('省份', validators=[Optional(), Length(max=50)])
    city = StringField('城市', validators=[Optional(), Length(max=50)])
    district = StringField('区县', validators=[Optional(), Length(max=50)])
    
    submit = SubmitField('保存项目')

class CostEstimationForm(FlaskForm):
    """成本估算输入表单。"""
    submit = SubmitField('计算项目造价')

class ProjectCostDetailForm(FlaskForm):
    """项目成本明细表单"""
    cost_category = SelectField('成本类别', choices=[
        ('设备费', '设备费'),
        ('工程费', '工程费'),
        ('其他费用', '其他费用'),
        ('预备费', '预备费')
    ], validators=[DataRequired()])
    cost_item = StringField('成本项名称', validators=[DataRequired(), Length(min=1, max=128)])
    unit_cost = FloatField('单位成本', validators=[DataRequired(), NumberRange(min=0)])
    unit_label = SelectField('单位', choices=[
        ('元/W', '元/W'),
        ('万元/MW', '万元/MW'),
        ('万元', '万元')
    ], validators=[DataRequired()])
    description = TextAreaField('描述')
    submit = SubmitField('添加成本项')

class CostEstimationDetailForm(FlaskForm):
    """成本估算详细表单，包含成本明细"""
    # 动态添加的成本项字段将在视图中处理
    calculate = SubmitField('计算总造价')
    save = SubmitField('保存成本配置')

class ProfitAnalysisForm(FlaskForm):
    """收益分析输入表单 - 严格按照计算模型技术文档V2.0实现。"""
    # 委托费收益计算参数
    dev_fee_rate = FloatField('项目开发收益费率 (元/W)', 
                             default=0.1, 
                             validators=[DataRequired()],
                             description='默认0.1元/W，根据合同约定可调整')
    extra_investment = FloatField('政府要求额外投资 (万元)', 
                                 default=0, 
                                 validators=[Optional()],
                                 description='政府要求的额外投资，作为委托费收益的扣除项')
    
    # 资源费分成计算参数
    resource_fee_total = FloatField('预计/实际资源费总额 (万元)', 
                                   default=0,
                                   validators=[Optional()],
                                   description='沃太能源获取的资源费总额，将按累进比例分成')
    
    # ROI计算参数
    dengpin_cost = FloatField('登品自身投入成本 (万元)', 
                             default=0,
                             validators=[Optional()],
                             description='登品科技为项目付出的直接成本（人力、差旅、公关等）')
    
    # 兼容性字段（已废弃，但保留用于数据迁移）
    market_profit_rate = FloatField('市场公允利润率 (%) [已废弃]', 
                                   validators=[Optional()],
                                   description='此字段已废弃，新算法不再使用此参数')
    
    submit = SubmitField('执行收益分析')
    
    def validate_dev_fee_rate(self, field):
        """验证开发收益费率的合理性。"""
        if field.data is not None and (field.data < 0 or field.data > 1):
            raise ValidationError('开发收益费率应在0-1元/W之间')
    
    def validate_extra_investment(self, field):
        """验证额外投资的合理性。"""
        if field.data is not None and field.data < 0:
            raise ValidationError('额外投资不能为负数')
    
    def validate_resource_fee_total(self, field):
        """验证资源费总额的合理性。"""
        if field.data is not None and field.data < 0:
            raise ValidationError('资源费总额不能为负数')
    
    def validate_dengpin_cost(self, field):
        """验证登品投入成本的合理性。"""
        if field.data is not None and field.data < 0:
            raise ValidationError('登品投入成本不能为负数')

class UserForm(FlaskForm):
    """用户管理表单（管理员使用）。"""
    username = StringField('用户名', validators=[DataRequired()])
    email = StringField('电子邮箱', validators=[DataRequired(), Email()])
    password = PasswordField('密码', validators=[Optional()])
    role = SelectField('角色', validators=[DataRequired()])
    submit = SubmitField('保存用户')

class CostModelForm(FlaskForm):
    """造价模型管理表单。"""
    project_type = StringField('项目类型', validators=[DataRequired()])
    unit_cost_label = StringField('单位标签', validators=[DataRequired()])
    cost_items_json = TextAreaField('成本项目 (JSON格式)', validators=[DataRequired()])
    cost_details_json = TextAreaField('详细成本构成 (JSON格式)', validators=[DataRequired()])
    submit = SubmitField('保存模型')

class ProjectEditForm(FlaskForm):
    """项目编辑表单（增强版）。"""
    name = StringField('项目名称', validators=[DataRequired()])
    project_type = SelectField('项目类型', choices=[
        ('集中式光伏', '集中式光伏'), 
        ('陆上风电', '陆上风电')
    ], validators=[DataRequired()])
    capacity_mw = FloatField('装机容量 (MW)', validators=[DataRequired()])
    location = StringField('项目位置')
    current_stage = SelectField('当前阶段', choices=[
        ('机会挖掘', '机会挖掘'),
        ('前期开发', '前期开发'),
        ('投资决策', '投资决策'),
        ('建设执行', '建设执行'),
        ('并网运营', '并网运营')
    ], validators=[DataRequired()])
    manager_id = SelectField('项目经理', coerce=int, validators=[Optional()])
    description = TextAreaField('项目描述')
    
    # 地理信息字段
    longitude = FloatField('经度', validators=[Optional(), NumberRange(min=-180, max=180)])
    latitude = FloatField('纬度', validators=[Optional(), NumberRange(min=-90, max=90)])
    address = StringField('详细地址', validators=[Optional(), Length(max=500)])
    province = StringField('省份', validators=[Optional(), Length(max=50)])
    city = StringField('城市', validators=[Optional(), Length(max=50)])
    district = StringField('区县', validators=[Optional(), Length(max=50)])
    
    submit = SubmitField('保存项目')

class DocumentUploadForm(FlaskForm):
    """文档上传表单。"""
    file = FileField('选择文件', validators=[
        FileRequired('请选择要上传的文件'),
        FileAllowed(['pdf', 'doc', 'docx', 'xls', 'xlsx', 'txt', 'jpg', 'jpeg', 'png', 'gif', 'bmp', 'svg', 
                    'md', 'markdown', 'html', 'htm', 'xml', 'json', 'csv', 'zip', 'rar', '7z', 
                    'ppt', 'pptx', 'dwg', 'dxf', 'cad', 'xmind', 'mm', 'mmap', 'vsd', 'vsdx'], 
                   '支持上传文档、图片、压缩包、思维导图、设计图纸等多种格式文件')
    ])
    stage = SelectField('关联阶段', choices=[
        ('机会挖掘', '机会挖掘'),
        ('前期开发', '前期开发'),
        ('投资决策', '投资决策'),
        ('建设执行', '建设执行'),
        ('并网运营', '并网运营'),
        ('其他', '其他')
    ], validators=[DataRequired()])
    description = TextAreaField('文档描述', validators=[Optional()])
    submit = SubmitField('上传文档')