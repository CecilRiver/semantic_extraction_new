#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
提取器基类
"""

class BaseExtractor:
    """提取器基类，定义通用接口"""
    
    def extract(self, element, context):
        """
        提取字段值
        
        Args:
            element: XML element对象
            context: 上下文信息（控制站、控制程序等）
            
        Returns:
            dict: {"value": 字段值, "evidence": 证据信息}
        """
        raise NotImplementedError("子类必须实现extract方法")
    
    def get_element_text(self, element, tag_name, default=""):
        """安全获取element中的子标签文本"""
        child = element.find(tag_name)
        return child.text if child is not None and child.text else default
    
    def get_element_attr(self, element, attr_name, default=""):
        """安全获取element的属性"""
        return element.get(attr_name, default)

