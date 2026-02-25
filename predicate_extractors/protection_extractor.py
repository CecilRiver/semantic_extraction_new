#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Protection Extractor - 防护谓词提取器
"""

from .base_predicate_extractor import BasePredicateExtractor
from .pattern_matcher import PatternMatcher

class ProtectionExtractor(BasePredicateExtractor):
    """防护谓词提取器"""
    
    # 防护关键词
    PROTECTION_KEYWORDS = ["切手动", "自动切手动", "主控", "手动", "切换"]
    
    def __init__(self):
        super().__init__()
        self.pattern_matcher = PatternMatcher()
        self.protection_counter = 1
    
    def extract_protections(self, elements, context):
        """
        提取防护谓词
        
        Args:
            elements: XML element列表
            context: 上下文
            
        Returns:
            list: 防护谓词列表 [{"predicate": {...}, "evidence": {...}}, ...]
        """
        # 初始化
        self.pattern_matcher.build_element_dict(elements)
        self.pattern_matcher.build_variable_dict(elements, context)
        self.element_dict = self.pattern_matcher.element_dict
        self.variable_dict = self.pattern_matcher.variable_dict
        
        protections = []
        
        # 从偏差模式中提取防护谓词
        deviation_patterns = self.pattern_matcher.find_deviation_patterns()
        for pattern in deviation_patterns:
            protection = self._build_protection_from_deviation(pattern, context)
            if protection:
                protections.append(protection)
        
        # 从阈值模式中提取防护谓词（带防护关键词的）
        threshold_patterns = self.pattern_matcher.find_threshold_patterns()
        for pattern in threshold_patterns:
            if self._is_protection_pattern(pattern):
                protection = self._build_protection_from_threshold(pattern, context)
                if protection:
                    protections.append(protection)
        
        return protections
    
    def _build_protection_from_deviation(self, pattern, context):
        """从偏差模式构建防护谓词"""
        sub_id = pattern["sub_id"]
        abs_id = pattern["abs_id"]
        cmp_id = pattern["cmp_id"]
        ref_var_id = pattern["ref_var_id"]
        proc_var_id = pattern["proc_var_id"]
        delta_id = pattern["delta_id"]
        cmp_op = pattern["cmp_operator"]
        
        # 解析变量名
        ref_var_evidence = {}
        ref_var_name = self.resolve_variable_name(ref_var_id, ref_var_evidence)
        
        proc_var_evidence = {}
        proc_var_name = self.resolve_variable_name(proc_var_id, proc_var_evidence)
        
        # 解析delta值
        delta_element = self.element_dict.get(delta_id)
        delta_text = self.get_element_text(delta_element, "text")
        try:
            delta_value = float(delta_text)
        except:
            return None
        
        # 提取guards
        guards = self._extract_guards_for_pattern(cmp_id)
        
        # 生成ID和name
        cmp_element = self.element_dict.get(cmp_id)
        comment = self.get_element_text(cmp_element, "Comment")
        
        protection_id = self._generate_protection_id(comment, ref_var_name)
        protection_name = self._extract_protection_name(comment, ref_var_name)
        
        # 构建谓词对象
        predicate = {
            "id": protection_id,
            "name": protection_name,
            "kind": "deviation",
            "ref_var": ref_var_name,
            "proc_var": proc_var_name,
            "cmp": cmp_op,
            "delta": delta_value,
            "guards": guards
        }
        
        # 构建证据
        evidence = {
            "pattern_type": "deviation",
            "sub_element": sub_id,
            "abs_element": abs_id,
            "gt_element": cmp_id,
            "ref_var_evidence": ref_var_evidence,
            "proc_var_evidence": proc_var_evidence,
            "delta_element": delta_id,
            "guards_evidence": []
        }
        
        return {
            "predicate": predicate,
            "evidence": evidence
        }
    
    def _build_protection_from_threshold(self, pattern, context):
        """从阈值模式构建防护谓词"""
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
        
        protection_id = self._generate_protection_id(comment, var_name)
        protection_name = self._extract_protection_name(comment, var_name)
        
        # 构建谓词对象
        predicate = {
            "id": protection_id,
            "name": protection_name,
            "kind": "threshold",
            "var": var_name,
            "cmp": cmp_op,
            "threshold": threshold_value,
            "guards": []
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
    
    def _is_protection_pattern(self, pattern):
        """判断是否是防护模式（通过Comment关键词）"""
        cmp_element = self.element_dict.get(pattern["cmp_id"])
        if not cmp_element:
            return False
        
        comment = self.get_element_text(cmp_element, "Comment")
        
        # 检查是否包含防护关键词
        for keyword in self.PROTECTION_KEYWORDS:
            if keyword in comment:
                return True
        
        return False
    
    def _extract_guards_for_pattern(self, cmp_id):
        """提取guards"""
        guard_patterns = self.pattern_matcher.extract_guards(cmp_id)
        
        guards = []
        for guard_pattern in guard_patterns:
            var_id = guard_pattern["var_id"]
            threshold_id = guard_pattern["threshold_id"]
            cmp_op = guard_pattern["cmp_operator"]
            
            # 解析变量名
            var_name = self.resolve_variable_name(var_id)
            
            # 解析阈值
            threshold_element = self.element_dict.get(threshold_id)
            threshold_text = self.get_element_text(threshold_element, "text")
            try:
                threshold_value = float(threshold_text)
            except:
                continue
            
            guards.append({
                "kind": "threshold",
                "var": var_name,
                "cmp": cmp_op,
                "threshold": threshold_value
            })
        
        return guards
    
    def _generate_protection_id(self, comment, var_name):
        """生成防护谓词ID"""
        description = self._extract_description_from_comment(comment)
        if not description:
            description = self._extract_description_from_varname(var_name)
        
        protection_id = f"P{self.protection_counter}_{description}"
        self.protection_counter += 1
        return protection_id
    
    def _extract_protection_name(self, comment, var_name):
        """提取防护谓词名称"""
        if comment:
            return comment
        return var_name
    
    def _extract_description_from_comment(self, comment):
        """从Comment中提取英文描述"""
        if not comment:
            return ""
        
        mapping = {
            "汽机": "turbine",
            "锅炉": "boiler",
            "主控": "master",
            "切手动": "to_manual",
            "自动": "auto",
            "压力": "pressure",
            "燃料": "fuel",
            "给水": "feedwater"
        }
        
        parts = []
        for cn, en in mapping.items():
            if cn in comment:
                parts.append(en)
        
        if parts:
            return "_".join(parts)
        
        return "protection"
    
    def _extract_description_from_varname(self, var_name):
        """从变量名中提取描述"""
        if "_" in var_name:
            parts = var_name.split("_")
            return parts[-1].lower()
        return "protection"
