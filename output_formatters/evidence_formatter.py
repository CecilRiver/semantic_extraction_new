#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
带证据版输出格式化器
"""

class EvidenceFormatter:
    """生成带证据版（With-Evidence）输出"""
    
    def format(self, variable_data, evidence_data):
        """
        格式化为带证据版输出
        
        Args:
            variable_data: 变量数据字典（与干净版相同）
            evidence_data: 证据数据字典
            
        Returns:
            str: 格式化后的字符串
        """
        lines = []
        
        # 首先输出 𝓓 条目（必须与干净版一致）
        lines.append("#### 𝓓 条目（必须与干净版一致）")
        lines.append("")
        
        # 使用CleanFormatter生成
        from .clean_formatter import CleanFormatter
        clean_formatter = CleanFormatter()
        clean_output = clean_formatter.format(variable_data)
        lines.append(clean_output)
        
        lines.append("")
        lines.append("")
        
        # 然后输出证据映射
        lines.append("#### 证据映射 𝒆(v)")
        lines.append("")
        
        # e_aliases
        lines.append("- e_aliases：")
        aliases_evidence = evidence_data.get("aliases", {})
        for key, value in aliases_evidence.items():
            lines.append(f"  - {key} {value}")
        lines.append("")
        
        # e_name
        lines.append("- e_name：")
        name_evidence = evidence_data.get("name", {})
        for key, value in name_evidence.items():
            lines.append(f"  - {key}: {value}")
        lines.append("")
        
        # e_type
        lines.append("- e_type：")
        type_evidence = evidence_data.get("type", {})
        for key, value in type_evidence.items():
            lines.append(f"  - {key}: {value}")
        lines.append("")
        
        # e_scope
        lines.append("- e_scope：")
        scope_evidence = evidence_data.get("scope", {})
        for key, value in scope_evidence.items():
            lines.append(f"  - {key}: {value}")
        lines.append("")
        
        # e_attackable
        lines.append("- e_attackable：")
        attackable_evidence = evidence_data.get("attackable", {})
        for key, value in attackable_evidence.items():
            lines.append(f"  - {key}: {value}")
        lines.append("")
        
        # e_default
        lines.append("- e_default：")
        default_evidence = evidence_data.get("default_value", {})
        for key, value in default_evidence.items():
            lines.append(f"  - {key}: {value}")
        lines.append("")
        
        # e_rate
        lines.append("- e_rate：")
        rate_evidence = evidence_data.get("rate", {})
        for key, value in rate_evidence.items():
            lines.append(f"  - {key}: {value}")
        lines.append("")
        
        # e_range
        lines.append("- e_range：")
        range_evidence = evidence_data.get("range", {})
        for key, value in range_evidence.items():
            lines.append(f"  - {key}: {value}")
        
        return "\n".join(lines)

