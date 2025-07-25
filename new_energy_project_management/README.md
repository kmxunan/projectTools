# 登品科技新能源项目管理平台

## 1. 项目简介

本项目旨在为登品科技打造一个从项目机会挖掘、前期成本估算、中期过程管理到后期收益精算的一体化项目管理与决策支持平台。该平台基于 Flask 框架开发，采用前后端一体的模式，并使用 SQLite 轻量级数据库，适合10人以下的小型团队使用。

详细需求请参考：[项目开发文档 (PRD)](../登品科技新能源项目收益计算工具 - 项目开发文档 (PRD).md)

## 2. 技术栈

- **后端框架:** Flask
- **数据库:** SQLite (通过 Flask-SQLAlchemy 管理)
- **前端:** Jinja2 模板引擎, HTML/CSS/JavaScript
- **表单处理:** Flask-WTF
- **用户认证:** Flask-Login
- **数据库迁移:** Flask-Migrate

## 3. 项目结构

```
.
├── app/                    # Flask 应用核心目录
│   ├── __init__.py         # 应用工厂函数
│   ├── models.py           # SQLAlchemy 数据库模型
│   ├── forms.py            # WTForms 表单定义
│   ├── routes.py           # 应用路由/视图函数
│   ├── static/             # 静态文件 (CSS, JS, Images)
│   └── templates/          # Jinja2 前端模板
│       ├── auth/           # 认证相关模板 (登录、注册)
│       ├── cost_estimation/ # 成本估算模块模板
│       ├── profit_analysis/ # 收益分析模块模板
│       └── project/        # 项目管理模块模板
├── docs/                   # 项目开发文档
├── tests/                  # 单元测试和集成测试
├── venv/                   # Python 虚拟环境
├── .gitignore              # Git 忽略文件配置
├── config.py               # 应用配置文件
├── requirements.txt        # Python 依赖包
└── run.py                  # 应用启动脚本
```

## 4. 开发环境搭建

1.  **克隆或下载项目到本地**

2.  **创建并激活 Python 虚拟环境**
    ```bash
    # 进入项目根目录
    cd new_energy_project_management

    # 创建虚拟环境
    python -m venv venv

    # 激活虚拟环境 (Windows)
    .\venv\Scripts\activate

    # 激活虚拟环境 (macOS/Linux)
    # source venv/bin/activate
    ```

3.  **安装项目依赖**
    ```bash
    pip install -r requirements.txt
    ```

4.  **配置环境变量**
    创建一个 `.env` 文件，并设置 `FLASK_APP=run.py` 和 `SECRET_KEY`。

5.  **初始化数据库**
    ```bash
    flask db init
    flask db migrate -m "Initial migration."
    flask db upgrade
    ```

6.  **运行应用**
    ```bash
    flask run
    ```
    访问 `http://127.0.0.1:5000` 查看应用。

## 5. 下一步开发资料编写计划

1.  创建 `requirements.txt` 并填充基础依赖。
2.  编写 `config.py` 配置文件。
3.  在 `docs/` 目录下创建详细的系统设计、数据库设计和模块功能文档。
4.  定义 `app/models.py` 中的核心数据库模型。
5.  搭建 `run.py` 和 `app/__init__.py` 中的基础应用框架。