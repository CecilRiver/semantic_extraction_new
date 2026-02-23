#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
边类型分类器 - 将边分类为 data/guard/call
"""

from .base_edge_extractor import BaseEdgeExtractor
import json
from pathlib import Path

class TypeClassifier(BaseEdgeExtractor):
    """边类型分类器"""
    
    def __init__(self, config_path="config/at_type_mapping.json"):
        """
        初始化分类器
        
        Args:
            config_path: 配置文件路径
        """
        self.config = self._load_config(config_path)
        self.mapping_cache = {}  # 缓存映射结果
    
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
            "mappings": {
                "LOGICAL_OPERATORS": {
                    "types": ["AND", "OR", "NOT", "XOR"],
                    "edge_type": "guard",
                    "eta": 1.0
                },
                "COMPARISON_OPERATORS": {
                    "types": ["LT", "GT", "LE", "GE", "EQ", "NE"],
                    "edge_type": "guard",
                    "eta": 1.0
                }
            },
            "default": {
                "edge_type": "call",
                "eta": 1.0
            }
        }
    
    def classify(self, box_element):
        """
        分类边类型
        
        Args:
            box_element: box类型的element
            
        Returns:
            dict: {
                "type": "call"|"guard"|"data",
                "evidence": 分类依据
            }
        """
        at_type = self.get_element_text(box_element, "AT_type", "")
        typetext = self.get_element_text(box_element, "typetext", "")
        isinst = self.get_element_text(box_element, "isinst", "")
        element_id = self.get_element_text(box_element, "id")
        
        edge_type = None
        rules = []
        
        # 规则1: isinst=TRUE → call（功能块实例）
        if isinst == "TRUE":
            edge_type = "call"
            rules.append("isinst=TRUE 的功能块实例 → call")
        
        # 规则2: 基于 AT_type 精确匹配
        if edge_type is None:
            for group_name, group_config in self.config.get("mappings", {}).items():
                # 精确匹配
                if "types" in group_config:
                    if at_type in group_config["types"]:
                        edge_type = group_config["edge_type"]
                        rules.append(f'AT_type="{at_type}" ∈ {group_name} → {edge_type}')
                        break
                
                # 模式匹配
                if "patterns" in group_config:
                    for pattern in group_config["patterns"]:
                        if self._match_pattern(at_type, pattern):
                            edge_type = group_config["edge_type"]
                            rules.append(f'AT_type="{at_type}" 匹配模式 "{pattern}" → {edge_type}')
                            break
                
                if edge_type:
                    break
        
        # 规则3: 基于 typetext
        if edge_type is None:
            if typetext == "BT_FB":
                edge_type = "call"
                rules.append("typetext=BT_FB（功能块）→ call")
            elif typetext == "BT_OPERATOR":
                # 无法判断是逻辑还是算术，默认为guard
                edge_type = "guard"
                rules.append("typetext=BT_OPERATOR，AT_type未知 → guard (默认)")
        
        # 规则4: 默认分类
        if edge_type is None:
            edge_type = self.config.get("default", {}).get("edge_type", "call")
            rules.append(f'AT_type="{at_type}" 未知，使用默认分类 → {edge_type}')
        
        # 构建证据
        evidence = {
            "规则": "; ".join(rules),
            "AT_type": at_type,
            "typetext": typetext,
            "isinst": isinst,
            "element_id": element_id
        }
        
        return {
            "type": edge_type,
            "evidence": evidence
        }
    
    def _match_pattern(self, text, pattern):
        """
        简单的模式匹配
        
        支持：
        - * 通配符（如 "PID*", "*RATE*"）
        """
        if "*" not in pattern:
            return text == pattern
        
        # 处理通配符
        if pattern.startswith("*") and pattern.endswith("*"):
            # *XXX* - 包含
            keyword = pattern[1:-1]
            return keyword in text
        elif pattern.startswith("*"):
            # *XXX - 结尾
            suffix = pattern[1:]
            return text.endswith(suffix)
        elif pattern.endswith("*"):
            # XXX* - 开头
            prefix = pattern[:-1]
            return text.startswith(prefix)
        
        return False
