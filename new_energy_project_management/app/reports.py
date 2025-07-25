from flask import make_response, send_file
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import pandas as pd
import io
from datetime import datetime
from app.models import Project, CostModel, ProfitAnalysis

# 注册中文字体（如果有的话）
try:
    pdfmetrics.registerFont(TTFont('SimSun', 'SimSun.ttf'))
    FONT_NAME = 'SimSun'
except:
    FONT_NAME = 'Helvetica'

def generate_project_report_pdf(project_id):
    """生成项目详细报告PDF。"""
    project = Project.query.get_or_404(project_id)
    cost_model = CostModel.query.filter_by(project_type=project.project_type).first()
    profit_analysis = ProfitAnalysis.query.filter_by(project_id=project_id).first()
    
    # 创建PDF文档
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    story = []
    
    # 样式设置
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontName=FONT_NAME,
        fontSize=18,
        spaceAfter=30,
        alignment=1  # 居中
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontName=FONT_NAME,
        fontSize=14,
        spaceAfter=12
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontName=FONT_NAME,
        fontSize=10,
        spaceAfter=6
    )
    
    # 标题
    story.append(Paragraph(f"新能源项目详细报告", title_style))
    story.append(Paragraph(f"项目名称: {project.name}", heading_style))
    story.append(Spacer(1, 12))
    
    # 项目基本信息
    story.append(Paragraph("项目基本信息", heading_style))
    project_data = [
        ['项目名称', project.name],
        ['项目类型', project.project_type],
        ['装机容量', f"{project.capacity_mw} MW"],
        ['当前阶段', project.current_stage],
        ['项目经理', project.manager.username if project.manager else '未分配'],
        ['创建时间', project.created_at.strftime('%Y-%m-%d %H:%M:%S')]
    ]
    
    project_table = Table(project_data, colWidths=[2*inch, 3*inch])
    project_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), FONT_NAME),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('BACKGROUND', (1, 0), (1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(project_table)
    story.append(Spacer(1, 20))
    
    # 成本估算信息
    if cost_model:
        story.append(Paragraph("成本估算信息", heading_style))
        total_cost = cost_model.calculate_total_cost(project.capacity_mw)
        
        cost_data = [['成本项目', '单位成本', '总成本(万元)']]
        for item, unit_cost in cost_model.cost_items.items():
            if cost_model.unit_cost_label == '元/W':
                total_item_cost = unit_cost * project.capacity_mw * 1000 / 10000  # 转换为万元
                cost_data.append([item, f"{unit_cost} 元/W", f"{total_item_cost:.2f}"])
            else:
                total_item_cost = unit_cost * project.capacity_mw
                cost_data.append([item, f"{unit_cost} 万元/MW", f"{total_item_cost:.2f}"])
        
        cost_data.append(['总计', '', f"{total_cost:.2f}"])
        
        cost_table = Table(cost_data, colWidths=[2*inch, 1.5*inch, 1.5*inch])
        cost_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), FONT_NAME),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(cost_table)
        story.append(Spacer(1, 20))
    
    # 收益分析信息
    if profit_analysis:
        story.append(Paragraph("收益分析信息", heading_style))
        profit_data = [
            ['项目工程总造价', f"{profit_analysis.total_project_cost:.2f} 万元"],
            ['市场公允利润率', f"{profit_analysis.market_profit_rate}%"],
            ['政府要求额外投资', f"{profit_analysis.extra_investment:.2f} 万元"],
            ['预计/实际资源费总额', f"{profit_analysis.resource_fee_total:.2f} 万元"],
            ['登品收益_委托费', f"{profit_analysis.commission_income:.2f} 万元"],
            ['登品收益_资源费', f"{profit_analysis.resource_income:.2f} 万元"],
            ['项目总收益', f"{profit_analysis.total_income:.2f} 万元"]
        ]
        
        profit_table = Table(profit_data, colWidths=[2.5*inch, 2.5*inch])
        profit_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), FONT_NAME),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('BACKGROUND', (1, 0), (1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(profit_table)
    
    # 生成PDF
    doc.build(story)
    buffer.seek(0)
    return buffer

def generate_project_report_excel(project_id):
    """生成项目详细报告Excel。"""
    project = Project.query.get_or_404(project_id)
    cost_model = CostModel.query.filter_by(project_type=project.project_type).first()
    profit_analysis = ProfitAnalysis.query.filter_by(project_id=project_id).first()
    
    # 创建Excel文件
    buffer = io.BytesIO()
    
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        # 项目基本信息工作表
        project_info = {
            '项目信息': ['项目名称', '项目类型', '装机容量(MW)', '当前阶段', '项目经理', '创建时间'],
            '详细信息': [
                project.name,
                project.project_type,
                project.capacity_mw,
                project.current_stage,
                project.manager.username if project.manager else '未分配',
                project.created_at.strftime('%Y-%m-%d %H:%M:%S')
            ]
        }
        df_project = pd.DataFrame(project_info)
        df_project.to_excel(writer, sheet_name='项目信息', index=False)
        
        # 成本估算工作表
        if cost_model:
            cost_data = []
            total_cost = cost_model.calculate_total_cost(project.capacity_mw)
            
            for item, unit_cost in cost_model.cost_items.items():
                if cost_model.unit_cost_label == '元/W':
                    total_item_cost = unit_cost * project.capacity_mw * 1000 / 10000
                    cost_data.append({
                        '成本项目': item,
                        '单位成本': f"{unit_cost} 元/W",
                        '总成本(万元)': round(total_item_cost, 2)
                    })
                else:
                    total_item_cost = unit_cost * project.capacity_mw
                    cost_data.append({
                        '成本项目': item,
                        '单位成本': f"{unit_cost} 万元/MW",
                        '总成本(万元)': round(total_item_cost, 2)
                    })
            
            cost_data.append({
                '成本项目': '总计',
                '单位成本': '',
                '总成本(万元)': round(total_cost, 2)
            })
            
            df_cost = pd.DataFrame(cost_data)
            df_cost.to_excel(writer, sheet_name='成本估算', index=False)
        
        # 收益分析工作表
        if profit_analysis:
            profit_data = {
                '分析项目': [
                    '项目工程总造价(万元)',
                    '市场公允利润率(%)',
                    '政府要求额外投资(万元)',
                    '预计/实际资源费总额(万元)',
                    '登品收益_委托费(万元)',
                    '登品收益_资源费(万元)',
                    '项目总收益(万元)'
                ],
                '数值': [
                    round(profit_analysis.total_project_cost, 2),
                    profit_analysis.market_profit_rate,
                    round(profit_analysis.extra_investment, 2),
                    round(profit_analysis.resource_fee_total, 2),
                    round(profit_analysis.commission_income, 2),
                    round(profit_analysis.resource_income, 2),
                    round(profit_analysis.total_income, 2)
                ]
            }
            df_profit = pd.DataFrame(profit_data)
            df_profit.to_excel(writer, sheet_name='收益分析', index=False)
    
    buffer.seek(0)
    return buffer

def generate_all_projects_excel():
    """生成所有项目汇总Excel报告。"""
    projects = Project.query.all()
    
    buffer = io.BytesIO()
    
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        # 项目汇总工作表
        project_summary = []
        for project in projects:
            cost_model = CostModel.query.filter_by(project_type=project.project_type).first()
            profit_analysis = ProfitAnalysis.query.filter_by(project_id=project.id).first()
            
            total_cost = cost_model.calculate_total_cost(project.capacity_mw) if cost_model else 0
            total_income = profit_analysis.total_income if profit_analysis else 0
            
            project_summary.append({
                '项目名称': project.name,
                '项目类型': project.project_type,
                '装机容量(MW)': project.capacity_mw,
                '当前阶段': project.current_stage,
                '项目经理': project.manager.username if project.manager else '未分配',
                '总造价(万元)': round(total_cost, 2),
                '预计收益(万元)': round(total_income, 2),
                '创建时间': project.created_at.strftime('%Y-%m-%d')
            })
        
        df_summary = pd.DataFrame(project_summary)
        df_summary.to_excel(writer, sheet_name='项目汇总', index=False)
        
        # 成本分析工作表
        cost_analysis = []
        for project in projects:
            cost_model = CostModel.query.filter_by(project_type=project.project_type).first()
            if cost_model:
                total_cost = cost_model.calculate_total_cost(project.capacity_mw)
                for item, unit_cost in cost_model.cost_items.items():
                    if cost_model.unit_cost_label == '元/W':
                        item_cost = unit_cost * project.capacity_mw * 1000 / 10000
                    else:
                        item_cost = unit_cost * project.capacity_mw
                    
                    cost_analysis.append({
                        '项目名称': project.name,
                        '项目类型': project.project_type,
                        '成本项目': item,
                        '成本金额(万元)': round(item_cost, 2)
                    })
        
        df_cost_analysis = pd.DataFrame(cost_analysis)
        df_cost_analysis.to_excel(writer, sheet_name='成本分析', index=False)
        
        # 收益分析工作表
        profit_summary = []
        for project in projects:
            profit_analysis = ProfitAnalysis.query.filter_by(project_id=project.id).first()
            if profit_analysis:
                profit_summary.append({
                    '项目名称': project.name,
                    '项目类型': project.project_type,
                    '总造价(万元)': round(profit_analysis.total_project_cost, 2),
                    '市场利润率(%)': profit_analysis.market_profit_rate,
                    '委托费收益(万元)': round(profit_analysis.commission_income, 2),
                    '资源费收益(万元)': round(profit_analysis.resource_income, 2),
                    '总收益(万元)': round(profit_analysis.total_income, 2)
                })
        
        df_profit_summary = pd.DataFrame(profit_summary)
        df_profit_summary.to_excel(writer, sheet_name='收益分析', index=False)
    
    buffer.seek(0)
    return buffer