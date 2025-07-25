#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
管理员后台功能测试脚本
"""

from app import create_app, db
from app.models import User, Project, CostModel, ProfitAnalysis, ProjectDocument
from datetime import datetime
import os

def test_admin_functions():
    """测试管理员后台功能"""
    app = create_app()
    
    with app.app_context():
        try:
            print("开始测试管理员后台功能...")
            
            # 1. 测试用户管理功能
            print("\n=== 1. 用户管理功能测试 ===")
            
            # 获取所有用户
            all_users = User.query.all()
            print(f"当前系统用户总数: {len(all_users)}")
            
            # 按角色统计用户
            role_counts = {}
            for user in all_users:
                role = user.role or '未分配'
                if role not in role_counts:
                    role_counts[role] = 0
                role_counts[role] += 1
            
            print("用户角色分布:")
            for role, count in role_counts.items():
                print(f"- {role}: {count} 人")
            
            # 显示用户详细信息
            print("\n用户详细信息:")
            for user in all_users:
                print(f"- ID: {user.id}, 用户名: {user.username}, 邮箱: {user.email}, 角色: {user.role}")
            
            # 测试用户权限验证
            print("\n测试用户权限验证:")
            admin_users = User.query.filter_by(role='管理员').all()
            manager_users = User.query.filter_by(role='项目经理').all()
            finance_users = User.query.filter_by(role='财务人员').all()
            employee_users = User.query.filter_by(role='普通员工').all()
            
            print(f"管理员用户: {len(admin_users)} 人")
            print(f"项目经理: {len(manager_users)} 人")
            print(f"财务人员: {len(finance_users)} 人")
            print(f"普通员工: {len(employee_users)} 人")
            
            # 2. 测试项目管理功能
            print("\n=== 2. 项目管理功能测试 ===")
            
            all_projects = Project.query.all()
            print(f"系统项目总数: {len(all_projects)}")
            
            # 按项目类型统计
            type_counts = {}
            for project in all_projects:
                proj_type = project.project_type or '未分类'
                if proj_type not in type_counts:
                    type_counts[proj_type] = 0
                type_counts[proj_type] += 1
            
            print("项目类型分布:")
            for proj_type, count in type_counts.items():
                print(f"- {proj_type}: {count} 个")
            
            # 按项目阶段统计
            stage_counts = {}
            for project in all_projects:
                stage = project.current_stage or '未分类'
                if stage not in stage_counts:
                    stage_counts[stage] = 0
                stage_counts[stage] += 1
            
            print("\n项目阶段分布:")
            for stage, count in stage_counts.items():
                print(f"- {stage}: {count} 个")
            
            # 计算总装机容量
            total_capacity = sum(p.capacity_mw for p in all_projects if p.capacity_mw)
            print(f"\n总装机容量: {total_capacity:.2f} MW")
            
            # 显示项目详细信息
            print("\n项目详细信息:")
            for project in all_projects:
                manager_name = project.manager.username if project.manager else '未分配'
                print(f"- {project.name} ({project.project_type}) - {project.capacity_mw}MW")
                print(f"  阶段: {project.current_stage}, 负责人: {manager_name}")
                print(f"  创建时间: {project.created_at}")
            
            # 3. 测试造价模型管理
            print("\n=== 3. 造价模型管理测试 ===")
            
            cost_models = CostModel.query.all()
            print(f"造价模型数量: {len(cost_models)}")
            
            for model in cost_models:
                print(f"\n{model.project_type} 造价模型:")
                print(f"- 单位: {model.unit_cost_label}")
                print(f"- 成本构成总览: {model.cost_items}")
                
                # 计算单位造价合计
                total_unit_cost = sum(model.cost_items.values()) if model.cost_items else 0
                print(f"- 单位造价合计: {total_unit_cost} {model.unit_cost_label}")
                
                # 测试造价计算
                test_capacity = 100  # 100MW
                total_cost = model.calculate_total_cost(test_capacity)
                print(f"- 测试计算 ({test_capacity}MW): {total_cost:.2f} 万元")
            
            # 4. 测试收益分析数据管理
            print("\n=== 4. 收益分析数据管理测试 ===")
            
            profit_analyses = ProfitAnalysis.query.all()
            print(f"收益分析记录数量: {len(profit_analyses)}")
            
            total_project_cost = 0
            total_income = 0
            
            for analysis in profit_analyses:
                project_name = analysis.project.name if analysis.project else '未知项目'
                print(f"\n项目: {project_name}")
                print(f"- 工程总造价: {analysis.total_project_cost:.2f} 万元")
                print(f"- 市场公允利润率: {analysis.market_profit_rate:.2f}%")
                print(f"- 额外投资: {analysis.extra_investment:.2f} 万元")
                print(f"- 预计资源费: {analysis.resource_fee_total:.2f} 万元")
                print(f"- 委托费收益: {analysis.commission_income:.2f} 万元")
                print(f"- 资源费收益: {analysis.resource_income:.2f} 万元")
                print(f"- 项目总收益: {analysis.total_income:.2f} 万元")
                
                total_project_cost += analysis.total_project_cost or 0
                total_income += analysis.total_income or 0
            
            print(f"\n汇总统计:")
            print(f"- 总工程造价: {total_project_cost:.2f} 万元")
            print(f"- 总预期收益: {total_income:.2f} 万元")
            if total_project_cost > 0:
                profit_rate = (total_income / total_project_cost) * 100
                print(f"- 整体收益率: {profit_rate:.2f}%")
            
            # 5. 测试文档管理统计
            print("\n=== 5. 文档管理统计测试 ===")
            
            all_documents = ProjectDocument.query.all()
            print(f"系统文档总数: {len(all_documents)}")
            
            # 按项目统计文档
            project_doc_stats = {}
            for doc in all_documents:
                project_name = doc.project.name if doc.project else '未知项目'
                if project_name not in project_doc_stats:
                    project_doc_stats[project_name] = {'count': 0, 'size': 0}
                project_doc_stats[project_name]['count'] += 1
                project_doc_stats[project_name]['size'] += doc.file_size or 0
            
            print("\n各项目文档统计:")
            total_size = 0
            for project_name, stats in project_doc_stats.items():
                size_mb = stats['size'] / (1024 * 1024) if stats['size'] > 0 else 0
                print(f"- {project_name}: {stats['count']} 个文档, {size_mb:.2f} MB")
                total_size += stats['size']
            
            total_size_mb = total_size / (1024 * 1024) if total_size > 0 else 0
            print(f"\n文档存储总大小: {total_size_mb:.2f} MB")
            
            # 按文件类型统计
            file_type_stats = {}
            for doc in all_documents:
                file_type = doc.file_type or '未知'
                if file_type not in file_type_stats:
                    file_type_stats[file_type] = 0
                file_type_stats[file_type] += 1
            
            print("\n文件类型分布:")
            for file_type, count in file_type_stats.items():
                print(f"- {file_type}: {count} 个")
            
            # 6. 测试系统健康状况
            print("\n=== 6. 系统健康状况检查 ===")
            
            # 检查数据完整性
            print("数据完整性检查:")
            
            # 检查项目是否有负责人
            projects_without_manager = Project.query.filter_by(manager_id=None).count()
            print(f"- 无负责人项目: {projects_without_manager} 个")
            
            # 检查项目是否有收益分析
            projects_with_analysis = len(set(a.project_id for a in profit_analyses))
            projects_without_analysis = len(all_projects) - projects_with_analysis
            print(f"- 无收益分析项目: {projects_without_analysis} 个")
            
            # 检查造价模型覆盖情况
            model_types = set(m.project_type for m in cost_models)
            project_types = set(p.project_type for p in all_projects if p.project_type)
            missing_models = project_types - model_types
            if missing_models:
                print(f"- 缺少造价模型的项目类型: {', '.join(missing_models)}")
            else:
                print(f"- ✅ 所有项目类型都有对应的造价模型")
            
            # 检查用户活跃度（基于文档上传）
            active_users = len(set(d.uploaded_by for d in all_documents if d.uploaded_by))
            inactive_users = len(all_users) - active_users
            print(f"- 活跃用户: {active_users} 人")
            print(f"- 非活跃用户: {inactive_users} 人")
            
            print("\n✅ 管理员后台功能测试完成")
            
        except Exception as e:
            print(f"❌ 管理员后台功能测试失败: {str(e)}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    test_admin_functions()