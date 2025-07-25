#!/usr/bin/env python
# -*- coding: utf-8 -*-

from app import create_app, db
from app.models import Project, CostModel, ProfitAnalysis

def test_profit_analysis():
    app = create_app()
    with app.app_context():
        # 测试光伏项目收益分析
        project = Project.query.filter_by(name='测试光伏项目A').first()
        if project:
            # 获取项目成本
            cost_model = CostModel.query.filter_by(project_type=project.project_type).first()
            if cost_model:
                total_cost = cost_model.calculate_total_cost(project.capacity_mw)
                
                # 创建收益分析记录
                profit_analysis = ProfitAnalysis(
                    project_id=project.id,
                    total_project_cost=total_cost,
                    market_profit_rate=15.0,  # 15%市场利润率
                    extra_investment=500.0,   # 500万额外投资
                    resource_fee_total=2000.0  # 2000万资源费
                )
                
                # 计算收益（根据PRD文档的公式）
                # 委托费收益 = (项目工程总造价 + 政府要求额外投资) × 市场公允利润率
                commission_income = (profit_analysis.total_project_cost + profit_analysis.extra_investment) * (profit_analysis.market_profit_rate / 100)
                
                # 资源费收益 = 预计/实际资源费总额
                resource_income = profit_analysis.resource_fee_total
                
                # 总收益 = 委托费收益 + 资源费收益
                total_income = commission_income + resource_income
                
                profit_analysis.commission_income = commission_income
                profit_analysis.resource_income = resource_income
                profit_analysis.total_income = total_income
                
                # 检查是否已存在该项目的分析记录
                existing_analysis = ProfitAnalysis.query.filter_by(project_id=project.id).first()
                if existing_analysis:
                    # 更新现有记录
                    existing_analysis.total_project_cost = profit_analysis.total_project_cost
                    existing_analysis.market_profit_rate = profit_analysis.market_profit_rate
                    existing_analysis.extra_investment = profit_analysis.extra_investment
                    existing_analysis.resource_fee_total = profit_analysis.resource_fee_total
                    existing_analysis.commission_income = profit_analysis.commission_income
                    existing_analysis.resource_income = profit_analysis.resource_income
                    existing_analysis.total_income = profit_analysis.total_income
                else:
                    # 添加新记录
                    db.session.add(profit_analysis)
                
                db.session.commit()
                
                print(f'项目: {project.name}')
                print(f'类型: {project.project_type}')
                print(f'容量: {project.capacity_mw}MW')
                print(f'项目工程总造价: {total_cost:,.2f} 万元')
                print(f'市场公允利润率: {profit_analysis.market_profit_rate}%')
                print(f'政府要求额外投资: {profit_analysis.extra_investment:,.2f} 万元')
                print(f'预计资源费总额: {profit_analysis.resource_fee_total:,.2f} 万元')
                print(f'委托费收益: {commission_income:,.2f} 万元')
                print(f'资源费收益: {resource_income:,.2f} 万元')
                print(f'项目总收益: {total_income:,.2f} 万元')
                print()
        
        # 测试风电项目收益分析
        project = Project.query.filter_by(name='测试风电项目B').first()
        if project:
            # 获取项目成本
            cost_model = CostModel.query.filter_by(project_type=project.project_type).first()
            if cost_model:
                total_cost = cost_model.calculate_total_cost(project.capacity_mw)
                
                # 创建收益分析记录
                profit_analysis = ProfitAnalysis(
                    project_id=project.id,
                    total_project_cost=total_cost,
                    market_profit_rate=12.0,  # 12%市场利润率
                    extra_investment=1000.0,  # 1000万额外投资
                    resource_fee_total=5000.0  # 5000万资源费
                )
                
                # 计算收益
                commission_income = (profit_analysis.total_project_cost + profit_analysis.extra_investment) * (profit_analysis.market_profit_rate / 100)
                resource_income = profit_analysis.resource_fee_total
                total_income = commission_income + resource_income
                
                profit_analysis.commission_income = commission_income
                profit_analysis.resource_income = resource_income
                profit_analysis.total_income = total_income
                
                # 检查是否已存在该项目的分析记录
                existing_analysis = ProfitAnalysis.query.filter_by(project_id=project.id).first()
                if existing_analysis:
                    # 更新现有记录
                    existing_analysis.total_project_cost = profit_analysis.total_project_cost
                    existing_analysis.market_profit_rate = profit_analysis.market_profit_rate
                    existing_analysis.extra_investment = profit_analysis.extra_investment
                    existing_analysis.resource_fee_total = profit_analysis.resource_fee_total
                    existing_analysis.commission_income = profit_analysis.commission_income
                    existing_analysis.resource_income = profit_analysis.resource_income
                    existing_analysis.total_income = profit_analysis.total_income
                else:
                    # 添加新记录
                    db.session.add(profit_analysis)
                
                db.session.commit()
                
                print(f'项目: {project.name}')
                print(f'类型: {project.project_type}')
                print(f'容量: {project.capacity_mw}MW')
                print(f'项目工程总造价: {total_cost:,.2f} 万元')
                print(f'市场公允利润率: {profit_analysis.market_profit_rate}%')
                print(f'政府要求额外投资: {profit_analysis.extra_investment:,.2f} 万元')
                print(f'预计资源费总额: {profit_analysis.resource_fee_total:,.2f} 万元')
                print(f'委托费收益: {commission_income:,.2f} 万元')
                print(f'资源费收益: {resource_income:,.2f} 万元')
                print(f'项目总收益: {total_income:,.2f} 万元')
                print()
        
        # 显示所有收益分析记录
        all_analyses = ProfitAnalysis.query.all()
        print(f'数据库中共有 {len(all_analyses)} 条收益分析记录:')
        for analysis in all_analyses:
            project = Project.query.get(analysis.project_id)
            print(f'- {project.name}: 总收益 {analysis.total_income:,.2f} 万元')

if __name__ == '__main__':
    test_profit_analysis()