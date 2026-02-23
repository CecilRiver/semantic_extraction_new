#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
边提取器基类
"""

class BaseEdgeExtractor:
    """边提取器基类"""
    
    def get_element_text(self, element, tag_name, default=""):
        """安全获取element中的子标签文本"""
        child = element.find(tag_name)
        return child.text if child is not None and child.text else default
    
    def get_element_attr(self, element, attr_name, default=""):
        """安全获取element的属性"""
        return element.get(attr_name, default)
    
    def get_element_children(self, element, tag_name):
        """获取element中的所有子标签"""
        return element.findall(tag_name)
