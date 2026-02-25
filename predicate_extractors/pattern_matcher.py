#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Pattern Matcher - 模式匹配器
识别XML中的谓词模式
"""

from .base_predicate_extractor import BasePredicateExtractor

class PatternMatcher(BasePredicateExtractor):
    """模式匹配器 - 识别偏差型和阈值型谓词模式"""
    
    def __init__(self):
        super().__init__()
    
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
        构建变量字典（复用ConnectionTracer逻辑）
        
        Args:
            elements: XML element列表
            context: 上下文（station, program等）
        """
        from edge_extractors.connection_tracer import ConnectionTracer
        
        tracer = ConnectionTracer()
        tracer.build_element_dict(elements)
        tracer.build_variable_dict(elements, context)
        
        self.variable_dict = tracer.variable_dict
    
    def find_deviation_patterns(self):
        """
        查找偏差型模式：SUB → ABS → GT/LT
        
        Returns:
            list: 偏差模式列表，每个元素为 {
                "sub_id": SUB元素ID,
                "abs_id": ABS元素ID,
                "cmp_id": GT/LT元素ID,
                "ref_var_id": 参考变量元素ID,
                "proc_var_id": 过程变量元素ID,
                "delta_id": 偏差阈值元素ID,
                "cmp_operator": ">"|"<"
            }
        """
        patterns = []
        
        # 遍历所有SUB box
        for element_id, element in self.element_dict.items():
            if self.get_element_attr(element, "type") != "box":
                continue
            
            at_type = self.get_element_text(element, "AT_type")
            if at_type != "SUB":
                continue
            
            # 获取SUB的两个输入
            inputs = self.get_element_children(element, "input")
            if len(inputs) < 2:
                continue
            
            input1_id = inputs[0].get("inputid", "")
            input2_id = inputs[1].get("inputid", "")
            
            if not input1_id or not input2_id or input1_id == "0" or input2_id == "0":
                continue
            
            # 检查两个输入是否都是变量
            if input1_id not in self.variable_dict or input2_id not in self.variable_dict:
                continue
            
            # 前向追踪：SUB → ABS
            abs_candidates = self.trace_forward(element_id, "ABS")
            if not abs_candidates:
                continue
            
            for abs_id in abs_candidates:
                # 前向追踪：ABS → GT/LT
                cmp_candidates = self.trace_forward(abs_id, ["GT", "LT", "GE", "LE"])
                
                for cmp_id, cmp_op in cmp_candidates:
                    # 验证GT/LT的另一个输入是常量
                    cmp_element = self.element_dict.get(cmp_id)
                    if not cmp_element:
                        continue
                    
                    cmp_inputs = self.get_element_children(cmp_element, "input")
                    if len(cmp_inputs) < 2:
                        continue
                    
                    # 找到非ABS的输入（应该是delta常量）
                    delta_id = None
                    for inp in cmp_inputs:
                        inp_id = inp.get("inputid", "")
                        if inp_id != abs_id and inp_id != "0":
                            # 检查是否是常量
                            delta_elem = self.element_dict.get(inp_id)
                            if delta_elem and self.get_element_attr(delta_elem, "type") == "input":
                                ttype = self.get_element_text(delta_elem, "ttype")
                                if ttype == "5":  # 常量
                                    delta_id = inp_id
                                    break
                    
                    if delta_id:
                        patterns.append({
                            "sub_id": element_id,
                            "abs_id": abs_id,
                            "cmp_id": cmp_id,
                            "ref_var_id": input1_id,
                            "proc_var_id": input2_id,
                            "delta_id": delta_id,
                            "cmp_operator": cmp_op
                        })
        
        return patterns
    
    def find_threshold_patterns(self):
        """
        查找阈值型模式：GT/LT(var, constant)
        
        Returns:
            list: 阈值模式列表，每个元素为 {
                "cmp_id": GT/LT元素ID,
                "var_id": 变量元素ID,
                "threshold_id": 阈值元素ID,
                "cmp_operator": ">"|"<"|">="|"<="
            }
        """
        patterns = []
        
        # 遍历所有GT/LT box
        for element_id, element in self.element_dict.items():
            if self.get_element_attr(element, "type") != "box":
                continue
            
            at_type = self.get_element_text(element, "AT_type")
            if at_type not in ["GT", "LT", "GE", "LE"]:
                continue
            
            # 获取比较符
            cmp_op = self._normalize_comparison_operator(at_type)
            
            # 获取两个输入
            inputs = self.get_element_children(element, "input")
            if len(inputs) < 2:
                continue
            
            input1_id = inputs[0].get("inputid", "")
            input2_id = inputs[1].get("inputid", "")
            
            if not input1_id or not input2_id or input1_id == "0" or input2_id == "0":
                continue
            
            # 检查一个是变量，另一个是常量
            var_id = None
            threshold_id = None
            
            # 检查input1
            if input1_id in self.variable_dict:
                var_id = input1_id
                # input2应该是常量
                threshold_elem = self.element_dict.get(input2_id)
                if threshold_elem and self.get_element_attr(threshold_elem, "type") == "input":
                    if self.get_element_text(threshold_elem, "ttype") == "5":
                        threshold_id = input2_id
            
            # 或者input2是变量
            elif input2_id in self.variable_dict:
                var_id = input2_id
                # input1应该是常量
                threshold_elem = self.element_dict.get(input1_id)
                if threshold_elem and self.get_element_attr(threshold_elem, "type") == "input":
                    if self.get_element_text(threshold_elem, "ttype") == "5":
                        threshold_id = input1_id
            
            if var_id and threshold_id:
                patterns.append({
                    "cmp_id": element_id,
                    "var_id": var_id,
                    "threshold_id": threshold_id,
                    "cmp_operator": cmp_op
                })
        
        return patterns
    
    def trace_forward(self, element_id, target_types):
        """
        前向追踪：查找引用当前元素的目标类型box
        
        Args:
            element_id: 当前元素ID
            target_types: 目标AT_type（字符串或列表）
            
        Returns:
            list: 如果target_types是字符串，返回元素ID列表
                  如果target_types是列表，返回(元素ID, AT_type)元组列表
        """
        if isinstance(target_types, str):
            target_types = [target_types]
            return_tuples = False
        else:
            return_tuples = True
        
        results = []
        
        for eid, element in self.element_dict.items():
            if self.get_element_attr(element, "type") != "box":
                continue
            
            at_type = self.get_element_text(element, "AT_type")
            if at_type not in target_types:
                continue
            
            # 检查这个box的输入是否引用了element_id
            inputs = self.get_element_children(element, "input")
            for inp in inputs:
                inp_id = inp.get("inputid", "")
                if inp_id == element_id:
                    if return_tuples:
                        results.append((eid, at_type))
                    else:
                        results.append(eid)
                    break
        
        return results
    
    def trace_backward(self, element_id):
        """
        后向追踪：递归查找元素的输入源
        
        Args:
            element_id: 元素ID
            
        Returns:
            list: 源变量的元素ID列表
        """
        element = self.element_dict.get(element_id)
        if not element:
            return []
        
        element_type = self.get_element_attr(element, "type")
        
        # 如果是变量，直接返回
        if element_id in self.variable_dict:
            return [element_id]
        
        # 如果是box，递归追踪其输入
        if element_type == "box":
            sources = []
            inputs = self.get_element_children(element, "input")
            for inp in inputs:
                inp_id = inp.get("inputid", "")
                if inp_id and inp_id != "0":
                    sources.extend(self.trace_backward(inp_id))
            return sources
        
        return []
    
    def extract_guards(self, cmp_id):
        """
        提取guards：查找与偏差判断AND组合的其他条件
        
        Args:
            cmp_id: 偏差判断的GT/LT元素ID
            
        Returns:
            list: guards列表，每个元素为阈值模式字典
        """
        guards = []
        
        # 查找引用cmp_id的AND box
        and_boxes = self.trace_forward(cmp_id, "AND")
        
        for and_id in and_boxes:
            and_element = self.element_dict.get(and_id)
            if not and_element:
                continue
            
            # 遍历AND的所有输入
            inputs = self.get_element_children(and_element, "input")
            for inp in inputs:
                inp_id = inp.get("inputid", "")
                if inp_id == cmp_id or inp_id == "0":
                    continue
                
                # 检查这个输入是否是阈值模式
                inp_element = self.element_dict.get(inp_id)
                if not inp_element or self.get_element_attr(inp_element, "type") != "box":
                    continue
                
                at_type = self.get_element_text(inp_element, "AT_type")
                if at_type not in ["GT", "LT", "GE", "LE"]:
                    continue
                
                # 尝试解析为阈值模式
                inp_inputs = self.get_element_children(inp_element, "input")
                if len(inp_inputs) < 2:
                    continue
                
                inp1_id = inp_inputs[0].get("inputid", "")
                inp2_id = inp_inputs[1].get("inputid", "")
                
                var_id = None
                threshold_id = None
                
                if inp1_id in self.variable_dict:
                    var_id = inp1_id
                    threshold_elem = self.element_dict.get(inp2_id)
                    if threshold_elem and self.get_element_text(threshold_elem, "ttype") == "5":
                        threshold_id = inp2_id
                elif inp2_id in self.variable_dict:
                    var_id = inp2_id
                    threshold_elem = self.element_dict.get(inp1_id)
                    if threshold_elem and self.get_element_text(threshold_elem, "ttype") == "5":
                        threshold_id = inp1_id
                
                if var_id and threshold_id:
                    guards.append({
                        "cmp_id": inp_id,
                        "var_id": var_id,
                        "threshold_id": threshold_id,
                        "cmp_operator": self._normalize_comparison_operator(at_type)
                    })
        
        return guards
    
    def _normalize_comparison_operator(self, at_type):
        """将AT_type转换为标准比较符"""
        mapping = {
            "GT": ">",
            "LT": "<",
            "GE": ">=",
            "LE": "<=",
            "EQ": "==",
            "NE": "!="
        }
        return mapping.get(at_type, at_type)
