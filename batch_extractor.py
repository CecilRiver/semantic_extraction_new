#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
批量提取脚本 - 处理所有XML文件
"""

from pathlib import Path
from main_extractor import MainExtractor
import time

def batch_extract_all_xml_files(input_base_dir, output_base_dir, extract_predicates=False):
    """
    批量处理所有XML文件
    
    Args:
        input_base_dir: 输入文件夹基础路径
        output_base_dir: 输出文件夹基础路径
        extract_predicates: 是否提取谓词（默认False）
    """
    input_path = Path(input_base_dir)
    output_path = Path(output_base_dir)
    
    # 创建输出目录
    output_path.mkdir(parents=True, exist_ok=True)
    
    # 创建提取器
    extractor = MainExtractor(extract_predicates=extract_predicates)
    
    # 查找所有XML文件
    xml_files = list(input_path.rglob('*.xml'))
    total_files = len(xml_files)
    
    print(f"找到 {total_files} 个XML文件")
    print("="*80)
    
    # 统计信息
    total_variables = 0
    total_protections = 0
    total_hazards = 0
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
            
            # 生成输出文件名
            station = extractor._extract_station_from_path(xml_file)
            file_prefix = f"{station}_{xml_file.stem}"
            
            # 提取谓词（如果启用）
            predicates_data = None
            if extract_predicates:
                predicates_data = extractor.extract_predicates_from_xml(str(xml_file))
                if predicates_data:
                    total_protections += len(predicates_data['protections'])
                    total_hazards += len(predicates_data['hazards'])
            
            # 保存输出
            extractor.save_outputs(
                variables,
                output_dir=str(output_path),
                file_prefix=file_prefix,
                predicates_data=predicates_data
            )
            
            total_variables += len(variables)
            success_count += 1
            
            if extract_predicates and predicates_data:
                p_count = len(predicates_data['protections'])
                h_count = len(predicates_data['hazards'])
                print(f"  ✓ 成功提取 {len(variables)} 个变量, {p_count} P, {h_count} H")
            else:
                print(f"  ✓ 成功提取 {len(variables)} 个变量")
            
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
    if extract_predicates:
        print(f"提取防护谓词总数: {total_protections}")
        print(f"提取危害谓词总数: {total_hazards}")
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
    parser = argparse.ArgumentParser(description='XML批量提取系统')
    parser.add_argument('--extract-predicates', action='store_true',
                       help='是否提取谓词（P和H）')
    args = parser.parse_args()
    
    # 输入和输出目录
    input_dir = r"input\XML格式控制程序"
    output_dir = r"output\extracted_variables"
    
    print("="*80)
    print("XML变量批量提取系统")
    print("="*80)
    print(f"输入目录: {input_dir}")
    print(f"输出目录: {output_dir}")
    if args.extract_predicates:
        print("模式: 变量 + 谓词提取")
    else:
        print("模式: 仅变量提取")
    print()
    
    # 确认
    response = input("开始批量处理？(y/n): ")
    if response.lower() != 'y':
        print("已取消")
        return
    
    # 批量处理
    batch_extract_all_xml_files(input_dir, output_dir, extract_predicates=args.extract_predicates)


if __name__ == "__main__":
    main()

