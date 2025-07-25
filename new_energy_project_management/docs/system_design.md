# 系统设计文档

## 1. 概述

本文件详细描述了“登品科技新能源项目管理平台”的系统架构、模块划分、数据库设计和技术选型，旨在为开发团队提供清晰、统一的设计蓝图。

## 2. 系统架构

采用基于 **Flask** 的单体式 Web 应用架构（Monolithic Architecture）。这种架构将前后端逻辑集成在同一个应用中，具有开发、部署和测试相对简单的优点，非常适合小型团队和项目初期快速迭代的需求。

- **Web 服务器**: 开发环境中使用 Flask 内置的 Werkzeug 服务器，生产环境推荐使用 Gunicorn 或 uWSGI 配合 Nginx 进行部署。
- **应用层**: Flask 作为核心框架，处理 HTTP 请求、路由分发、业务逻辑和模板渲染。
- **数据层**: 使用 Flask-SQLAlchemy 作为 ORM（对象关系映射）与数据库进行交互，实现业务逻辑与数据库操作的解耦。
- **数据库**: SQLite，一个轻量级的、无服务器的数据库引擎，数据存储在项目根目录下的单个文件中 (`app.db`)，无需额外配置，便于移植和备份。

## 3. 核心模块设计

根据 PRD 文档，系统划分为三大核心模块，并通过蓝图（Blueprints）在 Flask 中进行组织。

### 3.1. 模块A: 项目全周期管理 (`project` 蓝图)

- **功能**: 负责项目的创建、展示、更新和生命周期阶段管理。
- **核心页面**:
    - **项目看板 (`/`)**: 展示所有项目的卡片或列表，是系统的首页。
    - **项目详情页 (`/project/<id>`)**: 显示单个项目的详细信息、关联文档、任务和历史记录。
    - **项目创建/编辑页 (`/project/new`, `/project/<id>/edit`)**: 提供表单用于录入和修改项目信息。
- **数据模型**: 主要依赖 `Project` 和 `User` 模型。

### 3.2. 模块B: 项目造价估算模型 (`cost_estimation` 蓝图)

- **功能**: 根据项目类型和装机容量，自动计算项目工程总量和成本构成。
- **核心页面**:
    - **造价估算工具页 (`/cost-estimation`)**: 提供表单让用户输入项目类型和容量，实时或异步返回计算结果。
- **数据模型**: 依赖 `CostModel` 读取预设的成本参数，计算结果可与 `Project` 关联或临时展示。
- **后台管理**: 管理员应有权限在后台修改 `CostModel` 中的参考单价。

### 3.3. 模块C: 收益与盈利能力分析 (`profit_analysis` 蓝图)

- **功能**: 结合项目造价和市场参数，计算登品科技的收益并生成分析报告。
- **核心页面**:
    - **盈利分析页 (`/project/<id>/analysis`)**: 针对特定项目，输入利润率等参数，进行收益测算。
- **数据模型**: 计算结果存储在 `ProfitAnalysis` 模型中，并与 `Project` 关联。

### 3.4. 认证与权限模块 (`auth` 蓝图)

- **功能**: 负责用户注册、登录、退出和会话管理。
- **核心页面**: 登录页、注册页。
- **数据模型**: `User` 模型。
- **权限控制**: 通过 `User` 模型中的 `role` 字段，结合 Flask-Login 和装饰器，实现不同角色（管理员、项目经理等）对不同功能模块的访问控制。

## 4. 数据库设计

数据库实体关系 (ERD) 如下：

- **User**: 存储用户信息和角色。
    - `id` (PK), `username`, `email`, `password_hash`, `role`
- **Project**: 存储项目核心信息。
    - `id` (PK), `name`, `project_type`, `capacity_mw`, `current_stage`, `manager_id` (FK to User)
- **CostModel**: 存储不同项目类型的标准化造价模型。
    - `id` (PK), `project_type`, `cost_items` (JSON), `unit_cost_label`
- **ProfitAnalysis**: 存储每个项目的盈利分析结果。
    - `id` (PK), `project_id` (FK to Project), `total_project_cost`, `market_profit_rate`, `commission_income`, `resource_income`, `total_income`

**关系**: 
- 一个 `User` (项目经理) 可以管理多个 `Project` (一对多)。
- 一个 `Project` 可以有多次 `ProfitAnalysis` (一对多)。

## 5. 前端设计

- **模板引擎**: 使用 Flask 自带的 **Jinja2**，实现服务器端渲染。
- **UI 框架**: 采用 **Bootstrap 5 + 现代化CSS框架**，快速构建响应式、简洁美观的界面。
- **设计风格**: 现代化卡片式设计，响应式布局，统计数据可视化展示。
- **动画系统**: CSS3过渡动画和悬停效果，提升用户交互体验。
- **工具类样式**: 完整的工具类样式系统，支持快速UI开发和原型设计。
- **无障碍设计**: 遵循WCAG标准的无障碍设计，确保所有用户都能正常使用。
- **打印优化**: 专门的打印样式优化，确保报表和文档的打印效果。
- **静态文件**: CSS, JavaScript, 图片等文件存放在 `app/static/` 目录下，并通过 Flask 的 `url_for` 函数进行引用。

## 6. 报表生成系统

### 6.1. 技术实现
- **PDF报告**: 使用 **ReportLab** 库生成专业的PDF报告
- **Excel报告**: 使用 **Pandas** 和 **OpenPyXL** 生成Excel格式报告
- **报告类型**: 
  - 单项目详细报告（PDF/Excel）
  - 所有项目汇总报告（Excel）

### 6.2. 报告内容
- 项目基本信息
- 成本估算详情
- 收益分析结果
- 关键财务指标
- 项目状态和进度

### 6.3. 导出功能
- 项目详情页面集成导出按钮
- 项目看板页面提供汇总报告导出
- 支持即时下载和文件管理

## 7. 技术栈详情

### 7.1. 后端技术
- **Flask**: 2.3.x - Web应用框架
- **Flask-SQLAlchemy**: 3.0.x - ORM数据库操作
- **Flask-Login**: 0.6.x - 用户认证管理
- **Flask-WTF**: 1.1.x - 表单处理和CSRF保护
- **Flask-Migrate**: 4.0.x - 数据库迁移管理
- **ReportLab**: 4.0.x - PDF报告生成
- **Pandas**: 2.0.x - 数据处理和Excel生成
- **OpenPyXL**: 3.1.x - Excel文件操作

### 7.2. 前端技术
- **Bootstrap**: 5.3.x - UI组件框架
- **Jinja2**: 3.1.x - 模板引擎
- **JavaScript**: 原生JS处理交互逻辑
- **CSS3**: 自定义样式和动画效果

### 7.3. 数据库
- **SQLite**: 3.x - 开发环境数据库
- **SQLAlchemy**: 2.0.x - ORM映射层

## 8. 实际实现状态

### 8.1. 已完成功能模块

#### 项目管理模块 ✅
- 项目看板（首页）- 卡片式展示
- 项目创建、编辑、删除功能
- 项目详情页面
- 项目生命周期阶段管理
- 统计数据展示

#### 成本估算模块 ✅
- 集中式光伏造价模型（2.75元/W）
- 陆上风电造价模型（630万元/MW）
- 自动化成本计算
- 详细成本构成分析
- 造价模型数据管理

#### 收益分析模块 ✅
- 委托费收益计算
- 资源费收益计算
- 总收益汇总
- 市场公允利润率参数
- 额外投资扣减

#### 报表生成模块 ✅
- PDF项目报告生成
- Excel项目报告生成
- 汇总Excel报告
- 报表下载功能
- UI集成导出按钮

#### 用户认证模块 ✅
- 用户注册、登录、退出
- 会话管理
- 基础权限控制
- 角色字段支持

#### 用户界面现代化模块 ✅
- 现代化CSS框架和样式系统
- 响应式设计和动画效果
- 首页界面全面优化
- 模态框和交互组件现代化
- 无障碍设计和打印优化

### 8.2. 核心算法实现

#### 成本估算算法
```
总投资 = 装机容量 × 单位造价
设备费 = 总投资 × 设备费比例
工程费 = 总投资 × 工程费比例
其他费用 = 总投资 × 其他费用比例
```

#### 收益计算算法
```
委托费收益 = ((总投资 × 45%) × 市场公允利润率) - 政府要求额外投资
资源费收益 = 资源费总额
项目总收益 = 委托费收益 + 资源费收益
```

### 8.3. 数据模型实现

#### User模型
- id, username, email, password_hash, role, created_at

#### Project模型  
- id, name, project_type, capacity_mw, location, current_stage, manager_id, description, created_at, updated_at

#### CostModel模型
- id, project_type, equipment_cost_ratio, engineering_cost_ratio, other_cost_ratio, unit_cost_per_mw, unit_cost_label, created_at

#### ProfitAnalysis模型
- id, project_id, total_project_cost, market_profit_rate, additional_investment, resource_fee_total, commission_income, resource_income, total_income, created_at

## 9. 文件结构

```
new_energy_project_management/
├── app/
│   ├── __init__.py          # Flask应用初始化
│   ├── models.py            # 数据模型定义
│   ├── routes.py            # 路由和视图函数
│   ├── forms.py             # WTF表单定义
│   ├── reports.py           # 报表生成功能
│   ├── templates/           # Jinja2模板文件
│   │   ├── base.html        # 基础模板
│   │   ├── index.html       # 项目看板
│   │   ├── auth/            # 认证相关模板
│   │   ├── project/         # 项目管理模板
│   │   ├── cost_estimation/ # 成本估算模板
│   │   └── profit_analysis/ # 收益分析模板
│   └── static/              # 静态文件
│       ├── css/
│       ├── js/
│       └── images/
├── docs/                    # 项目文档
│   ├── project_plan.md      # 项目开发计划
│   ├── system_design.md     # 系统设计文档
│   └── development_progress.md # 开发进度报告
├── migrations/              # 数据库迁移文件
├── config.py               # 应用配置
├── run.py                  # 应用启动文件
├── requirements.txt        # 依赖包列表
├── init_cost_models.py     # 造价模型初始化脚本
└── create_admin.py         # 管理员账户创建脚本
```

## 10. 部署和运维

### 10.1. 开发环境
- Python 3.8+
- Flask开发服务器
- SQLite数据库文件

### 10.2. 生产环境建议
- **Web服务器**: Nginx + Gunicorn
- **数据库**: PostgreSQL 或 MySQL
- **缓存**: Redis（可选）
- **监控**: 日志记录和错误追踪

### 10.3. 安全考虑
- CSRF保护（Flask-WTF）
- 密码哈希存储
- 会话安全管理
- 文件上传安全验证（待实现）

## 11. 下一步开发计划

### 11.1. 权限管理增强
- 细粒度权限控制
- 管理员后台界面
- 用户角色管理

### 11.2. 文档管理功能
- 项目文档上传
- 文件分类和版本控制
- 文档预览功能

### 11.3. 高级分析功能
- 敏感性分析
- 数据可视化图表
- 项目对比分析

### 11.4. 系统优化
- 性能优化
- 错误处理完善
- 用户体验改进