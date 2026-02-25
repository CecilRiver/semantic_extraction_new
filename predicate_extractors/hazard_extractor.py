#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Hazard Extractor - 危害谓词提取器
"""

from .base_predicate_extractor import BasePredicateExtractor
from .pattern_matcher import PatternMatcher
import re

class HazardExtractor(BasePredicateExtractor):
    """危害谓词提取器"""
    
    # 危害关键词
    HAZARD_KEYWORDS = ["高", "低", "超限", "跳闸", "过", "欠", "保护", "报警", "故障"]
    
    def __init__(self):
        super().__init__()
        self.pattern_matcher = PatternMatcher()
        self.hazard_counter = 1
    
    def extract_hazards(self, elements, context):
        """
        提取危害谓词
        
        Args:
            elements: XML element列表
            context: 上下文
            
        Returns:
            list: 危害谓词列表 [{"predicate": {...}, "evidence": {...}}, ...]
        """
        # 初始化
        self.pattern_matcher.build_element_dict(elements)
        self.pattern_matcher.build_variable_dict(elements, context)
        self.element_dict = self.pattern_matcher.element_dict
        self.variable_dict = self.pattern_matcher.variable_dict
        
        hazards = []
        
        # 从阈值模式中提取危害谓词
        threshold_patterns = self.pattern_matcher.find_threshold_patterns()
        for pattern in threshold_patterns:
            if self._is_hazard_pattern(pattern):
                hazard = self._build_hazard_from_threshold(pattern, context)
                if hazard:
                    hazards.append(hazard)
        
        # 从3取2投票逻辑中提取危害谓词
        voting_hazards = self._extract_voting_hazards(elements, context)
        hazards.extend(voting_hazards)
        
        return hazards
    
    def _is_hazard_pattern(self, pattern):
        """判断是否是危害模式（通过Comment关键词）"""
        cmp_element = self.element_dict.get(pattern["cmp_id"])
        if not cmp_element:
            return False
        
        comment = self.get_element_text(cmp_element, "Comment")
        
        # 检查是否包含危害关键词
        for keyword in self.HAZARD_KEYWORDS:
            if keyword in comment:
                return True
        
        # 检查变量的Comment
        var_element = self.element_dict.get(pattern["var_id"])
        if var_element:
            var_comment = self.get_element_text(var_element, "Comment")
            for keyword in self.HAZARD_KEYWORDS:
                if keyword in var_comment:
                    return True
        
        return False
    
    def _build_hazard_from_threshold(self, pattern, context):
        """从阈值模式构建危害谓词"""
        cmp_id = pattern["cmp_id"]
        var_id = pattern["var_id"]
        threshold_id = pattern["threshold_id"]
        cmp_op = pattern["cmp_operator"]
        
        # 解析变量名
        var_evidence = {}
        var_name = self.resolve_variable_name(var_id, var_evidence)
        
        # 解析阈值
        threshold_element = self.element_dict.get(threshold_id)
        threshold_text = self.get_element_text(threshold_element, "text")
        try:
            threshold_value = float(threshold_text)
        except:
            return None
        
        # 生成ID和name
        cmp_element = self.element_dict.get(cmp_id)
        comment = self.get_element_text(cmp_element, "Comment")
        
        hazard_id = self._generate_hazard_id(comment, var_name)
        hazard_name = self._extract_hazard_name(comment, var_name)
        
        # 构建谓词对象
        predicate = {
            "id": hazard_id,
            "name": hazard_name,
            "kind": "threshold",
            "var": var_name,
            "cmp": cmp_op,
            "threshold": threshold_value
        }
        
        # 构建证据
        evidence = {
            "pattern_type": "threshold",
            "comparison_element": cmp_id,
            "var_element": var_id,
            "threshold_element": threshold_id,
            "var_evidence": var_evidence,
            "comment": comment,
            "classification_reason": "comment_keyword"
        }
        
        return {
            "predicate": predicate,
            "evidence": evidence
        }
    
    def _extract_voting_hazards(self, elements, context):
        """提取3取2投票逻辑的危害谓词"""
        hazards = []
        
        for element in elements:
            if self.get_element_attr(element, "type") != "box":
                continue
            
            at_type = self.get_element_text(element, "AT_type")
            if at_type != "HS3SEL2":
                continue
            
            element_id = self.get_element_text(element, "id")
            comment = self.get_element_text(element, "Comment")
            
            # 检查是否包含危害关键词
            is_hazard = False
            for keyword in self.HAZARD_KEYWORDS:
                if keyword in comment:
                    is_hazard = True
                    break
            
            if not is_hazard:
                continue
            
            # 获取投票逻辑的输入
            inputs = self.get_element_children(element, "input")
            input_ids = [inp.get("inputid", "") for inp in inputs if inp.get("inputid", "") != "0"]
            
            if len(input_ids) != 3:
                continue
            
            # 解析变量名
            var_names = []
            for inp_id in input_ids:
                var_name = self.resolve_variable_name(inp_id)
                var_names.append(var_name)
            
            # 生成ID和name
            hazard_id = self._generate_hazard_id(comment, var_names[0])
            hazard_name = self._extract_hazard_name(comment, var_names[0])
            
            # 构建谓词对象（使用第一个变量作为代表）
            predicate = {
                "id": hazard_id,
                "name": hazard_name,
                "kind": "threshold",
                "var": var_names[0],
                "cmp": "==",
                "threshold": True,
                "voting_logic": "3_out_of_2",
                "voting_inputs": var_names
            }
            
            evidence = {
                "pattern_type": "voting_logic",
                "voting_element": element_id,
                "voting_type": "HS3SEL2",
                "input_elements": input_ids,
                "comment": comment,
                "classification_reason": "comment_keyword"
            }
            
            hazards.append({
                "predicate": predicate,
                "evidence": evidence
            })
        
        return hazards
    
    def _generate_hazard_id(self, comment, var_name):
        """生成危害谓词ID"""
        # 从comment中提取描述
        description = self._extract_description_from_comment(comment)
        if not description:
            # 从变量名中提取
            description = self._extract_description_from_varname(var_name)
        
        hazard_id = f"H{self.hazard_counter}_{description}"
        self.hazard_counter += 1
        return hazard_id
    
    def _extract_hazard_name(self, comment, var_name):
        """提取危害谓词名称（优先使用Comment）"""
        if comment:
            return comment
        
        # 降级：使用变量名
        return var_name
    
    def _extract_description_from_comment(self, comment):
        """从Comment中提取英文描述"""
        if not comment:
            return ""
        
        # 简单映射
        mapping = {
            "压力": "pressure",
            "温度": "temperature",
            "流量": "flow",
            "液位": "level",
            "高": "high",
            "低": "low",
            "主汽": "main_steam",
            "给水": "feedwater",
            "燃料": "fuel",
            "跳闸": "trip"
        }
        
        parts = []
        for cn, en in mapping.items():
            if cn in comment:
                parts.append(en)
        
        if parts:
            return "_".join(parts)
        
        return "hazard"
    
    def _extract_description_from_varname(self, var_name):
        """从变量名中提取描述"""
        # 简化处理：使用变量名的最后一部分
        if "_" in var_name:
            parts = var_name.split("_")
            return parts[-1].lower()
        return "hazard"
