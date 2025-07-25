#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
收益计算模块 - 严格按照计算模型技术文档V2.0实现

本模块实现了登品科技新能源项目管理平台的核心收益计算算法，
包括委托费收益模型和资源费分成收益模型。
"""

from decimal import Decimal, ROUND_HALF_UP


class ProfitCalculator:
    """收益计算器 - 实现技术文档中定义的所有计算模型"""
    
    # 资源费分成的累进分级参数
    TIER_1_LIMIT = Decimal('4000')  # 第一级上限：4000万元
    TIER_2_LIMIT = Decimal('8000')  # 第二级上限：8000万元
    
    RATE_1 = Decimal('0.25')    # 第一级分成比例：25%
    RATE_2 = Decimal('0.75')    # 第二级分成比例：75%
    RATE_3 = Decimal('0.6667')  # 第三级分成比例：66.67%
    
    # 默认项目开发收益费率
    DEFAULT_DEV_FEE_RATE = Decimal('0.1')  # 0.1元/W
    
    @staticmethod
    def calculate_commission_revenue(capacity_mw, dev_fee_rate=None, extra_investment=0):
        """
        计算委托费收益 - Model 4.1
        
        业务逻辑：登品科技与水电六局合作的收益是一个与项目总装机容量直接挂钩的固定开发费。
        
        Args:
            capacity_mw (float): 项目装机容量，单位为兆瓦(MW)
            dev_fee_rate (float): 项目开发收益费率，单位为元/瓦(元/W)，默认0.1
            extra_investment (float): 政府要求额外投资，单位为万元
            
        Returns:
            float: 委托费收益，单位为万元
        """
        # 使用高精度计算避免浮点数误差
        capacity_mw = Decimal(str(capacity_mw))
        dev_fee_rate = Decimal(str(dev_fee_rate or ProfitCalculator.DEFAULT_DEV_FEE_RATE))
        extra_investment = Decimal(str(extra_investment))
        
        # 1. 将项目容量从兆瓦(MW)转换为瓦(W)
        capacity_watts = capacity_mw * Decimal('1000000')
        
        # 2. 计算项目开发收益总额（单位：元）
        total_dev_fee_yuan = capacity_watts * dev_fee_rate
        
        # 3. 将收益总额从"元"转换为"万元"
        total_dev_fee_wanyuan = total_dev_fee_yuan / Decimal('10000')
        
        # 4. 计算扣除额外投资后的最终收益
        final_revenue = total_dev_fee_wanyuan - extra_investment
        
        # 5. 约束条件：收益不能为负
        final_revenue = max(Decimal('0'), final_revenue)
        
        # 返回浮点数结果，保留2位小数
        return float(final_revenue.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))
    
    @staticmethod
    def calculate_resource_share_revenue(resource_fee_total):
        """
        计算资源费分成收益 - Model 4.2
        
        业务逻辑：登品科技与沃太能源合作的收益，根据沃太获取的资源费总额，
        按累进分级的比例进行分成。
        
        累进分级规则：
        - 0-4000万元：25%分成
        - 4000-8000万元：75%分成  
        - 8000万元以上：66.67%分成
        
        Args:
            resource_fee_total (float): 资源费总额，单位为万元
            
        Returns:
            float: 资源费分成收益，单位为万元
        """
        resource_fee_total = Decimal(str(resource_fee_total))
        
        if resource_fee_total <= 0:
            return 0.0
        
        total_revenue = Decimal('0')
        
        # 第一级收益计算 (0-4000万元，25%分成)
        if resource_fee_total > 0:
            amount_in_tier_1 = min(resource_fee_total, ProfitCalculator.TIER_1_LIMIT)
            tier_1_revenue = amount_in_tier_1 * ProfitCalculator.RATE_1
            total_revenue += tier_1_revenue
        
        # 第二级收益计算 (4000-8000万元，75%分成)
        if resource_fee_total > ProfitCalculator.TIER_1_LIMIT:
            amount_in_tier_2 = min(resource_fee_total, ProfitCalculator.TIER_2_LIMIT) - ProfitCalculator.TIER_1_LIMIT
            tier_2_revenue = amount_in_tier_2 * ProfitCalculator.RATE_2
            total_revenue += tier_2_revenue
        
        # 第三级收益计算 (8000万元以上，66.67%分成)
        if resource_fee_total > ProfitCalculator.TIER_2_LIMIT:
            amount_in_tier_3 = resource_fee_total - ProfitCalculator.TIER_2_LIMIT
            tier_3_revenue = amount_in_tier_3 * ProfitCalculator.RATE_3
            total_revenue += tier_3_revenue
        
        # 返回浮点数结果，保留2位小数
        return float(total_revenue.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))
    
    @staticmethod
    def calculate_total_revenue(commission_revenue, resource_share_revenue):
        """
        计算项目总收益 - Model 5.1
        
        Args:
            commission_revenue (float): 委托费收益，单位为万元
            resource_share_revenue (float): 资源费分成收益，单位为万元
            
        Returns:
            float: 项目总收益，单位为万元
        """
        commission_revenue = Decimal(str(commission_revenue))
        resource_share_revenue = Decimal(str(resource_share_revenue))
        
        total_revenue = commission_revenue + resource_share_revenue
        
        return float(total_revenue.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))
    
    @staticmethod
    def calculate_roi(total_revenue, dengpin_cost):
        """
        计算投资回报率(ROI) - Model 5.2
        
        Args:
            total_revenue (float): 项目总收益，单位为万元
            dengpin_cost (float): 登品自身投入成本，单位为万元
            
        Returns:
            float or str: 投资回报率(百分比)，如果投入成本为0则返回'N/A'
        """
        total_revenue = Decimal(str(total_revenue))
        dengpin_cost = Decimal(str(dengpin_cost))
        
        if dengpin_cost <= 0:
            return 'N/A'
        
        # 计算净利润
        net_profit = total_revenue - dengpin_cost
        
        # 计算ROI百分比
        roi_percentage = (net_profit / dengpin_cost) * Decimal('100')
        
        return float(roi_percentage.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))
    
    @classmethod
    def calculate_comprehensive_profit_analysis(cls, capacity_mw, dev_fee_rate=None, 
                                              extra_investment=0, resource_fee_total=0,
                                              dengpin_cost=0):
        """
        综合收益分析计算 - 一次性计算所有收益指标
        
        Args:
            capacity_mw (float): 项目装机容量，单位为兆瓦(MW)
            dev_fee_rate (float): 项目开发收益费率，单位为元/瓦(元/W)
            extra_investment (float): 政府要求额外投资，单位为万元
            resource_fee_total (float): 资源费总额，单位为万元
            dengpin_cost (float): 登品自身投入成本，单位为万元
            
        Returns:
            dict: 包含所有收益分析结果的字典
        """
        # 计算委托费收益
        commission_revenue = cls.calculate_commission_revenue(
            capacity_mw, dev_fee_rate, extra_investment
        )
        
        # 计算资源费分成收益
        resource_share_revenue = cls.calculate_resource_share_revenue(resource_fee_total)
        
        # 计算项目总收益
        total_revenue = cls.calculate_total_revenue(commission_revenue, resource_share_revenue)
        
        # 计算投资回报率
        roi = cls.calculate_roi(total_revenue, dengpin_cost)
        
        return {
            'commission_revenue': commission_revenue,
            'resource_share_revenue': resource_share_revenue,
            'total_revenue': total_revenue,
            'roi': roi,
            'net_profit': total_revenue - dengpin_cost if dengpin_cost > 0 else total_revenue
        }


# 向后兼容的函数接口
def calculate_profit(total_project_cost, market_profit_rate, extra_investment, resource_fee_total):
    """
    向后兼容的收益计算函数 - 已废弃，建议使用ProfitCalculator类
    
    注意：此函数使用旧的计算逻辑，不符合技术文档要求，仅为保持向后兼容性。
    新代码应使用ProfitCalculator类的方法。
    """
    import warnings
    warnings.warn(
        "calculate_profit函数已废弃，请使用ProfitCalculator类的方法",
        DeprecationWarning,
        stacklevel=2
    )
    
    # 旧的计算逻辑（不符合技术文档）
    commission_income = (total_project_cost * 0.45 * (market_profit_rate / 100)) - extra_investment
    resource_income = resource_fee_total
    total_income = commission_income + resource_income
    
    return commission_income, resource_income, total_income