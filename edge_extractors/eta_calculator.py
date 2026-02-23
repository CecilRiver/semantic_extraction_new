#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
eta 权重计算器
"""

from .base_edge_extractor import BaseEdgeExtractor
import json

class EtaCalculator(BaseEdgeExtractor):
    """计算边的 eta 权重值"""
    
    def __init__(self, config_path="config/eta_rules.json"):
        """
        初始化计算器
        
        Args:
            config_path: eta规则配置文件路径
        """
        self.config = self._load_config(config_path)
        self.default_eta = self.config.get("default_eta", 1.0)
        self.validation = self.config.get("validation", {"min": 0.0, "max": 1.0})
    
    def _load_config(self, config_path):
        """加载配置文件"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"警告: 配置文件 {config_path} 不存在，使用默认规则")
            return self._get_default_config()
        except json.JSONDecodeError as e:
            print(f"错误: 配置文件格式错误: {e}，使用默认规则")
            return self._get_default_config()
    
    def _get_default_config(self):
        """获取默认配置"""
        return {
            "rules": [
                {
                    "name": "PID控制器",
                    "condition": {"at_type_contains": ["PID"]},
                    "eta": 0.6
                },
                {
                    "name": "限速限幅器",
                    "condition": {"at_type_contains": ["RATE", "SLEW", "LIMIT"]},
                    "eta": 0.8
                }
            ],
            "default_eta": 1.0,
            "validation": {"min": 0.0, "max": 1.0}
        }
    
    def calculate(self, box_element, edge_type):
        """
        计算 eta 值
        
        Args:
            box_element: box类型的element
            edge_type: 边类型（data/guard/call）
            
        Returns:
            dict: {
                "eta": eta值,
                "eps": eps值（固定1.0）,
                "evidence": 计算依据
            }
        """
        at_type = self.get_element_text(box_element, "AT_type", "")
        element_id = self.get_element_text(box_element, "id")
        
        eta = None
        matched_rule = None
        
        # 遍历规则
        for rule in self.config.get("rules", []):
            if self._check_rule_condition(rule, at_type, edge_type):
                eta = rule["eta"]
                matched_rule = rule["name"]
                break
        
        # 使用默认值
        if eta is None:
            eta = self.default_eta
        
        # 验证eta范围
        eta = self._validate_eta(eta)
        
        # 构建证据
        evidence = {}
        if matched_rule:
            evidence["规则"] = f'{matched_rule} → eta={eta}'
            evidence["AT_type"] = at_type
            evidence["来源"] = "config/eta_rules.json"
        else:
            evidence["规则"] = f'AT_type="{at_type}" 无匹配规则，使用默认值 → eta={eta}'
            evidence["来源"] = "默认规则"
        
        return {
            "eta": eta,
            "eps": 1.0,  # 固定值
            "evidence": evidence
        }
    
    def _check_rule_condition(self, rule, at_type, edge_type):
        """检查规则条件是否满足"""
        condition = rule.get("condition", {})
        
        # 检查 at_type_contains
        if "at_type_contains" in condition:
            keywords = condition["at_type_contains"]
            for keyword in keywords:
                if keyword in at_type:
                    return True
        
        # 检查 at_type_starts_with
        if "at_type_starts_with" in condition:
            prefixes = condition["at_type_starts_with"]
            for prefix in prefixes:
                if at_type.startswith(prefix):
                    return True
        
        # 检查 edge_type
        if "edge_type" in condition:
            required_types = condition["edge_type"]
            if edge_type in required_types:
                return True
        
        return False
    
    def _validate_eta(self, eta):
        """验证eta值范围"""
        min_val = self.validation.get("min", 0.0)
        max_val = self.validation.get("max", 1.0)
        
        if eta < min_val:
            print(f"警告: eta={eta} < {min_val}，使用最小值")
            return min_val
        
        if eta > max_val:
            print(f"警告: eta={eta} > {max_val}，使用最大值")
            return max_val
        
        return eta
