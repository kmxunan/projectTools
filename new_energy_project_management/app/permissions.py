from functools import wraps
from flask import abort, flash, redirect, url_for
from flask_login import current_user

# 角色权限定义
ROLE_PERMISSIONS = {
    '管理员': {
        'can_manage_users': True,
        'can_manage_cost_models': True,
        'can_create_projects': True,
        'can_edit_all_projects': True,
        'can_delete_projects': True,
        'can_view_all_projects': True,
        'can_perform_cost_estimation': True,
        'can_perform_profit_analysis': True,
        'can_export_reports': True,
        'can_view_financial_data': True
    },
    '项目经理': {
        'can_manage_users': False,
        'can_manage_cost_models': False,
        'can_create_projects': True,
        'can_edit_all_projects': False,  # 只能编辑自己管理的项目
        'can_delete_projects': False,
        'can_view_all_projects': True,
        'can_perform_cost_estimation': True,
        'can_perform_profit_analysis': True,
        'can_export_reports': True,
        'can_view_financial_data': True
    },
    '财务/管理层': {
        'can_manage_users': False,
        'can_manage_cost_models': False,
        'can_create_projects': False,
        'can_edit_all_projects': False,
        'can_delete_projects': False,
        'can_view_all_projects': True,
        'can_perform_cost_estimation': False,
        'can_perform_profit_analysis': True,
        'can_export_reports': True,
        'can_view_financial_data': True
    },
    '普通员工': {
        'can_manage_users': False,
        'can_manage_cost_models': False,
        'can_create_projects': False,
        'can_edit_all_projects': False,
        'can_delete_projects': False,
        'can_view_all_projects': True,
        'can_perform_cost_estimation': False,
        'can_perform_profit_analysis': False,
        'can_export_reports': False,
        'can_view_financial_data': False
    }
}

def has_permission(permission_name):
    """检查当前用户是否具有指定权限"""
    if not current_user.is_authenticated:
        return False
    
    user_role = current_user.role
    if user_role not in ROLE_PERMISSIONS:
        return False
    
    return ROLE_PERMISSIONS[user_role].get(permission_name, False)

def can_edit_project(project):
    """检查当前用户是否可以编辑指定项目"""
    if not current_user.is_authenticated:
        return False
    
    # 管理员可以编辑所有项目
    if has_permission('can_edit_all_projects'):
        return True
    
    # 项目经理只能编辑自己管理的项目
    if current_user.role == '项目经理' and project.manager_id == current_user.id:
        return True
    
    return False

def require_permission(permission_name):
    """权限装饰器，要求用户具有指定权限"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('请先登录', 'warning')
                return redirect(url_for('main.login'))
            
            if not has_permission(permission_name):
                flash('您没有权限执行此操作', 'error')
                abort(403)
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def require_admin():
    """管理员权限装饰器"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('请先登录', 'warning')
                return redirect(url_for('main.login'))
            
            if current_user.role != '管理员':
                flash('只有管理员可以访问此页面', 'error')
                abort(403)
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def require_project_access(project_id_param='project_id'):
    """项目访问权限装饰器"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('请先登录', 'warning')
                return redirect(url_for('main.login'))
            
            # 从参数中获取项目ID
            project_id = kwargs.get(project_id_param)
            if not project_id:
                abort(404)
            
            from app.models import Project
            project = Project.query.get_or_404(project_id)
            
            # 检查用户是否有权限访问该项目
            if not (has_permission('can_view_all_projects') or 
                   (current_user.role == '项目经理' and project.manager_id == current_user.id)):
                flash('您没有权限访问此项目', 'error')
                abort(403)
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def get_user_accessible_projects():
    """获取当前用户可访问的项目列表"""
    from app.models import Project
    
    if not current_user.is_authenticated:
        return []
    
    # 管理员和财务/管理层可以查看所有项目
    if has_permission('can_view_all_projects'):
        return Project.query.all()
    
    # 项目经理只能查看自己管理的项目
    if current_user.role == '项目经理':
        return Project.query.filter_by(manager_id=current_user.id).all()
    
    # 普通员工可以查看所有项目（只读）
    return Project.query.all()

def get_available_roles():
    """获取可用的用户角色列表"""
    return list(ROLE_PERMISSIONS.keys())

def get_role_permissions(role):
    """获取指定角色的权限列表"""
    return ROLE_PERMISSIONS.get(role, {})

def format_permission_name(permission_key):
    """格式化权限名称为中文显示"""
    permission_names = {
        'can_manage_users': '用户管理',
        'can_manage_cost_models': '造价模型管理',
        'can_create_projects': '创建项目',
        'can_edit_all_projects': '编辑所有项目',
        'can_delete_projects': '删除项目',
        'can_view_all_projects': '查看所有项目',
        'can_perform_cost_estimation': '成本估算',
        'can_perform_profit_analysis': '收益分析',
        'can_export_reports': '导出报表',
        'can_view_financial_data': '查看财务数据'
    }
    return permission_names.get(permission_key, permission_key)