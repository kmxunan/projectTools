# 新能源项目管理系统

一个基于Flask的现代化新能源项目全生命周期管理平台，专为登品科技设计，提供项目管理、成本估算、收益分析和报表生成等核心功能。

## 🚀 项目特色

- **全生命周期管理**: 从项目立项到竣工验收的完整流程管理
- **智能成本估算**: 基于行业标准的自动化造价计算模型
- **收益分析**: 精确的盈利能力分析和投资回报计算
- **现代化界面**: 响应式设计，支持移动端访问
- **报表生成**: 一键生成PDF和Excel格式的专业报告
- **地理信息**: 集成高德地图API，支持项目位置管理

## 📋 功能模块

### 1. 项目管理模块
- 项目看板（卡片式展示）
- 项目创建、编辑、删除
- 项目详情页面
- 生命周期阶段管理
- 地理位置管理（地图选点、地址搜索）
- 统计数据展示

### 2. 成本估算模块
- 集中式光伏造价模型（2.75元/W）
- 陆上风电造价模型（630万元/MW）
- 自动化成本计算
- 详细成本构成分析
- 造价模型数据管理

### 3. 收益分析模块
- 委托费收益计算
- 资源费收益计算
- 总收益汇总
- 市场公允利润率参数
- 额外投资扣减

### 4. 报表生成模块
- PDF项目报告生成
- Excel项目报告生成
- 汇总Excel报告
- 报表下载功能

### 5. 用户认证模块
- 用户注册、登录、退出
- 会话管理
- 基础权限控制
- 角色管理

## 🛠 技术栈

### 后端技术
- **Flask 2.3.x** - Web应用框架
- **Flask-SQLAlchemy 3.0.x** - ORM数据库操作
- **Flask-Login 0.6.x** - 用户认证管理
- **Flask-WTF 1.1.x** - 表单处理和CSRF保护
- **Flask-Migrate 4.0.x** - 数据库迁移管理
- **ReportLab 4.0.x** - PDF报告生成
- **Pandas 2.0.x** - 数据处理和Excel生成
- **OpenPyXL 3.1.x** - Excel文件操作

### 前端技术
- **Bootstrap 5.3.x** - UI组件框架
- **Jinja2 3.1.x** - 模板引擎
- **JavaScript** - 原生JS处理交互逻辑
- **CSS3** - 自定义样式和动画效果
- **高德地图API** - 地理信息服务

### 数据库
- **SQLite 3.x** - 轻量级数据库
- **SQLAlchemy 2.0.x** - ORM映射层

## 📁 项目结构

```
new_energy_project_management/
├── app/
│   ├── __init__.py              # Flask应用初始化
│   ├── models.py                # 数据模型定义
│   ├── forms.py                 # 表单定义
│   ├── routes.py                # 路由和视图函数
│   ├── auth/
│   │   ├── __init__.py
│   │   └── routes.py            # 认证相关路由
│   ├── static/
│   │   ├── css/                 # 样式文件
│   │   ├── js/                  # JavaScript文件
│   │   └── images/              # 图片资源
│   └── templates/
│       ├── base.html            # 基础模板
│       ├── index.html           # 首页模板
│       ├── auth/                # 认证相关模板
│       └── project/             # 项目相关模板
├── migrations/                  # 数据库迁移文件
├── docs/                        # 项目文档
├── config.py                    # 配置文件
├── run.py                       # 应用启动文件
├── requirements.txt             # 依赖包列表
└── README.md                    # 项目说明文档
```

## 🚀 快速开始

### 环境要求
- Python 3.8+
- pip 包管理器

### 安装步骤

1. **克隆项目**
   ```bash
   git clone <repository-url>
   cd new_energy_project_management
   ```

2. **创建虚拟环境**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```

3. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

4. **初始化数据库**
   ```bash
   flask db init
   flask db migrate -m "Initial migration"
   flask db upgrade
   ```

5. **启动应用**
   ```bash
   python run.py
   ```

6. **访问应用**
   打开浏览器访问 `http://localhost:5000`

## 📊 核心算法

### 成本估算算法
```
总投资 = 装机容量 × 单位造价
设备费 = 总投资 × 设备费比例
工程费 = 总投资 × 工程费比例
其他费用 = 总投资 × 其他费用比例
```

### 收益计算算法
```
委托费收益 = ((总投资 × 45%) × 市场公允利润率) - 政府要求额外投资
资源费收益 = 资源费总额
项目总收益 = 委托费收益 + 资源费收益
```

## 🗄 数据模型

### User（用户）
- 用户基本信息
- 角色权限管理
- 密码加密存储

### Project（项目）
- 项目基本信息
- 地理位置信息
- 生命周期阶段
- 关联用户管理

### CostModel（成本模型）
- 项目类型配置
- 成本构成比例
- 单位造价标准

### ProfitAnalysis（收益分析）
- 收益计算结果
- 市场参数配置
- 历史分析记录

## 🎨 界面特色

- **现代化设计**: 采用卡片式布局和现代化色彩方案
- **响应式布局**: 完美适配桌面端和移动端
- **动画效果**: 流畅的CSS3过渡动画
- **无障碍设计**: 遵循WCAG标准
- **打印优化**: 专门的打印样式优化

## 🗺 地理信息功能

- **地图选点**: 集成高德地图，支持点击选择位置
- **地址搜索**: 智能地址搜索和自动补全
- **坐标转换**: 自动获取经纬度坐标
- **当前定位**: 支持获取用户当前位置
- **地址解析**: 坐标反查地址功能

## 📈 报表功能

### PDF报告
- 项目基本信息
- 成本估算详情
- 收益分析结果
- 专业排版设计

### Excel报告
- 详细数据表格
- 多工作表结构
- 公式计算支持
- 汇总统计功能

## 🔧 配置说明

### 环境变量
- `SECRET_KEY`: Flask应用密钥
- `DATABASE_URL`: 数据库连接字符串
- `AMAP_API_KEY`: 高德地图API密钥

### 配置文件
- `config.py`: 主要配置文件
- 支持开发、测试、生产环境配置

## 🚀 部署指南

### 生产环境部署
1. 使用Gunicorn作为WSGI服务器
2. 配置Nginx作为反向代理
3. 使用PostgreSQL或MySQL作为生产数据库
4. 配置SSL证书

### Docker部署
```bash
# 构建镜像
docker build -t new-energy-pm .

# 运行容器
docker run -p 5000:5000 new-energy-pm
```

## 🤝 贡献指南

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 📝 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 📞 联系方式

- 项目维护者: 登品科技开发团队
- 邮箱: contact@dengpin.tech
- 项目地址: [GitHub Repository]

## 🙏 致谢

感谢所有为这个项目做出贡献的开发者和测试人员。

---

**注意**: 本系统专为新能源项目管理设计，包含行业特定的计算模型和业务逻辑。在使用前请确保了解相关业务背景和计算标准。