# API接口文档

## 概述

本文档详细描述了新能源项目管理平台的所有API接口，包括路由、参数、返回值和使用示例。

## 认证相关接口

### 用户登录
- **路由**: `POST /login`
- **功能**: 用户登录认证
- **参数**: 
  - `username`: 用户名
  - `password`: 密码
- **返回**: 登录成功后重定向到首页

### 用户注册
- **路由**: `POST /register`
- **功能**: 新用户注册
- **参数**:
  - `username`: 用户名
  - `email`: 邮箱地址
  - `password`: 密码
  - `role`: 用户角色
- **返回**: 注册成功后重定向到登录页

### 用户退出
- **路由**: `GET /logout`
- **功能**: 用户退出登录
- **权限**: 需要登录
- **返回**: 重定向到首页

## 项目管理接口

### 项目看板（首页）
- **路由**: `GET /`
- **功能**: 显示所有项目的看板视图
- **权限**: 需要登录
- **返回**: 项目列表页面，包含统计信息

### 创建项目
- **路由**: `GET /create_project` - 显示创建表单
- **路由**: `POST /create_project` - 提交创建请求
- **功能**: 创建新项目
- **权限**: 需要登录
- **参数**:
  - `name`: 项目名称
  - `project_type`: 项目类型（集中式光伏/陆上风电）
  - `capacity_mw`: 装机容量（MW）
  - `location`: 项目位置
  - `current_stage`: 当前阶段
  - `description`: 项目描述
- **返回**: 创建成功后重定向到项目详情页

### 项目详情
- **路由**: `GET /project/<int:project_id>`
- **功能**: 显示项目详细信息
- **权限**: 需要登录
- **参数**: 
  - `project_id`: 项目ID
- **返回**: 项目详情页面，包含基本信息、成本估算、收益分析

### 编辑项目
- **路由**: `GET /edit_project/<int:project_id>` - 显示编辑表单
- **路由**: `POST /edit_project/<int:project_id>` - 提交编辑请求
- **功能**: 编辑项目信息
- **权限**: 需要登录
- **参数**: 同创建项目
- **返回**: 编辑成功后重定向到项目详情页

### 删除项目
- **路由**: `POST /delete_project/<int:project_id>`
- **功能**: 删除指定项目
- **权限**: 需要登录
- **参数**:
  - `project_id`: 项目ID
- **返回**: 删除成功后重定向到首页

## 项目文档管理接口

### 项目文档列表
- **路由**: `GET /project/<int:project_id>/documents`
- **功能**: 查看项目文档列表
- **权限**: 需要登录
- **参数**:
  - `project_id`: 项目ID
- **返回**: 项目所有文档列表，包含文档信息和操作按钮

### 上传项目文档
- **路由**: `GET /project/<int:project_id>/documents/upload` - 显示上传表单
- **路由**: `POST /project/<int:project_id>/documents/upload` - 提交上传请求
- **功能**: 上传项目文档
- **权限**: 需要登录
- **参数**:
  - `project_id`: 项目ID
  - `file`: 上传文件（支持PDF、Word、Excel、图片等格式）
  - `stage`: 关联项目阶段
  - `description`: 文档描述
- **文件限制**: 最大50MB，支持多种格式
- **返回**: 上传成功后重定向到文档列表页

### 下载项目文档
- **路由**: `GET /documents/<int:document_id>/download`
- **功能**: 下载项目文档
- **权限**: 需要登录
- **参数**:
  - `document_id`: 文档ID
- **返回**: 文件下载响应

### 删除项目文档
- **路由**: `POST /documents/<int:document_id>/delete`
- **功能**: 删除项目文档
- **权限**: 需要登录
- **参数**:
  - `document_id`: 文档ID
- **操作**: 同时删除物理文件和数据库记录
- **返回**: 删除成功后重定向到文档列表页

## 成本估算接口

### 成本估算
- **路由**: `GET /cost_estimation/<int:project_id>` - 显示估算表单
- **路由**: `POST /cost_estimation/<int:project_id>` - 提交估算请求
- **功能**: 对指定项目进行成本估算
- **权限**: 需要登录
- **参数**:
  - `project_id`: 项目ID
  - `capacity_mw`: 装机容量（自动从项目信息获取）
- **计算逻辑**:
  ```
  总投资 = 装机容量 × 单位造价
  设备费 = 总投资 × 设备费比例
  工程费 = 总投资 × 工程费比例
  其他费用 = 总投资 × 其他费用比例
  ```
- **返回**: 成本估算结果页面

## 收益分析接口

### 收益分析
- **路由**: `GET /profit_analysis/<int:project_id>` - 显示分析表单
- **路由**: `POST /profit_analysis/<int:project_id>` - 提交分析请求
- **功能**: 对指定项目进行收益分析
- **权限**: 需要登录
- **参数**:
  - `project_id`: 项目ID
  - `market_profit_rate`: 市场公允利润率（%）
  - `additional_investment`: 政府要求额外投资（万元）
  - `resource_fee_total`: 资源费总额（万元）
- **计算逻辑**:
  ```
  委托费收益 = ((总投资 × 45%) × 市场公允利润率) - 政府要求额外投资
  资源费收益 = 资源费总额
  项目总收益 = 委托费收益 + 资源费收益
  ```
- **返回**: 收益分析结果页面

## 管理员后台接口

### 管理员仪表板
- **路由**: `GET /admin`
- **功能**: 显示管理员仪表板
- **权限**: 需要管理员权限
- **返回**: 管理员仪表板页面，包含系统统计信息

### 用户管理
- **路由**: `GET /admin/users` - 用户列表
- **路由**: `GET /admin/users/create` - 创建用户表单
- **路由**: `POST /admin/users/create` - 提交创建用户
- **路由**: `GET /admin/users/<int:user_id>/edit` - 编辑用户表单
- **路由**: `POST /admin/users/<int:user_id>/edit` - 提交编辑用户
- **路由**: `POST /admin/users/<int:user_id>/delete` - 删除用户
- **功能**: 管理系统用户
- **权限**: 需要管理员权限
- **参数**:
  - `username`: 用户名
  - `email`: 邮箱地址
  - `role`: 用户角色（管理员/项目经理/财务管理层/普通员工）
  - `password`: 密码（可选，默认123456）

### 项目管理（管理员）
- **路由**: `GET /admin/projects` - 项目列表
- **路由**: `GET /admin/projects/<int:project_id>/edit` - 编辑项目表单
- **路由**: `POST /admin/projects/<int:project_id>/edit` - 提交编辑项目
- **功能**: 管理员管理所有项目
- **权限**: 需要管理员权限
- **参数**: 同项目管理接口，额外包含项目经理分配

### 造价模型管理
- **路由**: `GET /admin/cost_models` - 造价模型列表
- **路由**: `GET /admin/cost_models/<int:model_id>/edit` - 编辑造价模型表单
- **路由**: `POST /admin/cost_models/<int:model_id>/edit` - 提交编辑造价模型
- **功能**: 管理系统造价模型
- **权限**: 需要管理员权限
- **参数**:
  - `project_type`: 项目类型
  - `unit_cost_label`: 单位成本标签
  - `cost_items_json`: 成本项目JSON数据
  - `cost_details_json`: 详细成本构成JSON数据

### 文档管理（管理员）
- **路由**: `GET /admin/documents` - 文档管理页面
- **功能**: 管理员管理所有项目文档
- **权限**: 需要管理员权限
- **返回**: 所有项目文档列表，支持搜索和筛选
- **功能特性**:
  - 查看所有项目的文档
  - 按项目名称、文档类型筛选
  - 支持文档搜索
  - 文档下载和删除

### 系统信息
- **路由**: `GET /admin/system_info`
- **功能**: 显示系统信息和统计数据
- **权限**: 需要管理员权限
- **返回**: 系统信息页面

## 报表导出接口

### 导出项目PDF报告
- **路由**: `GET /export/project/<int:project_id>/pdf`
- **功能**: 生成并下载项目PDF报告
- **权限**: 需要登录
- **参数**:
  - `project_id`: 项目ID
- **返回**: PDF文件下载
- **报告内容**:
  - 项目基本信息
  - 成本估算详情
  - 收益分析结果
  - 关键财务指标

### 导出项目Excel报告
- **路由**: `GET /export/project/<int:project_id>/excel`
- **功能**: 生成并下载项目Excel报告
- **权限**: 需要登录
- **参数**:
  - `project_id`: 项目ID
- **返回**: Excel文件下载
- **报告内容**: 同PDF报告，但以Excel格式呈现

### 导出所有项目汇总Excel报告
- **路由**: `GET /export/all_projects/excel`
- **功能**: 生成并下载所有项目的汇总Excel报告
- **权限**: 需要登录
- **返回**: Excel文件下载
- **报告内容**:
  - 所有项目基本信息汇总
  - 成本估算汇总
  - 收益分析汇总
  - 统计分析数据

## 数据模型

### User（用户模型）
```python
{
    "id": "整数，主键",
    "username": "字符串，用户名，唯一",
    "email": "字符串，邮箱地址，唯一",
    "password_hash": "字符串，密码哈希",
    "role": "字符串，用户角色",
    "created_at": "日期时间，创建时间"
}
```

### Project（项目模型）
```python
{
    "id": "整数，主键",
    "name": "字符串，项目名称",
    "project_type": "字符串，项目类型",
    "capacity_mw": "浮点数，装机容量（MW）",
    "location": "字符串，项目位置",
    "current_stage": "字符串，当前阶段",
    "manager_id": "整数，项目经理ID，外键",
    "description": "文本，项目描述",
    "created_at": "日期时间，创建时间",
    "updated_at": "日期时间，更新时间"
}
```

### CostModel（造价模型）
```python
{
    "id": "整数，主键",
    "project_type": "字符串，项目类型",
    "equipment_cost_ratio": "浮点数，设备费比例",
    "engineering_cost_ratio": "浮点数，工程费比例",
    "other_cost_ratio": "浮点数，其他费用比例",
    "unit_cost_per_mw": "浮点数，单位造价",
    "unit_cost_label": "字符串，单位标签",
    "created_at": "日期时间，创建时间"
}
```

### ProfitAnalysis（收益分析模型）
```python
{
    "id": "整数，主键",
    "project_id": "整数，项目ID，外键",
    "total_project_cost": "浮点数，项目总投资",
    "market_profit_rate": "浮点数，市场公允利润率",
    "additional_investment": "浮点数，额外投资",
    "resource_fee_total": "浮点数，资源费总额",
    "commission_income": "浮点数，委托费收益",
    "resource_income": "浮点数，资源费收益",
    "total_income": "浮点数，总收益",
    "created_at": "日期时间，创建时间"
}
```

## 错误处理

### 常见错误码
- **400**: 请求参数错误
- **401**: 未授权访问（需要登录）
- **403**: 权限不足
- **404**: 资源不存在
- **500**: 服务器内部错误

### 错误响应格式
```python
{
    "error": "错误类型",
    "message": "错误描述信息",
    "code": "错误代码"
}
```

## 安全机制

### CSRF保护
- 所有POST请求都需要CSRF令牌
- 使用Flask-WTF提供的CSRF保护

### 用户认证
- 使用Flask-Login管理用户会话
- 密码使用Werkzeug进行哈希存储
- 支持记住登录状态

### 权限控制
- 所有业务功能都需要用户登录
- 基于用户角色的访问控制
- 项目数据访问权限验证

#### 用户角色权限说明

**管理员（admin）**
- 拥有系统最高权限
- 可以管理所有用户（创建、编辑、删除）
- 可以管理所有项目
- 可以管理造价模型
- 可以查看系统信息和统计数据
- 可以访问管理员后台所有功能

**项目经理（project_manager）**
- 可以创建和管理自己负责的项目
- 可以进行成本估算和收益分析
- 可以导出项目报告
- 可以查看项目统计信息

**财务/管理层（finance_manager）**
- 可以查看所有项目信息
- 可以进行成本估算和收益分析
- 可以导出所有项目的汇总报告
- 具有财务数据的查看权限

**普通员工（employee）**
- 可以查看被授权的项目信息
- 可以查看项目基本统计信息
- 权限相对受限

#### 权限验证装饰器

**@login_required**
- 验证用户是否已登录
- 未登录用户将被重定向到登录页面

**@require_admin()**
- 验证用户是否具有管理员权限
- 非管理员用户将收到403权限不足错误

**@require_permission(permission)**
- 验证用户是否具有指定权限
- 支持的权限类型：'view_all_projects', 'manage_projects', 'financial_analysis'

**@require_project_access()**
- 验证用户是否有权访问特定项目
- 项目经理只能访问自己负责的项目
- 管理员和财务管理层可以访问所有项目

## 使用示例

### 创建项目示例
```python
# POST /create_project
{
    "name": "阳光新能源光伏项目",
    "project_type": "集中式光伏",
    "capacity_mw": 100.0,
    "location": "山东省济南市",
    "current_stage": "前期开发",
    "description": "100MW集中式光伏发电项目"
}
```

### 成本估算示例
```python
# POST /cost_estimation/1
# 系统自动根据项目类型和容量计算
# 返回结果：
{
    "total_investment": 27500.0,  # 万元
    "equipment_cost": 19250.0,   # 万元
    "engineering_cost": 5500.0,  # 万元
    "other_cost": 2750.0         # 万元
}
```

### 收益分析示例
```python
# POST /profit_analysis/1
{
    "market_profit_rate": 8.0,      # 8%
    "additional_investment": 500.0,  # 500万元
    "resource_fee_total": 1000.0     # 1000万元
}
# 返回结果：
{
    "commission_income": 487.5,  # 万元
    "resource_income": 1000.0,   # 万元
    "total_income": 1487.5       # 万元
}
```

## 前端技术实现

### UI现代化特性

#### 样式系统
- **现代化CSS框架**: 基于CSS3的现代化样式系统
- **响应式设计**: 支持移动设备、平板和桌面设备
- **动画效果**: CSS3过渡动画和悬停效果
- **工具类样式**: 原子化CSS类，支持快速开发

#### 组件库
- **卡片组件**: 现代化的信息展示卡片
- **按钮组件**: 多种样式的交互按钮
- **表格组件**: 响应式数据表格
- **模态框组件**: 现代化的对话框
- **表单组件**: 优化的表单输入控件

#### 无障碍设计
- **键盘导航**: 完整的键盘操作支持
- **屏幕阅读器**: ARIA标签和语义化HTML
- **颜色对比**: 符合WCAG 2.1 AA标准
- **焦点管理**: 清晰的焦点状态指示

#### 性能优化
- **CSS压缩**: 生产环境CSS文件压缩
- **缓存策略**: 静态资源缓存优化
- **懒加载**: 非关键CSS延迟加载
- **渲染优化**: 60fps流畅动画

### 浏览器兼容性
- **Chrome**: 90+
- **Firefox**: 88+
- **Safari**: 14+
- **Edge**: 90+
- **移动浏览器**: iOS Safari 14+, Chrome Mobile 90+

## 版本信息

- **API版本**: v1.0
- **UI版本**: v2.0 (现代化升级)
- **最后更新**: 2025年1月
- **兼容性**: Flask 2.3+
- **数据库**: SQLite 3.x
- **前端技术**: HTML5, CSS3, Bootstrap 5, Jinja2

## 联系信息

如有API使用问题或UI相关建议，请联系开发团队。