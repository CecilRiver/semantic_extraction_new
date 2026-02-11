#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Range字段提取器
"""

from .base_extractor import BaseExtractor

class RangeExtractor(BaseExtractor):
    """提取变量的range字段"""
    
    def extract(self, element, context):
        """
        提取range字段
        
        规则：仅当存在显式限制时填写，否则为 ∅
        注意：注释中的阈值属于谓词阈值，不应写入变量range
        """
        text = self.get_element_text(element, "text")
        comment = self.get_element_text(element, "Comment", "")
        var_type = context.get("type", "")
        
        range_value = None  # ∅
        evidence_text = "无显式 range 声明 → ∅"
        
        # 可以添加备注说明隐含范围
        notes = []
        if var_type == "bool":
            notes.append("bool 类型隐含 {0,1}，但无显式声明")
        elif var_type in ["int", "real"]:
            notes.append(f"{var_type} 类型可能有物理范围，但 XML 中未声明")
        
        if notes:
            evidence_text += "\n备注：" + "; ".join(notes)
        
        evidence = {
            "说明": evidence_text,
            "证据": "XML 中未找到 range 配置"
        }
        
        # 注意：Comment中的数值（如"压力低80"）是谓词阈值，不是变量range
        if comment and any(char.isdigit() for char in comment):
            evidence["重要提示"] = "Comment 中的数值属于谓词阈值，不应写入变量 range"
        
        return {
            "value": range_value,
            "evidence": evidence
        }

