#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Base Predicate Extractor - 基础谓词提取器
"""

class BasePredicateExtractor:
    """谓词提取器基类"""
    
    def __init__(self):
        self.element_dict = {}  # id -> element 映射
        self.variable_dict = {}  # id -> variable name 映射
    
    def get_element_text(self, element, tag, default=""):
        """
        获取元素的子标签文本
        
        Args:
            element: XML element
            tag: 子标签名
            default: 默认值
            
        Returns:
            str: 标签文本或默认值
        """
        child = element.find(tag)
        if child is not None and child.text:
            return child.text.strip()
        return default
    
    def get_element_attr(self, element, attr, default=""):
        """
        获取元素的属性
        
        Args:
            element: XML element
            attr: 属性名
            default: 默认值
            
        Returns:
            str: 属性值或默认值
        """
        return element.get(attr, default)
    
    def get_element_children(self, element, tag):
        """
        获取元素的所有指定子元素
        
        Args:
            element: XML element
            tag: 子标签名
            
        Returns:
            list: 子元素列表
        """
        return element.findall(tag)
    
    def resolve_variable_name(self, element_id, evidence=None):
        """
        解析变量名
        
        Args:
            element_id: 元素ID
            evidence: 证据字典（可选，用于记录解析方法）
            
        Returns:
            str: 变量名
        """
        if element_id in self.variable_dict:
            var_name = self.variable_dict[element_id]
            if evidence is not None:
                evidence['resolution'] = 'variable_dict'
                evidence['var_name'] = var_name
            return var_name
        
        # 降级：尝试从element_dict获取text
        if element_id in self.element_dict:
            element = self.element_dict[element_id]
            text = self.get_element_text(element, "text")
            if text:
                if evidence is not None:
                    evidence['resolution'] = 'fallback_text'
                    evidence['source_text'] = text
                return text
        
        # 最终降级：使用UNRESOLVED前缀
        fallback_name = f"UNRESOLVED_{element_id}"
        if evidence is not None:
            evidence['resolution'] = 'unresolved'
            evidence['fallback_name'] = fallback_name
        return fallback_name
