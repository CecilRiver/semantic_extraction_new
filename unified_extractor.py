#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
统一提取脚本 - 批量处理 XML 文件并生成统一格式输出
将变量(D)、图结构(G)、防护谓词(P)、危害谓词(H)整合到单个 JSON 文件
"""

from pathlib import Path
from main_extractor import MainExtractor
from output_formatters.unified_formatter import UnifiedFormatter
import time
import argparse

def batch_extract_unified(input_base_dir, output_base_dir="output/unified", skip_confirm=False):
    """
    批量处理所有 XML 文件，生成统一格式输出
    
    Args:
        input_base_dir: 输入文件夹基础路径
        output_base_dir: 输出文件夹基础路径
        skip_confirm: 是否跳过确认提示
    """
    input_path = Path(input_base_dir)
    output_path = Path(output_base_dir)
    
    # 创建输出目录
    output_path.mkdir(parents=True, exist_ok=True)
    
    # 验证输出路径可写
    try:
        test_file = output_path / ".write_test"
        test_file.touch()
        test_file.unlink()
    except Exception as e:
        print(f"错误: 输出目录不可写: {output_path}")
        print(f"详情: {str(e)}")
        return
    
    # 创建提取器和格式化器
    extractor = MainExtractor(extract_edges=True, extract_predicates=True)
    formatter = UnifiedFormatter()
    
    # 查找所有 XML 文件
    xml_files = list(input_path.rglob('*.xml'))
    total_files = len(xml_files)
    
    if total_files == 0:
        print(f"未找到任何 XML 文件: {input_path}")
        return
    
    print(f"找到 {total_files} 个 XML 文件")
    print("="*80)
    
    # 确认提示
    if not skip_confirm:
        response = input(f"开始批量处理？(y/n): ")
        if response.lower() != 'y':
            print("已取消")
            return
        print("="*80)
    
    # 统计信息
    total_variables = 0
    total_edges = 0
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
                print(f"  [警告] 未提取到变量")
            
            # 提取图结构
            edges_data = extractor.extract_edges_from_xml(str(xml_file))
            edges = edges_data["edges"] if edges_data else []
            
            # 提取谓词
            predicates_data = extractor.extract_predicates_from_xml(str(xml_file))
            
            if predicates_data:
                protections = predicates_data["protections"]
                hazards = predicates_data["hazards"]
            else:
                protections = []
                hazards = []
            
            # 准备 clean 数据
            vars_clean = [v["variable_data"] for v in variables]
            edges_clean = [e["edge"] if isinstance(e, dict) and "edge" in e else e for e in edges]
            p_clean = [p["predicate"] if isinstance(p, dict) and "predicate" in p else p for p in protections]
            h_clean = [h["predicate"] if isinstance(h, dict) and "predicate" in h else h for h in hazards]
            
            # 生成文件前缀
            station = extractor._extract_station_from_path(xml_file)
            file_prefix = f"{station}_{xml_file.stem}"
            
            # 生成 metadata
            metadata = formatter.generate_metadata(station, xml_file.stem, xml_file)
            
            # 保存统一输出
            clean_file, evidence_file = formatter.save_unified_json(
                vars_clean, edges_clean, p_clean, h_clean,
                variables, edges, protections, hazards,
                output_dir=str(output_path),
                file_prefix=file_prefix,
                metadata=metadata
            )
            
            # 更新统计
            total_variables += len(vars_clean)
            total_edges += len(edges_clean)
            total_protections += len(p_clean)
            total_hazards += len(h_clean)
            success_count += 1
            
            print(f"  [成功] vars={len(vars_clean)}, edges={len(edges_clean)}, P={len(p_clean)}, H={len(h_clean)}")
            
        except Exception as e:
            print(f"  [失败] {str(e)}")
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
    print(f"提取边总数: {total_edges}")
    print(f"提取防护谓词总数: {total_protections}")
    print(f"提取危害谓词总数: {total_hazards}")
    print(f"耗时: {elapsed_time:.2f} 秒")
    
    if failed_files:
        print("\n失败文件列表:")
        for file_path, error in failed_files:
            print(f"  - {Path(file_path).name}")
            print(f"    错误: {error}")
    else:
        print("\n所有文件处理成功！")
    
    print(f"\n输出目录: {output_path.absolute()}")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='XML 统一格式批量提取系统 - 将变量、图、谓词整合到单个 JSON 文件',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python unified_extractor.py                    # 默认处理，带确认提示
  python unified_extractor.py -y                 # 跳过确认
  python unified_extractor.py --output custom/   # 自定义输出目录
        """
    )
    
    parser.add_argument(
        '--yes', '-y',
        action='store_true',
        help='跳过确认提示，直接开始处理'
    )
    
    parser.add_argument(
        '--output', '-o',
        default='output/unified',
        help='输出目录路径（默认: output/unified）'
    )
    
    args = parser.parse_args()
    
    # 输入和输出目录
    input_dir = r"input\XML格式控制程序"
    output_dir = args.output
    
    print("="*80)
    print("XML 统一格式批量提取系统")
    print("="*80)
    print(f"输入目录: {input_dir}")
    print(f"输出目录: {output_dir}")
    print(f"输出格式: D(vars) + G(edges) + P + H")
    print()
    
    # 批量处理
    batch_extract_unified(input_dir, output_dir, skip_confirm=args.yes)


if __name__ == "__main__":
    main()
