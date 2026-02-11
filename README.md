# XML变量提取系统

自动从XML控制程序文件中提取变量字典，生成**双输出格式**（干净版 + 带证据版）的JSON文件。

## 📁 项目结构

```
semantic_extraction_new/
├── extractors/              # 字段提取器模块
│   ├── name_extractor.py           # Name字段提取
│   ├── aliases_extractor.py        # Aliases字段提取
│   ├── type_extractor.py           # Type字段提取
│   ├── scope_extractor.py          # Scope字段提取
│   ├── attackable_extractor.py     # Attackable字段提取
│   ├── default_value_extractor.py  # Default Value字段提取
│   ├── rate_extractor.py           # Rate字段提取
│   └── range_extractor.py          # Range字段提取
├── filters/                 # 变量过滤器模块
│   └── variable_filter.py          # 判断哪些变量需要提取
├── output_formatters/       # 输出格式化模块
│   └── json_formatter.py           # JSON格式输出
├── main_extractor.py        # 主提取脚本
├── batch_extractor.py       # 批量提取脚本
└── input/XML格式控制程序/   # 输入XML文件
```

## 🚀 快速开始

### 1. 处理单个XML文件

```bash
python main_extractor.py
```

默认处理：`input\XML格式控制程序\10\UserView\SCS02.xml`

指定文件：
```bash
python main_extractor.py "input\XML格式控制程序\10\UserView\其他文件.xml"
```

### 2. 批量处理所有XML文件

```bash
python batch_extractor.py
```

将递归处理 `input\XML格式控制程序\` 下所有XML文件。

## 📊 输出格式

系统为每个XML文件生成两个JSON文件：

### 1. 干净版（Clean）- `*_clean.json`

仅包含变量字段值，符合论文定义格式：

```json
[
  {
    "aliases": ["HLS10GC001XB203.DI", "启动火检风机B", "10HLS10GC001XB203"],
    "name": "10_SCS02_HLS10GC001XB203.DI",
    "type": "bool",
    "scope": "global",
    "attackable": true,
    "default_value": null,
    "rate": null,
    "range": null
  }
]
```

### 2. 带证据版（With-Evidence）- `*_with_evidence.json`

包含变量字段值 + 证据映射，用于审计和复核：

```json
[
  {
    "variable": {
      "aliases": ["HLS10GC001XB203.DI", "启动火检风机B", "10HLS10GC001XB203"],
      "name": "10_SCS02_HLS10GC001XB203.DI",
      "type": "bool",
      "scope": "global",
      "attackable": true,
      "default_value": null,
      "rate": null,
      "range": null
    },
    "evidence": {
      "e_aliases": {
        "\"HLS10GC001XB203.DI\"": "← element(type=output, id=5).text",
        "\"启动火检风机B\"": "← element(type=output, id=5).Comment",
        "\"10HLS10GC001XB203\"": "← element(type=output, id=5).Alias"
      },
      "e_name": {
        "控制站": "\"10\" ← 文件路径",
        "控制程序": "\"SCS02\" ← <name>SCS02</name>",
        "变量名": "\"HLS10GC001XB203.DI\" ← element.text",
        "组合规则": "控制站_控制程序_变量名"
      },
      "e_type": {
        "规则": "T1-后缀规则（优先级最高）",
        "判断条件": "后缀 \".DI\" → bool",
        "证据": "text=\"HLS10GC001XB203.DI\""
      },
      ...
    }
  }
]
```

## 📝 提取规则

### 变量筛选规则

系统提取以下两类变量：

1. **工程点位变量**
   - `<element type="input">` 或 `<element type="output">`
   - `<text>` 包含工程后缀：`.DI`, `.DV`, `.AV`, `.AI`, `.AO` 等
   - 或包含 `@` 符号（远程点位）

2. **常量**
   - `<element type="input">` 且 `<ttype>5</ttype>`
   - 数字常量（如 `80`）或时间字面量（如 `T#15S`）

### 字段提取规则

#### Name（变量名）
格式：`控制站_控制程序_变量名`
- 控制站：从文件路径提取（如 `10`）
- 控制程序：从 `<name>` 标签提取（如 `SCS02`）
- 变量名：从 `<text>` 提取

#### Aliases（别名集合）
格式：`[text, Comment, Alias]`
- 第一项：`<text>` 内容
- 第二项：`<Comment>` 内容
- 第三项：`<Alias>` 内容（如无则为空字符串）

#### Type（数据类型）
优先级规则：
1. **T1 - 后缀规则**（最高优先级）
   - `.DI/.DV/.DO` → `bool`
   - `.AV/.AI/.AO/.PV/.MV/.SP` → `real`
2. **T2 - 常量规则**
   - 整数字面量 → `int`
   - 浮点字面量 → `real`
   - 时间字面量 `T#...` → `int`（转换为毫秒）

#### Scope（作用域）
- `global`：工程点位/跨实体交互变量
  - 包含后缀或 `@` 符号
  - `type="output"` 的元素
- `local`：功能块实例端口、内部中间量、常量
  - `ttype=5` 的常量

#### Attackable（可攻击性）
- `true`：命令/设定/可写输出
  - Comment 包含：启动、停止、设定、指令、给定、输出等
  - 后缀为 `.DI/.DO/.AO` 的命令类点位
- `false`：测量/状态/条件/内部量
  - Comment 包含：运行、状态、反馈、温度、压力、测量等
  - 后缀为 `.AV/.AI/.DV` 的状态类点位
  - 常量

#### Default Value（默认值）
- 常量：值即为默认值
  - 时间字面量自动转换为毫秒（如 `T#15S` → `15000`）
- 非常量：`null`

#### Rate & Range
- 仅当存在显式限制时填写，否则为 `null`

## 🔧 自定义配置

### 修改提取规则

各字段的提取规则分别在独立的模块中，可以单独修改：

- 修改 Name 规则：编辑 `extractors/name_extractor.py`
- 修改 Type 规则：编辑 `extractors/type_extractor.py`
- 修改 Attackable 关键词：编辑 `extractors/attackable_extractor.py`
- 修改变量筛选规则：编辑 `filters/variable_filter.py`

### 添加新字段

1. 在 `extractors/` 创建新的提取器（继承 `BaseExtractor`）
2. 在 `main_extractor.py` 中导入并使用
3. 在 `output_formatters/json_formatter.py` 中添加到输出格式

## 📦 输出目录

```
output/
└── extracted_variables/
    ├── 10_SCS02_clean.json
    ├── 10_SCS02_with_evidence.json
    ├── 11_MCS01_clean.json
    └── 11_MCS01_with_evidence.json
    ...
```

