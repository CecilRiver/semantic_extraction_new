#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Type字段提取器
Type ∈ {bool, int, real}
"""

from .base_extractor import BaseExtractor
import re

class TypeExtractor(BaseExtractor):
    """提取变量的type字段"""
    
    # 后缀到类型的映射
    SUFFIX_TYPE_MAP = {
        ".DI": "bool",
        ".DV": "bool",
        ".DO": "bool",
        ".AV": "real",
        ".AI": "real",
        ".AO": "real",
        ".PV": "real",
        ".MV": "real",
        ".SP": "real",
    }
    
    def extract(self, element, context):
        """
        提取type字段
        
        优先级：
        T1: 点位后缀规则（最高优先级）
        T2: 常量规则
        T3: 其它工程类型
        """
        text = self.get_element_text(element, "text")
        ttype = self.get_element_text(element, "ttype")
        element_id = self.get_element_text(element, "id")
        
        type_value = None
        rule = None
        evidence_detail = None
        
        # T1: 点位后缀规则（优先级最高）
        for suffix, type_name in self.SUFFIX_TYPE_MAP.items():
            if suffix in text:
                type_value = type_name
                rule = "T1-后缀规则（优先级最高）"
                evidence_detail = f'后缀 "{suffix}" → {type_name}'
                break
        
        # T2: 常量规则
        if type_value is None and ttype == "5":
            type_value, rule, evidence_detail = self._parse_constant_type(text)
        
        # T3: 默认规则（如果都没匹配到）
        if type_value is None:
            type_value = "bool"  # 默认
            rule = "T3-默认规则"
            evidence_detail = f"无法从后缀判断，默认为 bool"
        
        # 构建证据
        evidence = {
            "规则": rule,
            "判断条件": evidence_detail,
            "证据": f'text="{text}"'
        }
        
        if ttype == "5":
            evidence["常量标记"] = f"<ttype>5</ttype>"
        
        return {
            "value": type_value,
            "evidence": evidence
        }
    
    def _parse_constant_type(self, text):
        """解析常量类型"""
        # 时间字面量：T#...
        if text.startswith("T#"):
            return "int", "T2-常量规则（时间字面量）", f'时间常量 "{text}" → int (转换为毫秒)'
        
        # 浮点数
        if "." in text:
            try:
                float(text)
                return "real", "T2-常量规则（浮点数）", f'浮点字面量 "{text}" → real'
            except ValueError:
                pass
        
        # 整数
        try:
            int(text)
            return "int", "T2-常量规则（整数）", f'整数字面量 "{text}" → int'
        except ValueError:
            pass
        
        # 无法判断
        return "int", "T2-常量规则（默认）", f'常量 "{text}" 无法明确判断，默认 → int'

