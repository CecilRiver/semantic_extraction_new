#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Default Value字段提取器
"""

from .base_extractor import BaseExtractor
import re

class DefaultValueExtractor(BaseExtractor):
    """提取变量的default value字段"""
    
    def extract(self, element, context):
        """
        提取default value字段
        
        规则：
        - 常量：值即为默认值
        - 时间字面量：转换为毫秒
        - 其他：为空
        """
        text = self.get_element_text(element, "text")
        ttype = self.get_element_text(element, "ttype")
        
        default_value = None
        evidence_text = ""
        
        # 规则1：常量有默认值
        if ttype == "5":
            # 时间字面量转换
            if text.startswith("T#"):
                default_value = self._parse_time_literal(text)
                evidence_text = f'时间常量转换：{text} → {default_value}毫秒'
            else:
                # 尝试解析为数值
                try:
                    if "." in text:
                        default_value = float(text)
                    else:
                        default_value = int(text)
                    evidence_text = f'常量值即默认值 → {default_value}'
                except ValueError:
                    default_value = text
                    evidence_text = f'常量值 → "{text}"'
        else:
            # 非常量，检查是否有初始化赋值（当前XML中不常见）
            default_value = None
            evidence_text = "无 initialization 或默认值配置 → 空"
        
        # 构建证据
        evidence = {
            "说明": evidence_text,
            "证据": f'<text>{text}</text>' if ttype == "5" else "XML 中未找到初始化赋值"
        }
        
        return {
            "value": default_value,
            "evidence": evidence
        }
    
    def _parse_time_literal(self, time_str):
        """
        解析时间字面量，转换为毫秒
        例如：T#3S → 3000, T#15S → 15000
        """
        # 匹配模式：T#数字单位
        match = re.match(r'T#(\d+(?:\.\d+)?)([A-Za-z]+)', time_str)
        if not match:
            return None
        
        value = float(match.group(1))
        unit = match.group(2).upper()
        
        # 单位转换为毫秒
        unit_map = {
            'MS': 1,
            'S': 1000,
            'M': 60000,
            'H': 3600000,
            'D': 86400000
        }
        
        multiplier = unit_map.get(unit, 1)
        return int(value * multiplier)

