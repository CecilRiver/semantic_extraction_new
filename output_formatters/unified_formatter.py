#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Unified Formatter - 统一输出格式化器
将变量、图、谓词整合到单个 JSON 文件
"""

import json
from pathlib import Path
from datetime import datetime

class UnifiedFormatter:
    """统一格式化器 - 生成 D/G/P/H 统一输出"""
    
    def _deduplicate_by_name(self, vars_list):
        """
        简单去重 - 保留第一个出现的记录
        
        Args:
            vars_list: 变量列表
            
        Returns:
            list: 去重后的变量列表
        """
        seen = set()
        result = []
        duplicates_found = 0
        
        for var in vars_list:
            name = var.get('name')
            if name not in seen:
                seen.add(name)
                result.append(var)
            else:
                duplicates_found += 1
        
        if duplicates_found > 0:
            print(f"  [警告] UnifiedFormatter检测到 {duplicates_found} 个重复变量（已去重）")
        
        return result
    
    def format_clean(self, variables, edges, protections, hazards, metadata=None):
        """
        生成 clean 版本统一输出
        
        Args:
            variables: 变量列表（可能是嵌套或扁平结构）
            edges: 边列表（可能是嵌套或扁平结构）
            protections: 防护谓词列表（可能是嵌套或扁平结构）
            hazards: 危害谓词列表（可能是嵌套或扁平结构）
            metadata: 可选的元数据
            
        Returns:
            dict: {"D": {"vars": []}, "G": {"edges": []}, "P": [], "H": []}
        """
        # 扁平化变量数据
        vars_clean = []
        for item in variables:
            if isinstance(item, dict):
                if "variable_data" in item:
                    # 嵌套结构，提取 variable_data
                    vars_clean.append(item["variable_data"])
                else:
                    # 已经是扁平结构
                    vars_clean.append(item)
            else:
                vars_clean.append(item)
        
        # 扁平化边数据
        edges_clean = []
        for item in edges:
            if isinstance(item, dict):
                # 边数据可能是 {"edge": {...}} 或 {"variable_data": {...}, "evidence_data": {...}} 格式
                if "edge" in item:
                    # 格式1: {"edge": {...}, "evidence": {...}}
                    edges_clean.append(item["edge"])
                elif "variable_data" in item:
                    # 格式2: {"variable_data": {...}, "evidence_data": {...}}（边的实际格式）
                    edges_clean.append(item["variable_data"])
                else:
                    # 已经是扁平结构
                    edges_clean.append(item)
            else:
                edges_clean.append(item)
        
        # 扁平化防护谓词数据
        p_clean = []
        for item in protections:
            if isinstance(item, dict):
                if "predicate" in item:
                    # 嵌套结构，提取 predicate
                    p_clean.append(item["predicate"])
                else:
                    # 已经是扁平结构
                    p_clean.append(item)
            else:
                p_clean.append(item)
        
        # 扁平化危害谓词数据
        h_clean = []
        for item in hazards:
            if isinstance(item, dict):
                if "predicate" in item:
                    # 嵌套结构，提取 predicate
                    h_clean.append(item["predicate"])
                else:
                    # 已经是扁平结构
                    h_clean.append(item)
            else:
                h_clean.append(item)
        
        # 防御性去重检查（只对变量）
        vars_clean = self._deduplicate_by_name(vars_clean)
        
        unified = {
            "D": {"vars": vars_clean},
            "G": {"edges": edges_clean},
            "P": p_clean,
            "H": h_clean
        }
        
        # 添加可选的 metadata
        if metadata:
            unified["metadata"] = metadata
        
        return unified
    
    def format_with_evidence(self, variables_with_evidence, edges_with_evidence, 
                            protections_with_evidence, hazards_with_evidence, metadata=None):
        """
        生成 evidence 版本统一输出
        
        Args:
            variables_with_evidence: 带证据的变量列表
            edges_with_evidence: 带证据的边列表
            protections_with_evidence: 带证据的防护谓词列表
            hazards_with_evidence: 带证据的危害谓词列表
            metadata: 可选的元数据
            
        Returns:
            dict: 包含 evidence 字段的统一结构
        """
        # 提取 variables 和 evidence
        vars_clean = []
        for item in variables_with_evidence:
            if isinstance(item, dict) and "variable_data" in item:
                var_with_ev = item["variable_data"].copy()
                if "evidence_data" in item:
                    var_with_ev["evidence"] = item["evidence_data"]
                vars_clean.append(var_with_ev)
            else:
                vars_clean.append(item)
        
        # 防御性去重检查
        vars_clean = self._deduplicate_by_name(vars_clean)
        
        # 提取 edges 和 evidence
        edges_clean = []
        for item in edges_with_evidence:
            if isinstance(item, dict) and "edge" in item:
                edge_with_ev = item["edge"].copy()
                if "evidence" in item:
                    edge_with_ev["evidence"] = item["evidence"]
                edges_clean.append(edge_with_ev)
            else:
                edges_clean.append(item)
        
        # 提取 predicates 和 evidence
        p_clean = []
        for item in protections_with_evidence:
            if isinstance(item, dict) and "predicate" in item:
                pred_with_ev = item["predicate"].copy()
                if "evidence" in item:
                    pred_with_ev["evidence"] = item["evidence"]
                p_clean.append(pred_with_ev)
            else:
                p_clean.append(item)
        
        h_clean = []
        for item in hazards_with_evidence:
            if isinstance(item, dict) and "predicate" in item:
                pred_with_ev = item["predicate"].copy()
                if "evidence" in item:
                    pred_with_ev["evidence"] = item["evidence"]
                h_clean.append(pred_with_ev)
            else:
                h_clean.append(item)
        
        unified = {
            "D": {"vars": vars_clean},
            "G": {"edges": edges_clean},
            "P": p_clean,
            "H": h_clean
        }
        
        # 添加可选的 metadata
        if metadata:
            unified["metadata"] = metadata
        
        return unified
    
    def generate_metadata(self, station, program, xml_file):
        """
        生成元数据
        
        Args:
            station: 控制站编号
            program: 控制程序名称
            xml_file: XML文件路径
            
        Returns:
            dict: 元数据字典
        """
        return {
            "station": station,
            "program": program,
            "xml_file": str(xml_file),
            "extracted_at": datetime.now().isoformat(),
            "extractor_version": "3.0.0"
        }
    
    def save_unified_json(self, variables, edges, protections, hazards,
                         variables_with_evidence, edges_with_evidence,
                         protections_with_evidence, hazards_with_evidence,
                         output_dir, file_prefix, metadata=None):
        """
        保存统一 JSON 文件（clean + evidence 两个版本）
        
        Args:
            variables: 变量列表（clean）
            edges: 边列表（clean）
            protections: 防护谓词列表（clean）
            hazards: 危害谓词列表（clean）
            variables_with_evidence: 带证据的变量列表
            edges_with_evidence: 带证据的边列表
            protections_with_evidence: 带证据的防护谓词列表
            hazards_with_evidence: 带证据的危害谓词列表
            output_dir: 输出目录
            file_prefix: 文件前缀（如"10_SCS02"）
            metadata: 可选的元数据
            
        Returns:
            tuple: (clean文件路径, evidence文件路径)
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Clean 版本
        clean_data = self.format_clean(variables, edges, protections, hazards, metadata)
        clean_file = output_path / f"{file_prefix}_unified_clean.json"
        
        with open(clean_file, 'w', encoding='utf-8') as f:
            json.dump(clean_data, f, ensure_ascii=False, indent=2)
        
        # 检查文件大小
        file_size_mb = clean_file.stat().st_size / (1024 * 1024)
        if file_size_mb > 100:
            print(f"  [警告] Clean 文件较大: {file_size_mb:.1f} MB")
        
        # Evidence 版本
        evidence_data = self.format_with_evidence(
            variables_with_evidence, edges_with_evidence,
            protections_with_evidence, hazards_with_evidence, metadata
        )
        evidence_file = output_path / f"{file_prefix}_unified_with_evidence.json"
        
        with open(evidence_file, 'w', encoding='utf-8') as f:
            json.dump(evidence_data, f, ensure_ascii=False, indent=2)
        
        # 检查文件大小
        file_size_mb = evidence_file.stat().st_size / (1024 * 1024)
        if file_size_mb > 100:
            print(f"  [警告] Evidence 文件较大: {file_size_mb:.1f} MB")
        
        return (str(clean_file), str(evidence_file))
