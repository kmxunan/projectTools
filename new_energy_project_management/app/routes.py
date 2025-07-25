from flask import render_template, flash, redirect, url_for, request, make_response, send_file, jsonify, Blueprint, current_app
from flask_login import login_user, logout_user, current_user, login_required
from urllib.parse import urlparse
from datetime import datetime, timedelta
import json
import os
from werkzeug.utils import secure_filename
from sqlalchemy import func
from app import db
from app.models import User, Project, CostModel, ProfitAnalysis, ProjectDocument
from app.forms import LoginForm, RegistrationForm, ProjectForm, CostEstimationForm, ProfitAnalysisForm, ProjectCostDetailForm, UserForm, CostModelForm, ProjectEditForm, DocumentUploadForm
from app.reports import generate_project_report_pdf, generate_project_report_excel, generate_all_projects_excel
from app.permissions import require_admin, require_permission, has_permission, get_available_roles

main = Blueprint('main', __name__)

@main.route('/')
@main.route('/index')
@login_required
def index():
    projects = Project.query.all()
    
    # 计算KPI指标
    kpi_data = calculate_dashboard_kpis()
    
    return render_template('index.html', title='项目看板', projects=projects, kpi_data=kpi_data)

def calculate_dashboard_kpis(projects):
    """计算项目看板的KPI指标"""
    from app.models import ProfitAnalysis, ProjectDocument, CostModel
    from sqlalchemy import func
    
    # 基础统计
    total_projects = len(projects)
    total_capacity = sum(p.capacity_mw or 0 for p in projects)
    
    # 按阶段统计
    stage_stats = {}
    for project in projects:
        stage = project.current_stage or '机会挖掘'
        stage_stats[stage] = stage_stats.get(stage, 0) + 1
    
    # 按项目类型统计
    type_stats = {}
    type_capacity = {}
    for project in projects:
        ptype = project.project_type or '未知'
        type_stats[ptype] = type_stats.get(ptype, 0) + 1
        type_capacity[ptype] = type_capacity.get(ptype, 0) + (project.capacity_mw or 0)
    
    # 计算总投资和收益
    total_investment = 0
    total_revenue = 0
    total_profit = 0
    roi_values = []
    
    for project in projects:
        if project.capacity_mw:
            # 获取造价模型计算投资
            cost_model = CostModel.query.filter_by(project_type=project.project_type).first()
            if cost_model:
                investment = cost_model.calculate_total_cost(project.capacity_mw)
                total_investment += investment
            
            # 获取收益分析数据
            profit_analysis = ProfitAnalysis.query.filter_by(project_id=project.id).first()
            if profit_analysis:
                if profit_analysis.total_income:
                    total_revenue += profit_analysis.total_income
                if profit_analysis.net_profit:
                    total_profit += profit_analysis.net_profit
                if profit_analysis.roi_percentage and profit_analysis.roi_percentage > 0:
                    roi_values.append(profit_analysis.roi_percentage)
    
    # 计算平均ROI
    avg_roi = sum(roi_values) / len(roi_values) if roi_values else 0
    
    # 文档统计
    total_documents = ProjectDocument.query.count()
    
    # 最近活动项目（30天内有更新的）
    from datetime import datetime, timedelta
    recent_date = datetime.utcnow() - timedelta(days=30)
    recent_projects = [p for p in projects if p.created_at >= recent_date]
    
    # 项目经理统计
    manager_stats = {}
    for project in projects:
        if project.manager:
            manager_name = project.manager.username
            if manager_name not in manager_stats:
                manager_stats[manager_name] = {'count': 0, 'capacity': 0}
            manager_stats[manager_name]['count'] += 1
            manager_stats[manager_name]['capacity'] += project.capacity_mw or 0
    
    return {
        'total_projects': total_projects,
        'total_capacity': round(total_capacity, 1),
        'total_investment': round(total_investment, 2),
        'total_revenue': round(total_revenue, 2),
        'total_profit': round(total_profit, 2),
        'avg_roi': round(avg_roi, 2),
        'total_documents': total_documents,
        'recent_projects_count': len(recent_projects),
        'stage_stats': stage_stats,
        'type_stats': type_stats,
        'type_capacity': type_capacity,
        'manager_stats': manager_stats,
        'projects_with_analysis': len([p for p in projects if ProfitAnalysis.query.filter_by(project_id=p.id).first()])
    }

def calculate_dashboard_kpis():
    """计算项目看板的KPI指标"""
    # 基础统计
    total_projects = Project.query.count()
    total_capacity = db.session.query(func.sum(Project.capacity_mw)).scalar() or 0
    
    # 按阶段统计
    stage_stats = {}
    stages = ['机会挖掘', '前期开发', '投资决策', '建设执行', '并网运营']
    for stage in stages:
        count = Project.query.filter_by(current_stage=stage).count()
        stage_stats[stage] = count
    
    # 按类型统计
    type_stats = {}
    type_capacity = {}
    project_types = db.session.query(Project.project_type).distinct().all()
    for ptype_tuple in project_types:
        ptype = ptype_tuple[0]
        if ptype:
            count = Project.query.filter_by(project_type=ptype).count()
            capacity = db.session.query(func.sum(Project.capacity_mw)).filter_by(project_type=ptype).scalar() or 0
            type_stats[ptype] = count
            type_capacity[ptype] = capacity
    
    # 投资和收益统计
    total_investment = 0
    total_profit = 0
    roi_values = []
    
    projects_with_analysis = 0
    for project in Project.query.all():
        # 计算投资额（装机容量 * 单位投资成本，假设为400万元/MW）
        investment = project.capacity_mw * 400
        total_investment += investment
        
        # 获取收益分析数据
        profit_analysis = ProfitAnalysis.query.filter_by(project_id=project.id).first()
        if profit_analysis:
            projects_with_analysis += 1
            total_profit += profit_analysis.net_profit or 0
            if investment > 0:
                roi = ((profit_analysis.net_profit or 0) / investment) * 100
                roi_values.append(roi)
    
    avg_roi = sum(roi_values) / len(roi_values) if roi_values else 0
    
    # 文档统计
    total_documents = ProjectDocument.query.count()
    
    # 近期活跃项目（最近30天有更新的项目）
    thirty_days_ago = datetime.now() - timedelta(days=30)
    recent_projects_count = Project.query.filter(Project.created_at >= thirty_days_ago).count()
    
    return {
        'total_projects': total_projects,
        'total_capacity': f"{total_capacity:.1f}",
        'stage_stats': stage_stats,
        'type_stats': type_stats,
        'type_capacity': type_capacity,
        'total_investment': total_investment,
        'total_profit': total_profit,
        'avg_roi': avg_roi,
        'total_documents': total_documents,
        'recent_projects_count': recent_projects_count,
        'projects_with_analysis': projects_with_analysis
    }

@main.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('无效的用户名或密码')
            return redirect(url_for('main.login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or urlparse(next_page).netloc != '':
            next_page = url_for('main.index')
        return redirect(next_page)
    return render_template('auth/login.html', title='登录', form=form)

# 管理员后台路由
@main.route('/admin')
@login_required
@require_admin()
def admin_dashboard():
    """管理员仪表板。"""
    total_users = User.query.count()
    total_projects = Project.query.count()
    total_cost_models = CostModel.query.count()
    
    recent_projects = Project.query.order_by(Project.created_at.desc()).limit(5).all()
    recent_users = User.query.order_by(User.id.desc()).limit(5).all()
    
    return render_template('admin/dashboard.html', 
                         title='管理员后台',
                         total_users=total_users,
                         total_projects=total_projects,
                         total_cost_models=total_cost_models,
                         recent_projects=recent_projects,
                         recent_users=recent_users)

@main.route('/admin/users')
@login_required
@require_admin()
def admin_users():
    """用户管理页面。"""
    users = User.query.all()
    return render_template('admin/users.html', title='用户管理', users=users)

@main.route('/admin/users/create', methods=['GET', 'POST'])
@login_required
@require_admin()
def admin_create_user():
    """创建用户。"""
    form = UserForm()
    form.role.choices = [(role, role) for role in get_available_roles()]
    
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data,
            role=form.role.data
        )
        if form.password.data:
            user.set_password(form.password.data)
        else:
            user.set_password('123456')  # 默认密码
        
        db.session.add(user)
        db.session.commit()
        flash(f'用户 {user.username} 创建成功！')
        return redirect(url_for('main.admin_users'))
    
    return render_template('admin/user_form.html', title='创建用户', form=form)

@main.route('/admin/users/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
@require_admin()
def admin_edit_user(user_id):
    """编辑用户。"""
    user = User.query.get_or_404(user_id)
    form = UserForm(obj=user)
    form.role.choices = [(role, role) for role in get_available_roles()]
    
    if form.validate_on_submit():
        user.username = form.username.data
        user.email = form.email.data
        user.role = form.role.data
        if form.password.data:
            user.set_password(form.password.data)
        
        db.session.commit()
        flash(f'用户 {user.username} 更新成功！')
        return redirect(url_for('main.admin_users'))
    
    return render_template('admin/user_form.html', title='编辑用户', form=form, user=user)

@main.route('/admin/users/<int:user_id>/delete', methods=['POST'])
@login_required
@require_admin()
def admin_delete_user(user_id):
    """删除用户。"""
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash('不能删除自己的账户！')
        return redirect(url_for('main.admin_users'))
    
    db.session.delete(user)
    db.session.commit()
    flash(f'用户 {user.username} 删除成功！')
    return redirect(url_for('main.admin_users'))

@main.route('/admin/cost_models')
@login_required
@require_admin()
def admin_cost_models():
    """造价模型管理页面。"""
    cost_models = CostModel.query.all()
    return render_template('admin/cost_models.html', title='造价模型管理', cost_models=cost_models)

@main.route('/admin/cost_models/<int:model_id>/details')
@login_required
@require_admin()
def admin_cost_model_details(model_id):
    """获取造价模型详情API。"""
    cost_model = CostModel.query.get_or_404(model_id)
    return jsonify({
        'id': cost_model.id,
        'project_type': cost_model.project_type,
        'unit_cost_label': cost_model.unit_cost_label,
        'cost_items': cost_model.cost_items,
        'cost_details': cost_model.cost_details,
        'created_at': cost_model.created_at.strftime('%Y-%m-%d %H:%M:%S') if cost_model.created_at else None
    })

@main.route('/admin/cost_models/<int:model_id>/edit', methods=['GET', 'POST'])
@login_required
@require_admin()
def admin_edit_cost_model(model_id):
    """编辑造价模型。"""
    cost_model = CostModel.query.get_or_404(model_id)
    form = CostModelForm()
    
    if request.method == 'GET':
        form.project_type.data = cost_model.project_type
        form.unit_cost_label.data = cost_model.unit_cost_label
        form.cost_items_json.data = json.dumps(cost_model.cost_items, ensure_ascii=False, indent=2)
        form.cost_details_json.data = json.dumps(cost_model.cost_details, ensure_ascii=False, indent=2)
    
    if form.validate_on_submit():
        try:
            cost_model.project_type = form.project_type.data
            cost_model.unit_cost_label = form.unit_cost_label.data
            cost_model.cost_items = json.loads(form.cost_items_json.data)
            cost_model.cost_details = json.loads(form.cost_details_json.data)
            
            db.session.commit()
            flash(f'造价模型 {cost_model.project_type} 更新成功！')
            return redirect(url_for('main.admin_cost_models'))
        except json.JSONDecodeError as e:
            flash(f'JSON格式错误: {str(e)}')
    
    return render_template('admin/cost_model_form.html', title='编辑造价模型', form=form, cost_model=cost_model)

@main.route('/admin/projects')
@login_required
@require_permission('can_view_all_projects')
def admin_projects():
    """项目管理页面。"""
    projects = Project.query.all()
    return render_template('admin/projects.html', title='项目管理', projects=projects)

@main.route('/admin/projects/<int:project_id>/edit', methods=['GET', 'POST'])
@login_required
@require_permission('can_edit_all_projects')
def admin_edit_project(project_id):
    """管理员编辑项目。"""
    project = Project.query.get_or_404(project_id)
    form = ProjectEditForm(obj=project)
    
    # 设置项目经理选择列表
    managers = User.query.filter(User.role.in_(['管理员', '项目经理'])).all()
    form.manager_id.choices = [(0, '未分配')] + [(u.id, u.username) for u in managers]
    
    if form.validate_on_submit():
        project.name = form.name.data
        project.project_type = form.project_type.data
        project.capacity_mw = form.capacity_mw.data
        project.location = form.location.data
        project.current_stage = form.current_stage.data
        project.description = form.description.data
        
        if form.manager_id.data:
            project.manager_id = form.manager_id.data
        
        db.session.commit()
        flash(f'项目 {project.name} 更新成功！')
        return redirect(url_for('main.admin_projects'))
    
    return render_template('admin/project_form.html', title='编辑项目', form=form, project=project)

@main.route('/admin/system_info')
@login_required
@require_admin()
def admin_system_info():
    """系统信息页面。"""
    system_info = {
        '数据库': 'SQLite',
        '用户总数': User.query.count(),
        '项目总数': Project.query.count(),
        '造价模型数': CostModel.query.count(),
        '收益分析记录数': ProfitAnalysis.query.count(),
    }
    return render_template('admin/system_info.html', title='系统信息', system_info=system_info)

@main.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@main.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('恭喜，您已成功注册！')
        return redirect(url_for('main.login'))
    return render_template('auth/register.html', title='注册', form=form)

@main.route('/create_project', methods=['GET', 'POST'])
@login_required
def create_project():
    form = ProjectForm()
    if form.validate_on_submit():
        project = Project(
            name=form.name.data,
            project_type=form.project_type.data,
            capacity_mw=form.capacity_mw.data,
            current_stage=form.current_stage.data,
            manager=current_user,
            # 地理信息字段
            longitude=form.longitude.data,
            latitude=form.latitude.data,
            address=form.address.data,
            province=form.province.data,
            city=form.city.data,
            district=form.district.data
        )
        db.session.add(project)
        db.session.commit()
        flash('项目创建成功！')
        return redirect(url_for('main.index'))
    return render_template('project/create_edit_project.html', title='创建项目', form=form)

@main.route('/edit_project/<int:project_id>', methods=['GET', 'POST'])
@login_required
def edit_project(project_id):
    project = Project.query.get_or_404(project_id)
    # 确保只有项目经理或管理员可以编辑项目
    if project.manager != current_user and current_user.role != '管理员':
        flash('您没有权限编辑此项目。')
        return redirect(url_for('main.index'))

    form = ProjectForm(obj=project)
    if form.validate_on_submit():
        project.name = form.name.data
        project.project_type = form.project_type.data
        project.capacity_mw = form.capacity_mw.data
        project.current_stage = form.current_stage.data
        # 更新地理信息字段
        project.longitude = form.longitude.data
        project.latitude = form.latitude.data
        project.address = form.address.data
        project.province = form.province.data
        project.city = form.city.data
        project.district = form.district.data
        db.session.commit()
        flash('项目更新成功！')
        return redirect(url_for('main.index'))
    return render_template('project/create_edit_project.html', title='编辑项目', form=form)

@main.route('/delete_project/<int:project_id>', methods=['POST'])
@login_required
def delete_project(project_id):
    project = Project.query.get_or_404(project_id)
    # 确保只有项目经理或管理员可以删除项目
    if project.manager != current_user and current_user.role != '管理员':
        flash('您没有权限删除此项目。')
        return redirect(url_for('main.index'))

    db.session.delete(project)
    db.session.commit()
    flash('项目删除成功！')
    return redirect(url_for('main.index'))

@main.route('/project/<int:project_id>')
@login_required
def project_detail(project_id):
    project = Project.query.get_or_404(project_id)
    cost_estimation = ProfitAnalysis.query.filter_by(project_id=project.id).first() # 假设成本估算和收益分析结果都存储在ProfitAnalysis中，或者需要单独查询CostEstimation模型
    profit_analysis = ProfitAnalysis.query.filter_by(project_id=project.id).first()
    return render_template('project/project_detail.html', title=project.name, project=project, cost_estimation=cost_estimation, profit_analysis=profit_analysis)

@main.route('/project/<int:project_id>/update_location', methods=['POST'])
@login_required
def update_project_location(project_id):
    """更新项目地理信息"""
    project = Project.query.get_or_404(project_id)
    
    # 检查权限：项目经理或管理员可以编辑
    if project.manager != current_user and current_user.role != '管理员':
        flash('您没有权限编辑此项目的地理信息。')
        return redirect(url_for('main.project_detail', project_id=project_id))
    
    try:
        # 获取表单数据
        project.longitude = request.form.get('longitude', type=float) if request.form.get('longitude') else None
        project.latitude = request.form.get('latitude', type=float) if request.form.get('latitude') else None
        project.address = request.form.get('address', '').strip() or None
        project.province = request.form.get('province', '').strip() or None
        project.city = request.form.get('city', '').strip() or None
        project.district = request.form.get('district', '').strip() or None
        
        db.session.commit()
        flash('地理信息更新成功！')
    except Exception as e:
        db.session.rollback()
        flash(f'地理信息更新失败：{str(e)}')
    
    return redirect(url_for('main.project_detail', project_id=project_id))

@main.route('/cost_estimation/<int:project_id>', methods=['GET', 'POST'])
@login_required
def cost_estimation(project_id):
    """项目成本估算页面，支持自定义成本明细"""
    from app.models import ProjectCostDetail
    
    project = Project.query.get_or_404(project_id)
    form = CostEstimationForm()
    cost_detail_form = ProjectCostDetailForm()
    
    # 获取项目的自定义成本明细
    cost_details = ProjectCostDetail.query.filter_by(project_id=project.id).all()
    
    # 如果没有自定义成本明细，从默认模型初始化
    if not cost_details:
        cost_model = CostModel.query.filter_by(project_type=project.project_type).first()
        if cost_model and cost_model.cost_details:
            # cost_details 是 JSON 字段，在 Python 中已经是字典类型，无需 json.loads()
            default_costs = cost_model.cost_details
            for category, items in default_costs.items():
                for item_name, item_cost in items.items():
                    # item_cost 是直接的数值，需要使用项目类型对应的单位标签
                    cost_detail = ProjectCostDetail(
                        project_id=project.id,
                        cost_category=category,
                        cost_item=item_name,
                        unit_cost=item_cost,
                        unit_label=cost_model.unit_cost_label,
                        description='',
                        is_custom=False
                    )
                    cost_detail.calculate_total_cost(project.capacity_mw)
                    db.session.add(cost_detail)
            db.session.commit()
            cost_details = ProjectCostDetail.query.filter_by(project_id=project.id).all()
    
    if form.validate_on_submit():
        # 计算总造价
        total_cost = sum(detail.calculate_total_cost(project.capacity_mw) for detail in cost_details)
        
        # 保存成本估算结果到 ProfitAnalysis
        profit_analysis = ProfitAnalysis.query.filter_by(project_id=project.id).first()
        if profit_analysis:
            profit_analysis.total_project_cost = total_cost
        else:
            profit_analysis = ProfitAnalysis(
                project_id=project.id,
                total_project_cost=total_cost,
                dev_fee_rate=0.1,
                extra_investment=0,
                resource_fee_total=0,
                dengpin_cost=0,
                commission_income=0,
                resource_income=0,
                total_income=0,
                net_profit=0,
                roi_percentage=0,
                market_profit_rate=0
            )
            db.session.add(profit_analysis)
        
        # 更新所有成本明细的总成本
        for detail in cost_details:
            detail.calculate_total_cost(project.capacity_mw)
        
        db.session.commit()
        flash('成本估算成功！')
        return redirect(url_for('main.project_detail', project_id=project.id))
    
    return render_template('cost_estimation/cost_estimation.html', 
                         title='成本估算', 
                         form=form, 
                         cost_detail_form=cost_detail_form,
                         project=project, 
                         cost_details=cost_details)

@main.route('/cost_estimation/<int:project_id>/add_cost_item', methods=['POST'])
@login_required
def add_cost_item(project_id):
    """添加成本项"""
    from app.models import ProjectCostDetail
    
    project = Project.query.get_or_404(project_id)
    form = ProjectCostDetailForm()
    
    if form.validate_on_submit():
        cost_detail = ProjectCostDetail(
            project_id=project.id,
            cost_category=form.cost_category.data,
            cost_item=form.cost_item.data,
            unit_cost=form.unit_cost.data,
            unit_label=form.unit_label.data,
            description=form.description.data,
            is_custom=True
        )
        cost_detail.calculate_total_cost(project.capacity_mw)
        db.session.add(cost_detail)
        db.session.commit()
        flash(f'成本项 "{form.cost_item.data}" 添加成功！')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'{getattr(form, field).label.text}: {error}', 'error')
    
    return redirect(url_for('main.cost_estimation', project_id=project.id))

@main.route('/cost_estimation/<int:project_id>/delete_cost_item/<int:cost_item_id>', methods=['POST'])
@login_required
def delete_cost_item(project_id, cost_item_id):
    """删除成本项"""
    from app.models import ProjectCostDetail
    
    project = Project.query.get_or_404(project_id)
    cost_detail = ProjectCostDetail.query.get_or_404(cost_item_id)
    
    if cost_detail.project_id != project.id:
        flash('无效的成本项！', 'error')
        return redirect(url_for('main.cost_estimation', project_id=project.id))
    
    item_name = cost_detail.cost_item
    db.session.delete(cost_detail)
    db.session.commit()
    flash(f'成本项 "{item_name}" 删除成功！')
    
    return redirect(url_for('main.cost_estimation', project_id=project.id))

@main.route('/cost_estimation/<int:project_id>/update_cost_item/<int:cost_item_id>', methods=['POST'])
@login_required
def update_cost_item(project_id, cost_item_id):
    """更新成本项"""
    from app.models import ProjectCostDetail
    
    project = Project.query.get_or_404(project_id)
    cost_detail = ProjectCostDetail.query.get_or_404(cost_item_id)
    
    if cost_detail.project_id != project.id:
        flash('无效的成本项！', 'error')
        return redirect(url_for('main.cost_estimation', project_id=project.id))
    
    # 从表单获取更新数据
    unit_cost = request.form.get(f'unit_cost_{cost_item_id}', type=float)
    description = request.form.get(f'description_{cost_item_id}', '')
    
    if unit_cost is not None and unit_cost >= 0:
        cost_detail.unit_cost = unit_cost
        cost_detail.description = description
        cost_detail.calculate_total_cost(project.capacity_mw)
        cost_detail.updated_at = datetime.utcnow()
        db.session.commit()
        flash(f'成本项 "{cost_detail.cost_item}" 更新成功！')
    else:
        flash('单位成本必须为非负数！', 'error')
    
    return redirect(url_for('main.cost_estimation', project_id=project.id))

def calculate_profit(total_project_cost, market_profit_rate, extra_investment, resource_fee_total):
    """[已废弃] 旧版收益计算函数，保留用于向后兼容。
    
    请使用 app.profit_calculator 模块中的新计算函数。
    """
    import warnings
    warnings.warn(
        "calculate_profit函数已废弃，请使用app.profit_calculator模块中的新计算函数",
        DeprecationWarning,
        stacklevel=2
    )
    
    # 登品收益_委托费: ((P_total * 45%) * 市场公允利润率) - 政府要求额外投资
    commission_income = (total_project_cost * 0.45 * (market_profit_rate / 100)) - extra_investment

    # 登品收益_资源费: (严格按照合同的累进比例计算)
    # 这里简化处理，假设资源费总额即为资源费收益，实际应根据累进比例计算
    resource_income = resource_fee_total

    # 项目总收益: 委托费 + 资源费
    total_income = commission_income + resource_income

    return commission_income, resource_income, total_income

@main.route('/profit_analysis/<int:project_id>', methods=['GET', 'POST'])
@login_required
def profit_analysis(project_id):
    """收益分析路由 - 严格按照计算模型技术文档V2.0实现。"""
    from app.profit_calculator import ProfitCalculator
    
    project = Project.query.get_or_404(project_id)
    profit_analysis_record = ProfitAnalysis.query.filter_by(project_id=project.id).first()

    # 如果之前没有成本估算，则需要先进行成本估算
    if not profit_analysis_record or profit_analysis_record.total_project_cost is None:
        flash('请先为该项目进行成本估算。')
        return redirect(url_for('main.cost_estimation', project_id=project.id))

    form = ProfitAnalysisForm(obj=profit_analysis_record) # 预填充表单

    if form.validate_on_submit():
        try:
            # 更新表单数据到数据库记录
            profit_analysis_record.dev_fee_rate = form.dev_fee_rate.data
            profit_analysis_record.extra_investment = form.extra_investment.data
            profit_analysis_record.resource_fee_total = form.resource_fee_total.data
            profit_analysis_record.dengpin_cost = form.dengpin_cost.data
            
            # 保留旧字段用于兼容性（标记为废弃）
            profit_analysis_record.market_profit_rate = form.market_profit_rate.data

            # 使用新的收益计算逻辑
            analysis_result = ProfitCalculator.calculate_comprehensive_profit_analysis(
                capacity_mw=project.capacity_mw,
                dev_fee_rate=profit_analysis_record.dev_fee_rate,
                extra_investment=profit_analysis_record.extra_investment,
                resource_fee_total=profit_analysis_record.resource_fee_total,
                dengpin_cost=profit_analysis_record.dengpin_cost
            )

            # 更新计算结果
            profit_analysis_record.commission_income = float(analysis_result['commission_revenue'])
            profit_analysis_record.resource_income = float(analysis_result['resource_share_revenue'])
            profit_analysis_record.total_income = float(analysis_result['total_revenue'])
            profit_analysis_record.net_profit = float(analysis_result['net_profit'])
            profit_analysis_record.roi_percentage = float(analysis_result['roi']) if analysis_result['roi'] != 'N/A' else 0.0

            db.session.commit()
            flash('收益分析计算成功！')
            return redirect(url_for('main.project_detail', project_id=project.id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'收益分析计算失败: {str(e)}')
            current_app.logger.error(f'收益分析计算错误: {str(e)}')

    return render_template('profit_analysis/profit_analysis.html', 
                         title='收益分析', 
                         form=form, 
                         project=project, 
                         profit_analysis_record=profit_analysis_record)

# 报表生成路由
@main.route('/export/project/<int:project_id>/pdf')
@login_required
def export_project_pdf(project_id):
    """导出单个项目PDF报告。"""
    project = Project.query.get_or_404(project_id)
    
    try:
        pdf_buffer = generate_project_report_pdf(project_id)
        
        response = make_response(pdf_buffer.getvalue())
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'attachment; filename="{project.name}_项目报告_{datetime.now().strftime("%Y%m%d")}.pdf"'
        
        return response
    except Exception as e:
        flash(f'PDF报告生成失败: {str(e)}')
        return redirect(url_for('main.project_detail', project_id=project_id))

@main.route('/export/project/<int:project_id>/excel')
@login_required
def export_project_excel(project_id):
    """导出单个项目Excel报告。"""
    project = Project.query.get_or_404(project_id)
    
    try:
        excel_buffer = generate_project_report_excel(project_id)
        
        response = make_response(excel_buffer.getvalue())
        response.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        response.headers['Content-Disposition'] = f'attachment; filename="{project.name}_项目报告_{datetime.now().strftime("%Y%m%d")}.xlsx"'
        
        return response
    except Exception as e:
        flash(f'Excel报告生成失败: {str(e)}')
        return redirect(url_for('main.project_detail', project_id=project_id))

@main.route('/export/all_projects/excel')
@login_required
def export_all_projects_excel():
    """导出所有项目汇总Excel报告。"""
    try:
        excel_buffer = generate_all_projects_excel()
        
        response = make_response(excel_buffer.getvalue())
        response.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        response.headers['Content-Disposition'] = f'attachment; filename="项目汇总报告_{datetime.now().strftime("%Y%m%d")}.xlsx"'
        
        return response
    except Exception as e:
        flash(f'汇总报告生成失败: {str(e)}')
        return redirect(url_for('main.index'))

# 文档管理路由
@main.route('/project/<int:project_id>/documents')
@login_required
def project_documents(project_id):
    """项目文档列表页面。"""
    project = Project.query.get_or_404(project_id)
    
    # 检查用户权限：项目经理、管理员或有项目访问权限的用户
    if (project.manager != current_user and 
        current_user.role != '管理员' and 
        not has_permission('view_all_projects')):
        flash('您没有权限查看此项目的文档。')
        return redirect(url_for('main.index'))
    
    documents = ProjectDocument.query.filter_by(project_id=project_id).order_by(ProjectDocument.uploaded_at.desc()).all()
    return render_template('documents/document_list.html', 
                         title=f'{project.name} - 项目文档', 
                         project=project, 
                         documents=documents)

@main.route('/project/<int:project_id>/documents/upload', methods=['GET', 'POST'])
@login_required
def upload_document(project_id):
    """上传项目文档。"""
    project = Project.query.get_or_404(project_id)
    
    # 检查用户权限：项目经理、管理员或有项目编辑权限的用户
    if (project.manager != current_user and 
        current_user.role != '管理员' and 
        not has_permission('can_edit_all_projects')):
        flash('您没有权限上传此项目的文档。')
        return redirect(url_for('main.project_documents', project_id=project_id))
    
    form = DocumentUploadForm()
    
    if form.validate_on_submit():
        file = form.file.data
        if file:
            # 确保文件名安全
            filename = secure_filename(file.filename)
            
            # 创建项目文档目录
            upload_dir = os.path.join(current_app.root_path, '..', 'uploads', 'projects', str(project_id))
            os.makedirs(upload_dir, exist_ok=True)
            
            # 生成唯一文件名（添加时间戳）
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            name, ext = os.path.splitext(filename)
            unique_filename = f"{name}_{timestamp}{ext}"
            
            file_path = os.path.join(upload_dir, unique_filename)
            file.save(file_path)
            
            # 保存文档信息到数据库
            document = ProjectDocument(
                filename=filename,
                stored_filename=unique_filename,
                file_path=file_path,
                file_size=os.path.getsize(file_path),
                file_type=file.content_type or 'application/octet-stream',
                stage=form.stage.data,
                description=form.description.data,
                project_id=project_id,
                uploaded_by=current_user.id
            )
            
            db.session.add(document)
            db.session.commit()
            
            flash(f'文档 "{filename}" 上传成功！')
            return redirect(url_for('main.project_documents', project_id=project_id))
    
    return render_template('documents/upload_document.html', 
                         title=f'{project.name} - 上传文档', 
                         form=form, 
                         project=project)

@main.route('/documents/<int:document_id>/download')
@login_required
def download_document(document_id):
    """下载项目文档。"""
    document = ProjectDocument.query.get_or_404(document_id)
    project = document.project
    
    # 检查用户权限
    if (project.manager != current_user and 
        current_user.role != '管理员' and 
        not has_permission('view_all_projects')):
        flash('您没有权限下载此文档。')
        return redirect(url_for('main.index'))
    
    try:
        return send_file(document.file_path, 
                        as_attachment=True, 
                        download_name=document.filename)
    except FileNotFoundError:
        flash('文件不存在或已被删除。')
        return redirect(url_for('main.project_documents', project_id=project.id))

@main.route('/documents/<int:document_id>/delete', methods=['POST'])
@login_required
def delete_document(document_id):
    """删除项目文档。"""
    document = ProjectDocument.query.get_or_404(document_id)
    project = document.project
    
    # 检查用户权限：项目经理、管理员或文档上传者
    if (project.manager != current_user and 
        current_user.role != '管理员' and 
        document.uploaded_by != current_user.id and
        not has_permission('can_delete_projects')):
        flash('您没有权限删除此文档。')
        return redirect(url_for('main.project_documents', project_id=project.id))
    
    try:
        # 删除物理文件
        if os.path.exists(document.file_path):
            os.remove(document.file_path)
        
        # 删除数据库记录
        db.session.delete(document)
        db.session.commit()
        
        flash(f'文档 "{document.filename}" 删除成功！')
    except Exception as e:
        flash(f'删除文档失败: {str(e)}')
    
    return redirect(url_for('main.project_documents', project_id=project.id))

@main.route('/admin/documents')
@login_required
@require_admin()
def admin_documents():
    """管理员文档管理页面。"""
    documents = ProjectDocument.query.join(Project).order_by(ProjectDocument.uploaded_at.desc()).all()
    return render_template('admin/documents.html', 
                         title='文档管理', 
                         documents=documents)