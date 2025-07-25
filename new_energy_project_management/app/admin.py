from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import User, Project, CostModel, ProfitAnalysis
from app.permissions import require_admin, has_permission, get_available_roles, get_role_permissions, format_permission_name
from app.forms import UserForm, CostModelForm
from werkzeug.security import generate_password_hash
from datetime import datetime

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/')
@login_required
@require_admin()
def dashboard():
    """管理员仪表板"""
    # 统计数据
    total_users = User.query.count()
    total_projects = Project.query.count()
    total_analyses = ProfitAnalysis.query.count()
    
    # 按角色统计用户
    user_stats = {}
    for role in get_available_roles():
        user_stats[role] = User.query.filter_by(role=role).count()
    
    # 按类型统计项目
    project_stats = {}
    project_types = db.session.query(Project.project_type).distinct().all()
    for project_type in project_types:
        if project_type[0]:  # 确保不是None
            project_stats[project_type[0]] = Project.query.filter_by(project_type=project_type[0]).count()
    
    # 按阶段统计项目
    stage_stats = {}
    stages = db.session.query(Project.current_stage).distinct().all()
    for stage in stages:
        if stage[0]:  # 确保不是None
            stage_stats[stage[0]] = Project.query.filter_by(current_stage=stage[0]).count()
    
    return render_template('admin/dashboard.html',
                         total_users=total_users,
                         total_projects=total_projects,
                         total_analyses=total_analyses,
                         user_stats=user_stats,
                         project_stats=project_stats,
                         stage_stats=stage_stats)

@admin_bp.route('/users')
@login_required
@require_admin()
def users():
    """用户管理页面"""
    page = request.args.get('page', 1, type=int)
    users = User.query.paginate(
        page=page, per_page=20, error_out=False)
    return render_template('admin/users.html', users=users)

@admin_bp.route('/users/create', methods=['GET', 'POST'])
@login_required
@require_admin()
def create_user():
    """创建用户"""
    form = UserForm()
    form.role.choices = [(role, role) for role in get_available_roles()]
    
    if form.validate_on_submit():
        # 检查用户名和邮箱是否已存在
        if User.query.filter_by(username=form.username.data).first():
            flash('用户名已存在', 'error')
            return render_template('admin/create_user.html', form=form)
        
        if User.query.filter_by(email=form.email.data).first():
            flash('邮箱已存在', 'error')
            return render_template('admin/create_user.html', form=form)
        
        user = User(
            username=form.username.data,
            email=form.email.data,
            role=form.role.data
        )
        user.set_password(form.password.data)
        
        db.session.add(user)
        db.session.commit()
        
        flash(f'用户 {user.username} 创建成功', 'success')
        return redirect(url_for('admin.users'))
    
    return render_template('admin/create_user.html', form=form)

@admin_bp.route('/users/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
@require_admin()
def edit_user(user_id):
    """编辑用户"""
    user = User.query.get_or_404(user_id)
    form = UserForm(obj=user)
    form.role.choices = [(role, role) for role in get_available_roles()]
    
    if form.validate_on_submit():
        # 检查用户名和邮箱是否被其他用户使用
        existing_user = User.query.filter_by(username=form.username.data).first()
        if existing_user and existing_user.id != user.id:
            flash('用户名已被其他用户使用', 'error')
            return render_template('admin/edit_user.html', form=form, user=user)
        
        existing_email = User.query.filter_by(email=form.email.data).first()
        if existing_email and existing_email.id != user.id:
            flash('邮箱已被其他用户使用', 'error')
            return render_template('admin/edit_user.html', form=form, user=user)
        
        user.username = form.username.data
        user.email = form.email.data
        user.role = form.role.data
        
        # 如果提供了新密码，则更新密码
        if form.password.data:
            user.set_password(form.password.data)
        
        db.session.commit()
        flash(f'用户 {user.username} 更新成功', 'success')
        return redirect(url_for('admin.users'))
    
    return render_template('admin/edit_user.html', form=form, user=user)

@admin_bp.route('/users/<int:user_id>/delete', methods=['POST'])
@login_required
@require_admin()
def delete_user(user_id):
    """删除用户"""
    user = User.query.get_or_404(user_id)
    
    # 不能删除自己
    if user.id == current_user.id:
        flash('不能删除自己的账户', 'error')
        return redirect(url_for('admin.users'))
    
    # 检查用户是否有关联的项目
    if user.projects:
        flash(f'用户 {user.username} 还有关联的项目，无法删除', 'error')
        return redirect(url_for('admin.users'))
    
    username = user.username
    db.session.delete(user)
    db.session.commit()
    
    flash(f'用户 {username} 删除成功', 'success')
    return redirect(url_for('admin.users'))

@admin_bp.route('/cost-models')
@login_required
@require_admin()
def cost_models():
    """造价模型管理页面"""
    models = CostModel.query.all()
    return render_template('admin/cost_models.html', models=models)

@admin_bp.route('/cost-models/<int:model_id>/edit', methods=['GET', 'POST'])
@login_required
@require_admin()
def edit_cost_model(model_id):
    """编辑造价模型"""
    model = CostModel.query.get_or_404(model_id)
    form = CostModelForm(obj=model)
    
    if form.validate_on_submit():
        # 更新造价模型数据
        model.project_type = form.project_type.data
        model.unit_cost_label = form.unit_cost_label.data
        
        # 解析成本项目数据
        cost_items = {}
        cost_details = {}
        
        # 这里需要根据表单数据更新cost_items和cost_details
        # 具体实现取决于表单的设计
        
        db.session.commit()
        flash(f'造价模型 {model.project_type} 更新成功', 'success')
        return redirect(url_for('admin.cost_models'))
    
    return render_template('admin/edit_cost_model.html', form=form, model=model)

@admin_bp.route('/roles')
@login_required
@require_admin()
def roles():
    """角色权限管理页面"""
    roles_data = []
    for role in get_available_roles():
        permissions = get_role_permissions(role)
        user_count = User.query.filter_by(role=role).count()
        roles_data.append({
            'name': role,
            'permissions': permissions,
            'user_count': user_count
        })
    
    return render_template('admin/roles.html', 
                         roles_data=roles_data,
                         format_permission_name=format_permission_name)

@admin_bp.route('/system-info')
@login_required
@require_admin()
def system_info():
    """系统信息页面"""
    import sys
    import platform
    from flask import __version__ as flask_version
    
    system_data = {
        'python_version': sys.version,
        'platform': platform.platform(),
        'flask_version': flask_version,
        'database_url': 'SQLite (app.db)',
        'total_users': User.query.count(),
        'total_projects': Project.query.count(),
        'total_cost_models': CostModel.query.count(),
        'total_analyses': ProfitAnalysis.query.count()
    }
    
    return render_template('admin/system_info.html', system_data=system_data)

@admin_bp.route('/logs')
@login_required
@require_admin()
def logs():
    """系统日志页面"""
    # 这里可以实现日志查看功能
    # 目前返回一个简单的页面
    return render_template('admin/logs.html')