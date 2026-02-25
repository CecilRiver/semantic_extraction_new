#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
主提取脚本 - 从XML文件提取变量字典（双输出格式）
"""

import xml.etree.ElementTree as ET
from pathlib import Path
import sys

# 导入过滤器
from filters.variable_filter import VariableFilter

# 导入提取器
from extractors.name_extractor import NameExtractor
from extractors.aliases_extractor import AliasesExtractor
from extractors.type_extractor import TypeExtractor
from extractors.scope_extractor import ScopeExtractor
from extractors.attackable_extractor import AttackableExtractor
from extractors.default_value_extractor import DefaultValueExtractor
from extractors.rate_extractor import RateExtractor
from extractors.range_extractor import RangeExtractor

# 导入格式化器
from output_formatters.json_formatter import JsonFormatter
from output_formatters.graph_json_formatter import GraphJsonFormatter

# 导入边提取器
from edge_extractors.edge_builder import EdgeBuilder


class MainExtractor:
    """主提取器类"""
    
    def __init__(self, extract_edges=False, extract_predicates=False):
        """
        初始化主提取器
        
        Args:
            extract_edges: 是否提取边（默认False）
            extract_predicates: 是否提取谓词（默认False）
        """
        # 初始化过滤器
        self.filter = VariableFilter()
        
        # 初始化变量提取器
        self.name_extractor = NameExtractor()
        self.aliases_extractor = AliasesExtractor()
        self.type_extractor = TypeExtractor()
        self.scope_extractor = ScopeExtractor()
        self.attackable_extractor = AttackableExtractor()
        self.default_value_extractor = DefaultValueExtractor()
        self.rate_extractor = RateExtractor()
        self.range_extractor = RangeExtractor()
        
        # 初始化格式化器
        self.json_formatter = JsonFormatter()
        self.graph_formatter = GraphJsonFormatter()
        
        # 边提取配置
        self.extract_edges = extract_edges
        if extract_edges:
            self.edge_builder = EdgeBuilder()
        
        # 谓词提取配置
        self.extract_predicates = extract_predicates
        if extract_predicates:
            from predicate_extractors.hazard_extractor import HazardExtractor
            from predicate_extractors.protection_extractor import ProtectionExtractor
            from output_formatters.predicate_formatter import PredicateFormatter
            
            self.hazard_extractor = HazardExtractor()
            self.protection_extractor = ProtectionExtractor()
            self.predicate_formatter = PredicateFormatter()
    
    def extract_from_xml_file(self, xml_file_path):
        """
        从单个XML文件提取变量字典
        
        Args:
            xml_file_path: XML文件路径
            
        Returns:
            list: 变量列表，每个变量包含 clean 和 evidence 两个版本
        """
        # 解析文件路径，获取控制站和控制程序
        xml_path = Path(xml_file_path)
        station = self._extract_station_from_path(xml_path)
        
        # 解析XML（尝试多种编码方式）
        try:
            xml_content = None
            # 尝试多种编码
            for encoding in ['gbk', 'gb2312', 'utf-8', 'latin-1']:
                try:
                    with open(xml_file_path, 'r', encoding=encoding) as f:
                        xml_content = f.read()
                    # 如果成功读取，跳出循环
                    break
                except UnicodeDecodeError:
                    continue
            
            if xml_content is None:
                print(f"错误: 无法使用任何编码解码文件 {xml_file_path}")
                return []
            
            # 解析XML内容
            root = ET.fromstring(xml_content)
        except ET.ParseError as e:
            print(f"错误: 无法解析XML文件 {xml_file_path}: {e}")
            return []
        except FileNotFoundError:
            print(f"错误: 文件不存在 {xml_file_path}")
            return []
        
        # 获取控制程序名称
        program_elem = root.find(".//name")
        program = program_elem.text if program_elem is not None and program_elem.text else "UNKNOWN"
        
        # 获取POUCycle（可选）
        pou_cycle_elem = root.find(".//POUCycle")
        pou_cycle = pou_cycle_elem.text if pou_cycle_elem is not None else None
        
        # 构建上下文
        context = {
            "station": station,
            "program": program,
            "pou_cycle": pou_cycle,
            "xml_file": str(xml_path)
        }
        
        # 查找所有element
        elements = root.findall(".//element")
        
        # 提取变量
        variables = []
        for element in elements:
            # 过滤：判断是否需要提取
            filter_result = self.filter.should_extract(element)
            if not filter_result["should_extract"]:
                continue
            
            # 提取变量
            variable = self._extract_variable(element, context)
            if variable:
                variables.append(variable)
        
        return variables
    
    def extract_edges_from_xml(self, xml_file_path):
        """
        从XML文件提取边
        
        Args:
            xml_file_path: XML文件路径
            
        Returns:
            dict: {
                "edges": 边列表,
                "metadata": 元数据,
                "context": 上下文
            }
        """
        if not self.extract_edges:
            return None
        
        # 解析文件路径
        xml_path = Path(xml_file_path)
        station = self._extract_station_from_path(xml_path)
        
        # 解析XML
        try:
            xml_content = None
            for encoding in ['gbk', 'gb2312', 'utf-8', 'latin-1']:
                try:
                    with open(xml_file_path, 'r', encoding=encoding) as f:
                        xml_content = f.read()
                    break
                except UnicodeDecodeError:
                    continue
            
            if xml_content is None:
                print(f"错误: 无法解码文件 {xml_file_path}")
                return None
            
            root = ET.fromstring(xml_content)
        except Exception as e:
            print(f"错误: 解析XML失败 {xml_file_path}: {e}")
            return None
        
        # 获取控制程序名称
        program_elem = root.find(".//name")
        program = program_elem.text if program_elem is not None and program_elem.text else "UNKNOWN"
        
        # 构建上下文
        context = {
            "station": station,
            "program": program,
            "xml_file": str(xml_path)
        }
        
        # 查找所有element
        elements = root.findall(".//element")
        
        # 构建边
        edges = self.edge_builder.build_edges(elements, context)
        
        # 生成metadata
        metadata = self.graph_formatter.generate_metadata(context)
        
        return {
            "edges": edges,
            "metadata": metadata,
            "context": context
        }
    
    def extract_predicates_from_xml(self, xml_file_path):
        """
        从XML文件提取谓词
        
        Args:
            xml_file_path: XML文件路径
            
        Returns:
            dict: {
                "protections": [...],
                "hazards": [...],
                "context": {...}
            }
        """
        if not self.extract_predicates:
            return None
        
        # 解析文件路径
        xml_path = Path(xml_file_path)
        station = self._extract_station_from_path(xml_path)
        
        # 解析XML
        try:
            xml_content = None
            for encoding in ['gbk', 'gb2312', 'utf-8', 'latin-1']:
                try:
                    with open(xml_file_path, 'r', encoding=encoding) as f:
                        xml_content = f.read()
                    break
                except UnicodeDecodeError:
                    continue
            
            if xml_content is None:
                print(f"错误: 无法解码文件 {xml_file_path}")
                return None
            
            root = ET.fromstring(xml_content)
        except Exception as e:
            print(f"错误: 解析XML失败 {xml_file_path}: {e}")
            return None
        
        # 获取控制程序名称
        program_elem = root.find(".//name")
        program = program_elem.text if program_elem is not None and program_elem.text else "UNKNOWN"
        
        # 构建上下文
        context = {
            "station": station,
            "program": program,
            "xml_file": str(xml_path)
        }
        
        # 查找所有element
        elements = root.findall(".//element")
        
        # 提取谓词
        protections = self.protection_extractor.extract_protections(elements, context)
        hazards = self.hazard_extractor.extract_hazards(elements, context)
        
        return {
            "protections": protections,
            "hazards": hazards,
            "context": context
        }
    
    def _extract_variable(self, element, context):
        """
        从element提取单个变量
        
        Returns:
            dict: {
                "variable_data": {...},  # 字段值
                "evidence_data": {...},  # 证据
                "clean_output": str,     # 干净版输出
                "evidence_output": str   # 带证据版输出
            }
        """
        variable_data = {}
        evidence_data = {}
        
        # 1. 提取 aliases
        result = self.aliases_extractor.extract(element, context)
        variable_data["aliases"] = result["value"]
        evidence_data["aliases"] = result["evidence"]
        
        # 2. 提取 name
        result = self.name_extractor.extract(element, context)
        variable_data["name"] = result["value"]
        evidence_data["name"] = result["evidence"]
        
        # 3. 提取 type
        result = self.type_extractor.extract(element, context)
        variable_data["type"] = result["value"]
        evidence_data["type"] = result["evidence"]
        
        # 更新上下文（type会被scope等使用）
        context["type"] = variable_data["type"]
        
        # 4. 提取 scope
        result = self.scope_extractor.extract(element, context)
        variable_data["scope"] = result["value"]
        evidence_data["scope"] = result["evidence"]
        
        # 5. 提取 attackable
        result = self.attackable_extractor.extract(element, context)
        variable_data["attackable"] = result["value"]
        evidence_data["attackable"] = result["evidence"]
        
        # 6. 提取 default_value
        result = self.default_value_extractor.extract(element, context)
        variable_data["default_value"] = result["value"]
        evidence_data["default_value"] = result["evidence"]
        
        # 7. 提取 rate
        result = self.rate_extractor.extract(element, context)
        variable_data["rate"] = result["value"]
        evidence_data["rate"] = result["evidence"]
        
        # 8. 提取 range
        result = self.range_extractor.extract(element, context)
        variable_data["range"] = result["value"]
        evidence_data["range"] = result["evidence"]
        
        return {
            "variable_data": variable_data,
            "evidence_data": evidence_data
        }
    
    def _extract_station_from_path(self, xml_path):
        """从文件路径中提取控制站编号"""
        # 路径格式：.../XML格式控制程序/10/UserView/SCS02.xml
        parts = xml_path.parts
        for i, part in enumerate(parts):
            if part == "XML格式控制程序" and i + 1 < len(parts):
                return parts[i + 1]
        return "UNKNOWN"
    
    def save_outputs(self, variables, output_dir, file_prefix="variables", edges_data=None, predicates_data=None):
        """
        保存输出到JSON文件
        
        Args:
            variables: 变量列表
            output_dir: 输出目录
            file_prefix: 文件前缀
            edges_data: 边数据（可选），包含edges, metadata, context
            predicates_data: 谓词数据（可选），包含protections, hazards, context
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # 保存变量
        clean_file = output_path / f"{file_prefix}_clean.json"
        count = self.json_formatter.save_clean_json(variables, clean_file)
        print(f"干净版已保存到: {clean_file} (共 {count} 个变量)")
        
        evidence_file = output_path / f"{file_prefix}_with_evidence.json"
        count = self.json_formatter.save_evidence_json(variables, evidence_file)
        print(f"带证据版已保存到: {evidence_file} (共 {count} 个变量)")
        
        # 保存图（如果有边数据）
        if edges_data:
            nodes = [v["variable_data"] for v in variables]
            self.graph_formatter.save_graph_json(
                nodes=nodes,
                edges=edges_data["edges"],
                metadata=edges_data["metadata"],
                output_dir="output/extracted_graphs",
                file_prefix=file_prefix
            )
        
        # 保存谓词（如果有谓词数据）
        if predicates_data:
            self.predicate_formatter.save_predicates_json(
                protections=predicates_data["protections"],
                hazards=predicates_data["hazards"],
                output_dir="output/extracted_predicates",
                file_prefix=file_prefix
            )


def main():
    """主函数"""
    import argparse
    
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='XML变量和图结构提取器')
    parser.add_argument('xml_file', nargs='?', 
                       default=r"input\XML格式控制程序\10\UserView\SCS02.xml",
                       help='XML文件路径')
    parser.add_argument('--extract-edges', action='store_true',
                       help='是否提取边（图结构）')
    parser.add_argument('--extract-predicates', action='store_true',
                       help='是否提取谓词（P和H）')
    
    args = parser.parse_args()
    
    print(f"开始处理文件: {args.xml_file}")
    mode_parts = ["变量提取"]
    if args.extract_edges:
        mode_parts.append("图结构提取")
    if args.extract_predicates:
        mode_parts.append("谓词提取")
    print(f"模式: {' + '.join(mode_parts)}")
    print("="*60)
    
    # 创建提取器
    extractor = MainExtractor(
        extract_edges=args.extract_edges,
        extract_predicates=args.extract_predicates
    )
    
    # 提取变量
    variables = extractor.extract_from_xml_file(args.xml_file)
    
    print(f"\n提取完成！共提取 {len(variables)} 个变量")
    
    # 提取边（如果启用）
    edges_data = None
    if args.extract_edges:
        print("="*60)
        print("开始提取图结构...")
        edges_data = extractor.extract_edges_from_xml(args.xml_file)
        if edges_data:
            print(f"提取完成！共提取 {len(edges_data['edges'])} 条边")
    
    # 提取谓词（如果启用）
    predicates_data = None
    if args.extract_predicates:
        print("="*60)
        print("开始提取谓词...")
        predicates_data = extractor.extract_predicates_from_xml(args.xml_file)
        if predicates_data:
            p_count = len(predicates_data['protections'])
            h_count = len(predicates_data['hazards'])
            print(f"提取完成！共提取 {p_count} 个防护谓词(P)，{h_count} 个危害谓词(H)")
    
    print("="*60)
    
    # 保存输出
    xml_path = Path(args.xml_file)
    file_prefix = f"{extractor._extract_station_from_path(xml_path)}_{xml_path.stem}"
    
    extractor.save_outputs(
        variables, 
        output_dir="output/extracted_variables",
        file_prefix=file_prefix,
        edges_data=edges_data,
        predicates_data=predicates_data
    )
    
    print("\n处理完成！")


if __name__ == "__main__":
    main()


