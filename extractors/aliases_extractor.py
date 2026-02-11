#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Aliases字段提取器
格式：{ text, Comment, Alias }
"""

from .base_extractor import BaseExtractor

class AliasesExtractor(BaseExtractor):
    """提取变量的aliases字段"""
    
    def extract(self, element, context):
        """
        提取aliases字段
        
        Returns:
            {"value": [text, comment, alias], "evidence": 证据信息}
        """
        element_type = self.get_element_attr(element, "type")
        element_id = self.get_element_text(element, "id")
        
        # 提取三个别名
        text = self.get_element_text(element, "text", "")
        comment = self.get_element_text(element, "Comment", "")
        alias = self.get_element_text(element, "Alias", "")
        
        # 过滤Comment中的特殊标记（如 @5432@）
        if comment.startswith("@") and comment.endswith("@"):
            comment = ""  # 特殊编码，不作为描述
        
        # 构建aliases列表，去掉尾部的空字符串
        aliases_list = [text, comment, alias]
        
        # 去掉尾部的空字符串，保持至少有一个元素（text）
        while len(aliases_list) > 1 and aliases_list[-1] == "":
            aliases_list.pop()
        
        # 构建证据
        evidence = {}
        evidence[f'"{text}"'] = f"← element(type={element_type}, id={element_id}).text"
        
        if comment or len(aliases_list) > 1:
            evidence[f'"{comment}"'] = f"← element(type={element_type}, id={element_id}).Comment"
        
        if alias or len(aliases_list) > 2:
            evidence[f'"{alias}"'] = f"← element(type={element_type}, id={element_id}).Alias"
        
        if not comment and not alias:
            evidence["备注"] = "Comment和Alias字段不存在，已省略"
        elif not alias:
            evidence["备注"] = "Alias字段不存在，已省略"
        
        return {
            "value": aliases_list,
            "evidence": evidence
        }

