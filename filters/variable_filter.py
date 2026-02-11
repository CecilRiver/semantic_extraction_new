#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
变量过滤器 - 判断哪些变量需要记录为变量字典
"""

class VariableFilter:
    """判断element是否需要提取为变量"""
    
    # 工程点位的后缀标记
    ENGINEERING_SUFFIXES = [".DI", ".DV", ".DO", ".AV", ".AI", ".AO", ".PV", ".MV", ".SP"]
    
    def should_extract(self, element):
        """
        判断element是否需要提取
        
        规则：
        1. <element type="input|output"> 中的 <text>，
           且 <text> 表示工程点位/信号（含 .DI/.DV/.AV 或含 @）
        2. <element type="input"> 且 <ttype>=5，
           <text> 为数字常量或时间字面量（如 80、T#15S）
        
        Args:
            element: XML element对象
            
        Returns:
            dict: {
                "should_extract": bool,
                "reason": str,  # 原因说明
                "category": str  # 变量类别：engineering_point, constant, skip
            }
        """
        element_type = element.get("type", "")
        
        # 只处理 input 和 output 类型
        if element_type not in ["input", "output"]:
            return {
                "should_extract": False,
                "reason": f"元素类型为 '{element_type}'，非 input/output",
                "category": "skip"
            }
        
        # 获取关键字段
        text_elem = element.find("text")
        ttype_elem = element.find("ttype")
        
        text = text_elem.text if text_elem is not None and text_elem.text else ""
        ttype = ttype_elem.text if ttype_elem is not None and ttype_elem.text else ""
        
        if not text:
            return {
                "should_extract": False,
                "reason": "<text> 为空",
                "category": "skip"
            }
        
        # 规则1：工程点位（含后缀或@符号）
        is_engineering_point = self._is_engineering_point(text)
        if is_engineering_point:
            return {
                "should_extract": True,
                "reason": f"工程点位/信号：text='{text}'",
                "category": "engineering_point"
            }
        
        # 规则2：常量（ttype=5）
        if ttype == "5":
            return {
                "should_extract": True,
                "reason": f"常量：ttype=5, text='{text}'",
                "category": "constant"
            }
        
        # 不符合任何提取规则
        return {
            "should_extract": False,
            "reason": f"不符合提取规则：text='{text}', ttype='{ttype}'",
            "category": "skip"
        }
    
    def _is_engineering_point(self, text):
        """
        判断是否为工程点位
        
        规则：
        - 包含工程后缀（.DI, .DV, .AV等）
        - 包含 @ 符号（远程点位）
        """
        # 检查后缀
        for suffix in self.ENGINEERING_SUFFIXES:
            if suffix in text:
                return True
        
        # 检查 @ 符号
        if "@" in text:
            return True
        
        return False
    
    def get_filter_statistics(self, elements):
        """
        获取过滤统计信息
        
        Args:
            elements: XML element列表
            
        Returns:
            dict: 统计信息
        """
        stats = {
            "total": len(elements),
            "engineering_point": 0,
            "constant": 0,
            "skip": 0,
            "extracted": 0
        }
        
        for element in elements:
            result = self.should_extract(element)
            stats[result["category"]] += 1
            if result["should_extract"]:
                stats["extracted"] += 1
        
        return stats

