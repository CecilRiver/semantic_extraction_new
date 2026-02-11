#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
使用GBK编码读取XML文件并将内容写入XML文件（转换为UTF-8编码）
"""

import os
from pathlib import Path

def read_xml_and_write_to_xml(xml_file_path, output_xml_path):
    """
    读取XML文件并写入XML文件（编码转换：GBK -> UTF-8）
    
    Args:
        xml_file_path: 输入的XML文件路径
        output_xml_path: 输出的XML文件路径
    """
    try:
        # 使用GBK编码读取XML文件
        with open(xml_file_path, 'r', encoding='gbk') as xml_input_file:
            content = xml_input_file.read()
        
        # 将内容写入XML文件（使用UTF-8编码，更通用）
        with open(output_xml_path, 'w', encoding='utf-8') as xml_output_file:
            xml_output_file.write(content)
        
        print(f"成功处理: {xml_file_path} -> {output_xml_path}")
        
    except FileNotFoundError:
        print(f"错误: 找不到文件 {xml_file_path}")
    except UnicodeDecodeError:
        print(f"错误: 无法使用GBK编码解码文件 {xml_file_path}")
    except Exception as e:
        print(f"发生错误: {str(e)}")


def process_all_xml_files(input_base_dir, output_base_dir):
    """
    递归处理所有XML文件
    
    Args:
        input_base_dir: 输入文件夹的基础路径
        output_base_dir: 输出文件夹的基础路径
    """
    input_path = Path(input_base_dir)
    output_path = Path(output_base_dir)
    
    # 创建输出目录
    output_path.mkdir(parents=True, exist_ok=True)
    
    # 统计信息
    total_files = 0
    success_files = 0
    
    # 递归查找所有XML文件
    xml_files = list(input_path.rglob('*.xml'))
    total_files = len(xml_files)
    
    print(f"找到 {total_files} 个XML文件")
    print("="*60)
    
    for xml_file in xml_files:
        # 计算相对路径
        relative_path = xml_file.relative_to(input_path)
        
        # 构建输出路径，保持相同的目录结构
        output_file = output_path / relative_path
        
        # 创建输出文件的父目录
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        # 处理文件
        try:
            read_xml_and_write_to_xml(str(xml_file), str(output_file))
            success_files += 1
        except Exception as e:
            print(f"处理文件失败 {xml_file}: {str(e)}")
    
    print("="*60)
    print(f"处理完成！总共: {total_files} 个文件，成功: {success_files} 个")


if __name__ == "__main__":
    # 指定输入和输出文件夹路径
    input_dir = r"input\XML格式控制程序"
    output_dir = r"output\XML格式控制程序"
    
    # 批量处理所有XML文件
    process_all_xml_files(input_dir, output_dir)

