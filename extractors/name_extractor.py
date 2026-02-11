#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Name字段提取器
格式：控制站_控制程序_变量名
"""

from .base_extractor import BaseExtractor

class NameExtractor(BaseExtractor):
    """提取变量的name字段"""
    
    def extract(self, element, context):
        """
        提取name字段
        
        Args:
            element: XML element
            context: {"station": "10", "program": "SCS02", ...}
            
        Returns:
            {"value": name值, "evidence": 证据信息}
        """
        station = context.get("station", "")
        program = context.get("program", "")
        
        # 获取变量名
        text = self.get_element_text(element, "text")
        element_type = self.get_element_attr(element, "type")
        element_id = self.get_element_text(element, "id")
        ttype = self.get_element_text(element, "ttype")
        
        # 处理常量的特殊命名
        if ttype == "5":
            # 常量：CONST_{text}_id{id}
            # 对特殊字符进行处理
            safe_text = text.replace("#", "").replace(":", "").replace(".", "_")
            variable_name = f"CONST_{safe_text}_id{element_id}"
        else:
            # 普通变量：保持原样
            variable_name = text
        
        # 组合name
        name = f"{station}_{program}_{variable_name}"
        
        # 构建证据
        evidence = {
            "控制站": f'"{station}" ← 文件路径 "input/XML格式控制程序/{station}/..."',
            "控制程序": f'"{program}" ← context.program',
            "变量名": f'"{variable_name}" ← element(id={element_id}).text',
            "组合规则": "控制站_控制程序_变量名"
        }
        
        if ttype == "5":
            evidence["特殊处理"] = f"常量命名规则：CONST_{{text}}_id{{id}}"
        
        return {
            "value": name,
            "evidence": evidence
        }

