#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
图JSON格式化器 - 输出图结构（nodes + edges）
"""

import json
from datetime import datetime
from pathlib import Path

class GraphJsonFormatter:
    """图结构JSON格式化器"""
    
    def format_clean_graph(self, nodes, edges, metadata):
        """
        格式化干净版图JSON
        
        Args:
            nodes: 节点列表（变量列表）
            edges: 边列表
            metadata: 元数据
            
        Returns:
            dict: 图结构
        """
        graph = {
            "metadata": metadata,
            "nodes": nodes,
            "edges": [edge["variable_data"] for edge in edges]
        }
        return graph
    
    def format_evidence_graph(self, nodes, edges, metadata):
        """
        格式化带证据版图JSON
        
        Args:
            nodes: 节点列表（变量列表）
            edges: 边列表
            metadata: 元数据
            
        Returns:
            dict: 图结构（包含证据）
        """
        edges_with_evidence = []
        for edge in edges:
            edges_with_evidence.append({
                "edge": edge["variable_data"],
                "evidence": edge["evidence_data"]
            })
        
        graph = {
            "metadata": metadata,
            "nodes": nodes,
            "edges": edges_with_evidence
        }
        return graph
    
    def generate_metadata(self, context):
        """
        生成metadata
        
        Args:
            context: 上下文信息
            
        Returns:
            dict: metadata
        """
        metadata = {
            "station": context.get("station", ""),
            "program": context.get("program", ""),
            "xml_file": context.get("xml_file", ""),
            "extracted_at": datetime.now().isoformat(),
            "extractor_version": "1.0.0"
        }
        return metadata
    
    def save_graph_json(self, nodes, edges, metadata, output_dir, file_prefix):
        """
        保存图JSON到文件
        
        Args:
            nodes: 节点列表
            edges: 边列表
            metadata: 元数据
            output_dir: 输出目录
            file_prefix: 文件前缀
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # 保存干净版
        clean_graph = self.format_clean_graph(nodes, edges, metadata)
        clean_file = output_path / f"{file_prefix}_graph_clean.json"
        
        with open(clean_file, 'w', encoding='utf-8') as f:
            json.dump(clean_graph, f, ensure_ascii=False, indent=2)
        
        print(f"图(干净版)已保存到: {clean_file} (共 {len(edges)} 条边)")
        
        # 保存带证据版
        evidence_graph = self.format_evidence_graph(nodes, edges, metadata)
        evidence_file = output_path / f"{file_prefix}_graph_with_evidence.json"
        
        with open(evidence_file, 'w', encoding='utf-8') as f:
            json.dump(evidence_graph, f, ensure_ascii=False, indent=2)
        
        print(f"图(带证据版)已保存到: {evidence_file} (共 {len(edges)} 条边)")
        
        return {
            "clean_file": str(clean_file),
            "evidence_file": str(evidence_file),
            "edge_count": len(edges),
            "node_count": len(nodes)
        }
