#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
边构建器 - 核心边构建逻辑
"""

from .base_edge_extractor import BaseEdgeExtractor
from .connection_tracer import ConnectionTracer
from .type_classifier import TypeClassifier
from .eta_calculator import EtaCalculator
from datetime import datetime

class EdgeBuilder(BaseEdgeExtractor):
    """构建完整的边对象"""
    
    def __init__(self):
        """初始化边构建器"""
        self.tracer = ConnectionTracer()
        self.type_classifier = TypeClassifier()
        self.eta_calculator = EtaCalculator()
    
    def build_edges(self, elements, context):
        """
        从XML元素列表构建所有边
        
        Args:
            elements: XML element列表
            context: 上下文信息
            
        Returns:
            list: 边列表，每个边包含 variable_data 和 evidence_data
        """
        # 构建映射字典
        self.tracer.build_element_dict(elements)
        self.tracer.build_variable_dict(elements, context)
        
        edges = []
        
        # 遍历所有box元素
        for element in elements:
            element_type = self.get_element_attr(element, "type")
            if element_type != "box":
                continue
            
            # 提取该box的所有连接
            connections = self.tracer.trace_connections(element)
            
            # 为每个连接构建边
            for conn in connections:
                edge = self._build_single_edge(conn, element, context)
                if edge:
                    edges.append(edge)
        
        return edges
    
    def _build_single_edge(self, connection, box_element, context):
        """
        构建单条边
        
        Args:
            connection: 连接信息 {src_id, dst_id, via_elements, box_element}
            box_element: box元素
            context: 上下文
            
        Returns:
            dict: 边数据（包含 variable_data 和 evidence_data）
        """
        src_id = connection["src_id"]
        dst_id = connection["dst_id"]
        
        # 获取变量名
        src_name = self.tracer.variable_dict.get(src_id)
        dst_name = self.tracer.variable_dict.get(dst_id)
        
        # 如果src或dst无法解析，跳过
        if not src_name or not dst_name:
            return None
        
        # 分类边类型
        type_result = self.type_classifier.classify(box_element)
        edge_type = type_result["type"]
        
        # 计算eta
        eta_result = self.eta_calculator.calculate(box_element, edge_type)
        eta = eta_result["eta"]
        eps = eta_result["eps"]
        
        # 提取meta信息
        meta = self._extract_meta(box_element, connection, context)
        
        # 构建边数据
        variable_data = {
            "src": src_name,
            "dst": dst_name,
            "type": edge_type,
            "eta": eta,
            "eps": eps,
            "meta": meta
        }
        
        # 构建证据数据
        evidence_data = {
            "e_src": f"element(id={src_id}) → 变量字典查找 → {src_name}",
            "e_dst": f"element(id={dst_id}) → 变量字典查找 → {dst_name}",
            "e_type": type_result["evidence"],
            "e_eta": eta_result["evidence"],
            "e_connection": f"追踪路径：{' → '.join(map(str, connection['via_elements']))}"
        }
        
        return {
            "variable_data": variable_data,
            "evidence_data": evidence_data
        }
    
    def _extract_meta(self, box_element, connection, context):
        """
        提取meta信息
        
        Args:
            box_element: box元素
            connection: 连接信息
            context: 上下文
            
        Returns:
            dict: meta数据
        """
        box_id = self.get_element_text(box_element, "id")
        box_text = self.get_element_text(box_element, "text", "")
        at_type = self.get_element_text(box_element, "AT_type", "")
        
        program = context.get("program", "UNKNOWN")
        xml_file = context.get("xml_file", "")
        
        meta = {
            "block": box_text if box_text else f"element_{box_id}",
            "block_type": at_type,
            "origin": f"{program}.xml:element[id={box_id}]",
            "element_path": connection.get("via_elements", [])
        }
        
        return meta
