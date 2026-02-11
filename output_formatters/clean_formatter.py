#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
干净版输出格式化器
"""

class CleanFormatter:
    """生成干净版（Clean）输出"""
    
    def format(self, variable_data):
        """
        格式化为干净版输出
        
        Args:
            variable_data: 变量数据字典，包含所有字段的value
            
        Returns:
            str: 格式化后的字符串
        """
        lines = []
        
        # Aliases
        aliases = variable_data.get("aliases", ["", "", ""])
        aliases_str = '{ "' + '", "'.join(aliases) + '" }'
        lines.append(f"- aliases = {aliases_str}")
        
        # Name
        name = variable_data.get("name", "")
        lines.append(f"- name = \"{name}\"")
        
        # Type
        type_val = variable_data.get("type", "")
        lines.append(f"- type = {type_val}")
        
        # Scope
        scope = variable_data.get("scope", "")
        lines.append(f"- scope = {scope}")
        
        # Attackable
        attackable = variable_data.get("attackable", False)
        lines.append(f"- attackable = {'true' if attackable else 'false'}")
        
        # Default value
        default_value = variable_data.get("default_value", None)
        if default_value is None:
            lines.append(f"- default value = 空")
        else:
            lines.append(f"- default value = {default_value}")
        
        # Rate
        rate = variable_data.get("rate", None)
        lines.append(f"- rate = ∅")
        
        # Range
        range_val = variable_data.get("range", None)
        lines.append(f"- range = ∅")
        
        return "\n".join(lines)

