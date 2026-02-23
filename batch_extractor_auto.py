#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
批量提取脚本（自动模式）- 直接处理所有XML文件，无需确认
"""

from pathlib import Path
from main_extractor import MainExtractor
import time

def batch_extract_all_xml_files(input_base_dir, output_base_dir, extract_edges=False):
    """
    批量处理所有XML文件
    
    Args:
        input_base_dir: 输入文件夹基础路径
        output_base_dir: 输出文件夹基础路径
        extract_edges: 是否提取边（图结构）
    """
    input_path = Path(input_base_dir)
    output_path = Path(output_base_dir)
    
    # 创建输出目录
    output_path.mkdir(parents=True, exist_ok=True)
    
    # 创建提取器
    extractor = MainExtractor(extract_edges=extract_edges)
    
    # 查找所有XML文件
    xml_files = list(input_path.rglob('*.xml'))
    total_files = len(xml_files)
    
    print(f"找到 {total_files} 个XML文件")
    if extract_edges:
        print("模式: 变量 + 图结构提取")
    else:
        print("模式: 仅变量提取")
    print("="*80)
    
    # 统计信息
    total_variables = 0
    total_edges = 0
    success_count = 0
    failed_files = []
    
    start_time = time.time()
    
    # 处理每个文件
    for i, xml_file in enumerate(xml_files, 1):
        print(f"\n[{i}/{total_files}] 正在处理: {xml_file.name}")
        print("-"*80)
        
        try:
            # 提取变量
            variables = extractor.extract_from_xml_file(str(xml_file))
            
            if not variables:
                print(f"  ⚠️  未提取到变量")
                continue
            
            # 提取边（如果启用）
            edges_data = None
            if extract_edges:
                edges_data = extractor.extract_edges_from_xml(str(xml_file))
                if edges_data:
                    total_edges += len(edges_data["edges"])
            
            # 生成输出文件名
            station = extractor._extract_station_from_path(xml_file)
            file_prefix = f"{station}_{xml_file.stem}"
            
            # 保存输出
            extractor.save_outputs(
                variables,
                output_dir=str(output_path),
                file_prefix=file_prefix,
                edges_data=edges_data
            )
            
            total_variables += len(variables)
            success_count += 1
            
            edge_info = f", {len(edges_data['edges'])} 条边" if edges_data else ""
            print(f"  ✓ 成功提取 {len(variables)} 个变量{edge_info}")
            
        except Exception as e:
            print(f"  ✗ 处理失败: {str(e)}")
            failed_files.append((str(xml_file), str(e)))
    
    # 总结
    elapsed_time = time.time() - start_time
    
    print("\n" + "="*80)
    print("批量处理完成！")
    print("="*80)
    print(f"处理文件总数: {total_files}")
    print(f"成功处理: {success_count}")
    print(f"失败: {len(failed_files)}")
    print(f"提取变量总数: {total_variables}")
    if extract_edges:
        print(f"提取边总数: {total_edges}")
    print(f"耗时: {elapsed_time:.2f} 秒")
    
    if failed_files:
        print("\n失败文件列表:")
        for file_path, error in failed_files:
            print(f"  - {file_path}")
            print(f"    错误: {error}")
    
    print(f"\n输出目录: {output_path.absolute()}")


def main():
    """主函数"""
    import argparse
    
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='批量XML变量和图结构提取器')
    parser.add_argument('--extract-edges', action='store_true',
                       help='是否提取边（图结构）')
    
    args = parser.parse_args()
    
    # 输入和输出目录
    input_dir = r"input\XML格式控制程序"
    output_dir = r"output\extracted_variables"
    
    print("="*80)
    print("XML变量批量提取系统（自动模式）")
    if args.extract_edges:
        print("模式: 变量 + 图结构提取")
    else:
        print("模式: 仅变量提取")
    print("="*80)
    print(f"输入目录: {input_dir}")
    print(f"输出目录: {output_dir}")
    print()
    
    # 直接批量处理
    batch_extract_all_xml_files(input_dir, output_dir, extract_edges=args.extract_edges)


if __name__ == "__main__":
    main()

