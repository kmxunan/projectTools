#!/usr/bin/env python
# -*- coding: utf-8 -*-

from app import create_app, db
from app.models import Project, CostModel, ProfitAnalysis
from app.reports import generate_project_report_pdf, generate_project_report_excel, generate_all_projects_excel
import os

def test_report_generation():
    app = create_app()
    with app.app_context():
        # 获取测试项目
        projects = Project.query.all()
        print(f'准备为 {len(projects)} 个项目生成报表...')
        
        # 创建reports目录（如果不存在）
        reports_dir = 'reports'
        if not os.path.exists(reports_dir):
            os.makedirs(reports_dir)
            print(f'创建报表目录: {reports_dir}')
        
        for project in projects:
            print(f'\n正在为项目 "{project.name}" 生成报表...')
            
            try:
                # 测试PDF报表生成
                pdf_buffer = generate_project_report_pdf(project.id)
                pdf_filename = f'{reports_dir}/project_{project.id}_{project.name}_report.pdf'
                with open(pdf_filename, 'wb') as f:
                    f.write(pdf_buffer.getvalue())
                print(f'✅ PDF报表生成成功: {pdf_filename}')
                
                # 测试Excel报表生成
                excel_buffer = generate_project_report_excel(project.id)
                excel_filename = f'{reports_dir}/project_{project.id}_{project.name}_report.xlsx'
                with open(excel_filename, 'wb') as f:
                    f.write(excel_buffer.getvalue())
                print(f'✅ Excel报表生成成功: {excel_filename}')
                
            except Exception as e:
                print(f'❌ 项目 "{project.name}" 报表生成失败: {str(e)}')
        
        try:
            # 测试汇总报表生成
            print(f'\n正在生成汇总报表...')
            summary_buffer = generate_all_projects_excel()
            summary_filename = f'{reports_dir}/all_projects_summary.xlsx'
            with open(summary_filename, 'wb') as f:
                f.write(summary_buffer.getvalue())
            print(f'✅ 汇总Excel报表生成成功: {summary_filename}')
            
        except Exception as e:
            print(f'❌ 汇总报表生成失败: {str(e)}')
        
        # 显示生成的文件列表
        print(f'\n生成的报表文件:')
        if os.path.exists(reports_dir):
            for filename in os.listdir(reports_dir):
                filepath = os.path.join(reports_dir, filename)
                file_size = os.path.getsize(filepath)
                print(f'- {filename} ({file_size} bytes)')
        
        # 验证数据完整性
        print(f'\n数据完整性验证:')
        print(f'- 项目数量: {Project.query.count()}')
        print(f'- 造价模型数量: {CostModel.query.count()}')
        print(f'- 收益分析记录数量: {ProfitAnalysis.query.count()}')
        
        # 检查每个项目的数据完整性
        for project in projects:
            cost_model = CostModel.query.filter_by(project_type=project.project_type).first()
            profit_analysis = ProfitAnalysis.query.filter_by(project_id=project.id).first()
            
            status = '✅ 完整' if cost_model and profit_analysis else '⚠️ 不完整'
            missing = []
            if not cost_model:
                missing.append('造价模型')
            if not profit_analysis:
                missing.append('收益分析')
            
            missing_str = f' (缺少: {", ".join(missing)})' if missing else ''
            print(f'  - {project.name}: {status}{missing_str}')

if __name__ == '__main__':
    test_report_generation()