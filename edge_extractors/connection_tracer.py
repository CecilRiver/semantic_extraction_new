#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
连接路径追踪器 - 递归追踪元素间的连接关系
"""

from .base_edge_extractor import BaseEdgeExtractor

class ConnectionTracer(BaseEdgeExtractor):
    """追踪XML元素间的连接路径"""
    
    def __init__(self):
        self.element_dict = {}  # id -> element 映射
        self.variable_dict = {}  # id -> 变量name 映射
        self.visited = set()  # 防止循环引用
    
    def build_element_dict(self, elements):
        """
        构建元素字典
        
        Args:
            elements: XML element列表
        """
        self.element_dict = {}
        for element in elements:
            element_id = self.get_element_text(element, "id")
            if element_id:
                self.element_dict[element_id] = element
    
    def build_variable_dict(self, elements, context):
        """
        构建元素ID到变量名的映射
        
        Args:
            elements: XML element列表
            context: 上下文（station, program等）
        """
        from extractors.name_extractor import NameExtractor
        name_extractor = NameExtractor()
        
        self.variable_dict = {}
        
        for element in elements:
            element_id = self.get_element_text(element, "id")
            element_type = self.get_element_attr(element, "type")
            
            # 只有 input 和 output 类型有对应的变量
            if element_type in ["input", "output"]:
                text = self.get_element_text(element, "text")
                ttype = self.get_element_text(element, "ttype")
                
                # 检查是否是需要提取的变量
                if self._should_extract_variable(text, ttype):
                    result = name_extractor.extract(element, context)
                    variable_name = result["value"]
                    self.variable_dict[element_id] = variable_name
    
    def _should_extract_variable(self, text, ttype):
        """判断是否是有效的变量（与variable_filter逻辑一致）"""
        if not text:
            return False
        
        # 工程点位
        suffixes = [".DI", ".DV", ".DO", ".AV", ".AI", ".AO", ".PV", ".MV", ".SP"]
        for suffix in suffixes:
            if suffix in text:
                return True
        
        if "@" in text:
            return True
        
        # 常量
        if ttype == "5":
            return True
        
        return False
    
    def trace_connections(self, box_element):
        """
        追踪box元素的输入输出连接
        
        Args:
            box_element: box类型的element
            
        Returns:
            list: 连接列表，每个连接为 {
                "src_id": 源元素ID,
                "dst_id": 目标元素ID,
                "via_elements": 经过的元素ID列表,
                "box_element": box元素本身
            }
        """
        box_id = self.get_element_text(box_element, "id")
        
        # 获取所有输入
        input_elements = self.get_element_children(box_element, "input")
        
        connections = []
        
        for input_elem in input_elements:
            inputid = input_elem.get("inputid", "")
            if not inputid or inputid == "0":
                continue
            
            # 追踪输入的源头
            src_ids = self._trace_backward(inputid)
            
            # 追踪box的输出目标
            dst_ids = self._trace_forward(box_id)
            
            # 为每个源和目标组合生成连接
            for src_id in src_ids:
                for dst_id in dst_ids:
                    connections.append({
                        "src_id": src_id,
                        "dst_id": dst_id,
                        "via_elements": [src_id, box_id, dst_id],
                        "box_element": box_element
                    })
        
        return connections
    
    def _trace_backward(self, element_id, path=None):
        """
        向后追踪，找到真实的源变量
        
        Args:
            element_id: 当前元素ID
            path: 已访问的路径（防止循环）
            
        Returns:
            list: 源变量的元素ID列表
        """
        if path is None:
            path = []
        
        # 防止循环
        if element_id in path:
            return []
        
        # 检查是否是真实变量
        if element_id in self.variable_dict:
            return [element_id]
        
        # 如果是box元素，继续向后追踪其输入
        element = self.element_dict.get(element_id)
        if element is None:
            return []
        
        element_type = self.get_element_attr(element, "type")
        if element_type == "box":
            sources = []
            input_elements = self.get_element_children(element, "input")
            for input_elem in input_elements:
                inputid = input_elem.get("inputid", "")
                if inputid and inputid != "0":
                    new_path = path + [element_id]
                    sources.extend(self._trace_backward(inputid, new_path))
            return sources
        
        return []
    
    def _trace_forward(self, element_id, path=None):
        """
        向前追踪，找到真实的目标变量
        
        Args:
            element_id: 当前元素ID
            path: 已访问的路径（防止循环）
            
        Returns:
            list: 目标变量的元素ID列表
        """
        if path is None:
            path = []
        
        # 防止循环
        if element_id in path:
            return []
        
        targets = []
        
        # 查找所有引用当前元素的元素
        for eid, element in self.element_dict.items():
            element_type = self.get_element_attr(element, "type")
            
            # output元素通过Inputid引用
            if element_type == "output":
                inputid = self.get_element_text(element, "Inputid", "")
                if inputid == element_id:
                    # 找到目标变量
                    if eid in self.variable_dict:
                        targets.append(eid)
            
            # box元素通过input子元素的inputid引用
            elif element_type == "box":
                input_elements = self.get_element_children(element, "input")
                for input_elem in input_elements:
                    inputid = input_elem.get("inputid", "")
                    if inputid == element_id:
                        # 继续向前追踪
                        new_path = path + [element_id]
                        targets.extend(self._trace_forward(eid, new_path))
        
        return targets
    
    def get_connection_path(self, src_id, dst_id):
        """
        获取从源到目标的完整路径
        
        Args:
            src_id: 源元素ID
            dst_id: 目标元素ID
            
        Returns:
            list: 元素ID路径
        """
        # 简化版本：返回直接路径
        # 完整版本需要实现路径搜索算法（如BFS）
        return [src_id, dst_id]
