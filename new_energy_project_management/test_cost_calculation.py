#!/usr/bin/env python
# -*- coding: utf-8 -*-

from app import create_app, db
from app.models import Project, CostModel

def test_cost_calculation():
    app = create_app()
    with app.app_context():
        # 测试光伏项目成本计算
        project = Project.query.filter_by(name='测试光伏项目A').first()
        if project:
            cost_model = CostModel.query.filter_by(project_type=project.project_type).first()
            if cost_model:
                total_cost = cost_model.calculate_total_cost(project.capacity_mw)
                unit_cost = sum(cost_model.cost_items.values())
                
                print(f'项目: {project.name}')
                print(f'类型: {project.project_type}')
                print(f'容量: {project.capacity_mw}MW')
                print(f'总投资: {total_cost:,.2f} 万元')
                print(f'单位造价: {unit_cost:,.2f} {cost_model.unit_cost_label}')
                print('成本构成:')
                for k, v in cost_model.cost_items.items():
                    item_cost = v * project.capacity_mw
                    if cost_model.unit_cost_label == '元/W':
                        item_cost = project.capacity_mw * 1000 * 1000 * v / 10000
                    print(f'  {k}: {item_cost:,.2f} 万元')
                print()
            else:
                print(f'未找到 {project.project_type} 的造价模型')
        
        # 测试风电项目成本计算
        project = Project.query.filter_by(name='测试风电项目B').first()
        if project:
            cost_model = CostModel.query.filter_by(project_type=project.project_type).first()
            if cost_model:
                total_cost = cost_model.calculate_total_cost(project.capacity_mw)
                unit_cost = sum(cost_model.cost_items.values())
                
                print(f'项目: {project.name}')
                print(f'类型: {project.project_type}')
                print(f'容量: {project.capacity_mw}MW')
                print(f'总投资: {total_cost:,.2f} 万元')
                print(f'单位造价: {unit_cost:,.2f} {cost_model.unit_cost_label}')
                print('成本构成:')
                for k, v in cost_model.cost_items.items():
                    item_cost = v * project.capacity_mw
                    if cost_model.unit_cost_label == '元/W':
                        item_cost = project.capacity_mw * 1000 * 1000 * v / 10000
                    print(f'  {k}: {item_cost:,.2f} 万元')
                print()
            else:
                print(f'未找到 {project.project_type} 的造价模型')
        
        # 测试造价模型数据
        cost_models = CostModel.query.all()
        print(f'造价模型数据 (共{len(cost_models)}条):')
        for model in cost_models:
            total_unit_cost = sum(model.cost_items.values())
            print(f'- {model.project_type}: {total_unit_cost} {model.unit_cost_label}')
            print(f'  成本构成: {model.cost_items}')

if __name__ == '__main__':
    test_cost_calculation()