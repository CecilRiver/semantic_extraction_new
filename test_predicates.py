#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
谓词提取测试脚本
"""

from pathlib import Path
from main_extractor import MainExtractor
import json

def test_predicate_extraction():
    """测试谓词提取功能"""
    
    # 测试文件
    test_files = [
        r"input\XML格式控制程序\19\UserView\CCS02.xml",  # 偏差型防护谓词
        r"input\XML格式控制程序\10\UserView\FSSS01B.xml",  # 阈值型危害谓词
    ]
    
    print("="*80)
    print("谓词提取测试")
    print("="*80)
    
    # 创建提取器
    extractor = MainExtractor(extract_predicates=True)
    
    for test_file in test_files:
        if not Path(test_file).exists():
            print(f"\n⚠️  文件不存在: {test_file}")
            continue
        
        print(f"\n测试文件: {test_file}")
        print("-"*80)
        
        try:
            # 提取谓词
            predicates_data = extractor.extract_predicates_from_xml(test_file)
            
            if not predicates_data:
                print("  未提取到谓词数据")
                continue
            
            protections = predicates_data['protections']
            hazards = predicates_data['hazards']
            
            print(f"\n防护谓词(P): {len(protections)}")
            for item in protections:
                pred = item['predicate']
                print(f"  - {pred['id']}: {pred['name']}")
                print(f"    kind: {pred['kind']}")
                if pred['kind'] == 'deviation':
                    print(f"    {pred['ref_var']} vs {pred['proc_var']}, delta={pred['delta']}, guards={len(pred['guards'])}")
            
            print(f"\n危害谓词(H): {len(hazards)}")
            for item in hazards:
                pred = item['predicate']
                print(f"  - {pred['id']}: {pred['name']}")
                print(f"    kind: {pred['kind']}")
                if 'var' in pred:
                    print(f"    {pred['var']} {pred['cmp']} {pred.get('threshold', '')}")
            
            # 保存测试输出
            xml_path = Path(test_file)
            file_prefix = f"{extractor._extract_station_from_path(xml_path)}_{xml_path.stem}_test"
            
            extractor.predicate_formatter.save_predicates_json(
                protections=protections,
                hazards=hazards,
                output_dir="output/test_predicates",
                file_prefix=file_prefix
            )
            
            print(f"\n成功 - 测试输出已保存到: output/test_predicates/")
            
        except Exception as e:
            print(f"[X] 提取失败: {str(e)}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "="*80)
    print("测试完成")
    print("="*80)

if __name__ == "__main__":
    test_predicate_extraction()
