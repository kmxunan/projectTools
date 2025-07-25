from app import create_app, db
from app.models import CostModel

app = create_app()

def init_cost_models():
    """初始化造价模型数据。"""
    with app.app_context():
        # 检查是否已存在造价模型
        if CostModel.query.count() == 0:
            # 集中式光伏电站造价模型
            photovoltaic_cost_items = {
                '设备费': 1.72,  # 光伏组件1.10 + 逆变器0.15 + 支架0.25 + 箱变开关柜0.10 + 电缆0.12
                '工程费': 0.70,  # 建安工程0.50 + 送出线路0.20
                '其他费用': 0.33  # 土地费用0.18 + 项目前期费0.05 + 管理费0.10
            }
            
            photovoltaic_cost_details = {
                '设备费': {
                    '光伏组件': 1.10,
                    '逆变器': 0.15,
                    '支架': 0.25,
                    '箱变、开关柜': 0.10,
                    '电缆': 0.12
                },
                '工程费': {
                    '建安工程(含桩基)': 0.50,
                    '送出线路工程': 0.20
                },
                '其他费用': {
                    '土地费用/租金': 0.18,
                    '项目前期费': 0.05,
                    '管理费': 0.10
                }
            }
            
            photovoltaic_model = CostModel(
                project_type='集中式光伏',
                cost_items=photovoltaic_cost_items,
                cost_details=photovoltaic_cost_details,
                unit_cost_label='元/W'
            )
            
            # 陆上风电项目造价模型
            wind_cost_items = {
                '设备费': 400,  # 风力发电机组280 + 塔筒80 + 箱变主变40
                '工程费': 170,  # 道路与基础90 + 安装与吊装50 + 集电线路30
                '其他费用': 60   # 土地征用20 + 项目前期费15 + 管理与并网费25
            }
            
            wind_cost_details = {
                '设备费': {
                    '风力发电机组': 280,
                    '塔筒': 80,
                    '箱变、主变': 40
                },
                '工程费': {
                    '道路与基础工程': 90,
                    '安装与吊装工程': 50,
                    '集电线路工程': 30
                },
                '其他费用': {
                    '土地征用/租金': 20,
                    '项目前期费': 15,
                    '管理与并网费': 25
                }
            }
            
            wind_model = CostModel(
                project_type='陆上风电',
                cost_items=wind_cost_items,
                cost_details=wind_cost_details,
                unit_cost_label='万元/MW'
            )
            
            db.session.add(photovoltaic_model)
            db.session.add(wind_model)
            db.session.commit()
            
            print('造价模型初始化成功！')
            print(f'集中式光伏单位造价: {sum(photovoltaic_cost_items.values())} 元/W')
            print(f'陆上风电单位造价: {sum(wind_cost_items.values())} 万元/MW')
        else:
            print('造价模型已存在，无需初始化。')
            # 显示现有模型信息
            models = CostModel.query.all()
            for model in models:
                total_cost = sum(model.cost_items.values())
                print(f'{model.project_type}: {total_cost} {model.unit_cost_label}')

if __name__ == '__main__':
    init_cost_models()