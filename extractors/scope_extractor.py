#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Scope字段提取器
Scope ∈ {global, local}
"""

from .base_extractor import BaseExtractor

class ScopeExtractor(BaseExtractor):
    """提取变量的scope字段"""
    
    # 全局变量的后缀标记
    GLOBAL_SUFFIXES = [".DI", ".DV", ".DO", ".AV", ".AI", ".AO", ".PV", ".MV", ".SP"]
    
    def extract(self, element, context):
        """
        提取scope字段
        
        规则：
        - global: 工程点位/跨实体交互变量（包含后缀或@符号）
        - local: 功能块实例端口、内部中间量、常量
        """
        element_type = self.get_element_attr(element, "type")
        text = self.get_element_text(element, "text")
        ttype = self.get_element_text(element, "ttype")
        element_id = self.get_element_text(element, "id")
        
        scope_value = None
        rules = []
        
        # 规则1：常量 → local
        if ttype == "5":
            scope_value = "local"
            rules.append("ttype=5 的常量 → local")
        
        # 规则2：含 @ 的远程点位 → global
        elif "@" in text:
            scope_value = "global"
            rules.append(f'含 "@" 的远程点位 → global')
        
        # 规则3：output类型 → global
        elif element_type == "output":
            scope_value = "global"
            rules.append(f'element type=output → global')
        
        # 规则4：含全局后缀的点位 → global
        else:
            for suffix in self.GLOBAL_SUFFIXES:
                if suffix in text:
                    scope_value = "global"
                    rules.append(f'含 "{suffix}" 后缀的工程点位 → global')
                    break
        
        # 默认规则
        if scope_value is None:
            scope_value = "local"
            rules.append("无明确全局标记 → local (默认)")
        
        # 构建证据
        evidence = {}
        for i, rule in enumerate(rules, 1):
            evidence[f"规则{i if len(rules) > 1 else ''}"] = rule
        
        evidence["证据"] = f"<element type=\"{element_type}\">"
        
        if ttype == "5":
            evidence["常量标记"] = "<ttype>5</ttype>"
        
        return {
            "value": scope_value,
            "evidence": evidence
        }

