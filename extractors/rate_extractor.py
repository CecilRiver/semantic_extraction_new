#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Rate字段提取器
"""

from .base_extractor import BaseExtractor

class RateExtractor(BaseExtractor):
    """提取变量的rate字段"""
    
    def extract(self, element, context):
        """
        提取rate字段
        
        规则：仅当存在显式限制时填写，否则为 ∅
        """
        # 当前XML格式中没有显式的rate信息
        # 可能需要从POUCycle或其他工程配置推断
        
        pou_cycle = context.get("pou_cycle", None)
        
        rate_value = None  # ∅
        evidence_text = "无显式 rate 声明 → ∅"
        
        # 如果有POUCycle信息，可以作为参考
        if pou_cycle:
            evidence_text += f"\n备注：可能需要从工程配置或 POUCycle={pou_cycle}ms 推断"
        
        evidence = {
            "说明": evidence_text,
            "证据": "XML 中未找到 rate 配置"
        }
        
        return {
            "value": rate_value,
            "evidence": evidence
        }

