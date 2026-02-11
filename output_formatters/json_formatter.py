#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
JSON格式输出格式化器
"""

import json

class JsonFormatter:
    """生成JSON格式输出"""
    
    def format_clean(self, variable_data):
        """
        格式化为干净版JSON
        
        Args:
            variable_data: 变量数据字典
            
        Returns:
            dict: JSON格式的变量数据
        """
        clean_json = {
            "aliases": variable_data.get("aliases", ["", "", ""]),
            "name": variable_data.get("name", ""),
            "type": variable_data.get("type", ""),
            "scope": variable_data.get("scope", ""),
            "attackable": variable_data.get("attackable", False),
            "default_value": variable_data.get("default_value", None),
            "rate": None,  # ∅
            "range": None  # ∅
        }
        return clean_json
    
    def format_with_evidence(self, variable_data, evidence_data):
        """
        格式化为带证据版JSON
        
        Args:
            variable_data: 变量数据字典
            evidence_data: 证据数据字典
            
        Returns:
            dict: JSON格式的变量数据（包含证据）
        """
        evidence_json = {
            "variable": {
                "aliases": variable_data.get("aliases", ["", "", ""]),
                "name": variable_data.get("name", ""),
                "type": variable_data.get("type", ""),
                "scope": variable_data.get("scope", ""),
                "attackable": variable_data.get("attackable", False),
                "default_value": variable_data.get("default_value", None),
                "rate": None,
                "range": None
            },
            "evidence": {
                "e_aliases": evidence_data.get("aliases", {}),
                "e_name": evidence_data.get("name", {}),
                "e_type": evidence_data.get("type", {}),
                "e_scope": evidence_data.get("scope", {}),
                "e_attackable": evidence_data.get("attackable", {}),
                "e_default": evidence_data.get("default_value", {}),
                "e_rate": evidence_data.get("rate", {}),
                "e_range": evidence_data.get("range", {})
            }
        }
        return evidence_json
    
    def save_clean_json(self, variables, output_file):
        """
        保存干净版JSON到文件
        
        Args:
            variables: 变量列表
            output_file: 输出文件路径
        """
        clean_data = []
        for var in variables:
            clean_json = self.format_clean(var["variable_data"])
            clean_data.append(clean_json)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(clean_data, f, ensure_ascii=False, indent=2)
        
        return len(clean_data)
    
    def save_evidence_json(self, variables, output_file):
        """
        保存带证据版JSON到文件
        
        Args:
            variables: 变量列表
            output_file: 输出文件路径
        """
        evidence_data = []
        for var in variables:
            evidence_json = self.format_with_evidence(
                var["variable_data"], 
                var["evidence_data"]
            )
            evidence_data.append(evidence_json)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(evidence_data, f, ensure_ascii=False, indent=2)
        
        return len(evidence_data)

