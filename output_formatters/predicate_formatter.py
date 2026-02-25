#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Predicate Formatter - 谓词输出格式化器
"""

import json
from pathlib import Path
from datetime import datetime

class PredicateFormatter:
    """谓词格式化器 - 生成clean和evidence两种版本"""
    
    def format_clean(self, protections, hazards):
        """
        生成clean版本（仅谓词数据）
        
        Args:
            protections: 防护谓词列表 [{"predicate": {...}, "evidence": {...}}, ...]
            hazards: 危害谓词列表
            
        Returns:
            dict: {"P": [...], "H": [...]}
        """
        clean_output = {
            "P": [item["predicate"] for item in protections],
            "H": [item["predicate"] for item in hazards]
        }
        return clean_output
    
    def format_with_evidence(self, protections, hazards):
        """
        生成带证据版本
        
        Args:
            protections: 防护谓词列表
            hazards: 危害谓词列表
            
        Returns:
            dict: {"P": [...], "H": [...]}
        """
        evidence_output = {
            "P": protections,  # 已包含predicate和evidence
            "H": hazards
        }
        return evidence_output
    
    def save_predicates_json(self, protections, hazards, output_dir, file_prefix):
        """
        保存谓词JSON文件（clean + evidence两个版本）
        
        Args:
            protections: 防护谓词列表
            hazards: 危害谓词列表
            output_dir: 输出目录
            file_prefix: 文件前缀（如"10_SCS02"）
            
        Returns:
            tuple: (clean文件路径, evidence文件路径)
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Clean版本
        clean_data = self.format_clean(protections, hazards)
        clean_file = output_path / f"{file_prefix}_predicates_clean.json"
        with open(clean_file, 'w', encoding='utf-8') as f:
            json.dump(clean_data, f, ensure_ascii=False, indent=2)
        
        p_count = len(clean_data["P"])
        h_count = len(clean_data["H"])
        print(f"Clean版已保存到: {clean_file} ({p_count} P, {h_count} H)")
        
        # Evidence版本
        evidence_data = self.format_with_evidence(protections, hazards)
        evidence_file = output_path / f"{file_prefix}_predicates_with_evidence.json"
        with open(evidence_file, 'w', encoding='utf-8') as f:
            json.dump(evidence_data, f, ensure_ascii=False, indent=2)
        
        print(f"Evidence版已保存到: {evidence_file}")
        
        return (str(clean_file), str(evidence_file))
