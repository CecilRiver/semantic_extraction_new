#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Attackable字段提取器
Attackable ∈ {true, false}
"""

from .base_extractor import BaseExtractor

class AttackableExtractor(BaseExtractor):
    """提取变量的attackable字段"""
    
    # 可攻击的关键词（命令/设定类）
    ATTACKABLE_KEYWORDS = [
        "启动", "停止", "设定", "指令", "给定", "输出",
        "开启", "关闭", "投入", "切除", "复位", "确认",
        "开", "关", "增", "减", "调节"
    ]
    
    # 不可攻击的关键词（测量/状态类）
    NON_ATTACKABLE_KEYWORDS = [
        "运行", "状态", "反馈", "温度", "压力", "测量",
        "流量", "液位", "位置", "检测", "监测", "信号",
        "故障", "报警", "就地", "跳闸"
    ]
    
    # 可攻击的后缀（命令类输出）
    ATTACKABLE_SUFFIXES = [".DI", ".DO", ".AO"]
    
    # 不可攻击的后缀（测量/状态类输入）
    NON_ATTACKABLE_SUFFIXES = [".AV", ".AI", ".DV"]
    
    def extract(self, element, context):
        """
        提取attackable字段
        
        规则：
        - true: 命令/设定/可写输出等
        - false: 测量/状态/条件/内部量等
        """
        element_type = self.get_element_attr(element, "type")
        text = self.get_element_text(element, "text")
        comment = self.get_element_text(element, "Comment", "")
        ttype = self.get_element_text(element, "ttype")
        
        attackable_value = None
        rules = []
        
        # 规则1：常量 → false
        if ttype == "5":
            attackable_value = False
            rules.append("常量不可被攻击 → false")
        
        # 规则2：根据Comment关键词判断
        elif comment:
            # 检查可攻击关键词
            for keyword in self.ATTACKABLE_KEYWORDS:
                if keyword in comment:
                    attackable_value = True
                    rules.append(f'Comment 含关键词 "{keyword}" → true')
                    break
            
            # 检查不可攻击关键词
            if attackable_value is None:
                for keyword in self.NON_ATTACKABLE_KEYWORDS:
                    if keyword in comment:
                        attackable_value = False
                        rules.append(f'Comment 含 "{keyword}" (状态词) → false')
                        break
        
        # 规则3：根据element type判断
        if attackable_value is None:
            if element_type == "output":
                # output且没有明确状态词，倾向于可攻击
                for suffix in self.ATTACKABLE_SUFFIXES:
                    if suffix in text:
                        attackable_value = True
                        rules.append(f'type=output 且为命令点位 ({suffix}) → true')
                        break
            elif element_type == "input":
                # input倾向于不可攻击（状态反馈）
                for suffix in self.NON_ATTACKABLE_SUFFIXES:
                    if suffix in text:
                        attackable_value = False
                        rules.append(f'type=input 且为状态反馈 ({suffix}) → false')
                        break
        
        # 规则4：默认规则（保守策略）
        if attackable_value is None:
            if element_type == "output":
                attackable_value = True
                rules.append("type=output，默认 → true (保守策略)")
            else:
                attackable_value = False
                rules.append("type=input，默认 → false (保守策略)")
        
        # 构建证据
        evidence = {}
        for i, rule in enumerate(rules, 1):
            evidence[f"规则{i if len(rules) > 1 else ''}"] = rule
        
        if comment:
            evidence["证据"] = f'<Comment>{comment}</Comment>'
        else:
            evidence["证据"] = f'element type={element_type}'
        
        return {
            "value": attackable_value,
            "evidence": evidence
        }

