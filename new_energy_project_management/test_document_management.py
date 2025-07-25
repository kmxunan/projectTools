#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
文档管理功能测试脚本
"""

from app import create_app, db
from app.models import Project, ProjectDocument, User
import os
import tempfile
from datetime import datetime

def test_document_management():
    """测试文档管理功能"""
    app = create_app()
    
    with app.app_context():
        try:
            print("开始测试文档管理功能...")
            
            # 获取测试项目
            projects = Project.query.all()
            if not projects:
                print("❌ 没有找到测试项目")
                return
            
            test_project = projects[0]
            print(f"使用测试项目: {test_project.name}")
            
            # 创建测试文档目录
            docs_dir = 'test_documents'
            if not os.path.exists(docs_dir):
                os.makedirs(docs_dir)
                print(f"创建文档目录: {docs_dir}")
            
            # 创建测试文档文件
            test_files = [
                ('项目可研报告.pdf', '这是一个测试的项目可研报告内容'),
                ('环评报告.docx', '这是一个测试的环评报告内容'),
                ('设计图纸.dwg', '这是一个测试的设计图纸内容'),
                ('合同文件.pdf', '这是一个测试的合同文件内容')
            ]
            
            created_files = []
            for filename, content in test_files:
                file_path = os.path.join(docs_dir, filename)
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                created_files.append(file_path)
                print(f"创建测试文件: {file_path}")
            
            # 获取测试用户
            test_user = User.query.first()
            if not test_user:
                print("❌ 没有找到测试用户")
                return
            
            # 测试文档记录创建
            print("\n测试文档记录创建...")
            document_stages = ['机会挖掘', '项目开发', '项目建设', '运营维护']
            
            for i, (filename, _) in enumerate(test_files):
                file_path = created_files[i]
                file_size = os.path.getsize(file_path)
                file_ext = os.path.splitext(filename)[1][1:]  # 获取文件扩展名
                
                # 创建文档记录
                document = ProjectDocument(
                    project_id=test_project.id,
                    filename=filename,
                    stored_filename=f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}",
                    file_path=file_path,
                    file_size=file_size,
                    file_type=file_ext,
                    stage=document_stages[i % len(document_stages)],
                    description=f"测试文档 - {filename}",
                    uploaded_by=test_user.id,
                    uploaded_at=datetime.utcnow()
                )
                
                db.session.add(document)
                print(f"✅ 创建文档记录: {filename} ({file_size} bytes)")
            
            db.session.commit()
            
            # 验证文档记录
            print("\n验证文档记录...")
            documents = ProjectDocument.query.filter_by(project_id=test_project.id).all()
            print(f"项目 '{test_project.name}' 的文档数量: {len(documents)}")
            
            for doc in documents:
                print(f"- {doc.filename} ({doc.file_type}) - {doc.file_size} bytes")
                print(f"  阶段: {doc.stage}")
                print(f"  路径: {doc.file_path}")
                print(f"  上传者: {doc.uploader.username if doc.uploader else '未知'}")
                print(f"  上传时间: {doc.uploaded_at}")
                
                # 验证文件是否存在
                if os.path.exists(doc.file_path):
                    print(f"  ✅ 文件存在")
                else:
                    print(f"  ❌ 文件不存在")
            
            # 测试文档查询功能
            print("\n测试文档查询功能...")
            
            # 按文件类型查询
            pdf_docs = ProjectDocument.query.filter(
                ProjectDocument.project_id == test_project.id,
                ProjectDocument.file_type == 'pdf'
            ).all()
            print(f"PDF文档数量: {len(pdf_docs)}")
            
            # 按文件名查询
            report_docs = ProjectDocument.query.filter(
                ProjectDocument.project_id == test_project.id,
                ProjectDocument.filename.like('%报告%')
            ).all()
            print(f"报告类文档数量: {len(report_docs)}")
            
            # 统计所有项目的文档
            print("\n所有项目文档统计:")
            all_documents = ProjectDocument.query.all()
            print(f"总文档数量: {len(all_documents)}")
            
            # 按项目分组统计
            project_doc_counts = {}
            for doc in all_documents:
                project_name = doc.project.name if doc.project else '未知项目'
                if project_name not in project_doc_counts:
                    project_doc_counts[project_name] = 0
                project_doc_counts[project_name] += 1
            
            for project_name, count in project_doc_counts.items():
                print(f"- {project_name}: {count} 个文档")
            
            # 按文件类型统计
            type_counts = {}
            for doc in all_documents:
                file_type = doc.file_type or '未知'
                if file_type not in type_counts:
                    type_counts[file_type] = 0
                type_counts[file_type] += 1
            
            print("\n按文件类型统计:")
            for file_type, count in type_counts.items():
                print(f"- {file_type}: {count} 个")
            
            # 按项目阶段统计
            stage_counts = {}
            for doc in all_documents:
                stage = doc.stage or '未分类'
                if stage not in stage_counts:
                    stage_counts[stage] = 0
                stage_counts[stage] += 1
            
            print("\n按项目阶段统计:")
            for stage, count in stage_counts.items():
                print(f"- {stage}: {count} 个")
            
            print("\n✅ 文档管理功能测试完成")
            
        except Exception as e:
            print(f"❌ 文档管理功能测试失败: {str(e)}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    test_document_management()