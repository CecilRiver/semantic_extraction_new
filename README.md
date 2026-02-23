# XML变量与图结构提取系统

自动从XML控制程序文件中提取**变量字典**和**控制逻辑图结构**，生成**双输出格式**（干净版 + 带证据版）的JSON文件。

## ✨ 核心功能

- 🔍 **变量提取**：自动提取工程点位和常量，包含8个字段（name, aliases, type, scope, attackable等）
- 🕸️ **图结构提取**：提取变量间的依赖关系，构建控制逻辑图（nodes + edges）
- 📊 **边分类**：自动将边分类为 data（数据依赖）、guard（守卫依赖）、call（连线依赖）
- ⚖️ **权重计算**：基于功能块类型计算 eta 权重（PID=0.6, 限速器=0.8, 其他=1.0）
- 📝 **证据追溯**：每个字段和边都有完整的提取依据，支持审计
- 🔧 **可配置**：通过配置文件自定义 AT_type 映射和 eta 规则

## 📁 项目结构

```
semantic_extraction_new/
├── extractors/              # 变量字段提取器模块
│   ├── name_extractor.py           # Name字段提取
│   ├── aliases_extractor.py        # Aliases字段提取
│   ├── type_extractor.py           # Type字段提取
│   ├── scope_extractor.py          # Scope字段提取
│   ├── attackable_extractor.py     # Attackable字段提取
│   ├── default_value_extractor.py  # Default Value字段提取
│   ├── rate_extractor.py           # Rate字段提取
│   └── range_extractor.py          # Range字段提取
├── edge_extractors/         # 边提取器模块（NEW）
│   ├── connection_tracer.py        # 连接路径追踪器
│   ├── type_classifier.py          # 边类型分类器
│   ├── eta_calculator.py           # eta权重计算器
│   └── edge_builder.py             # 核心边构建逻辑
├── filters/                 # 变量过滤器模块
│   └── variable_filter.py          # 判断哪些变量需要提取
├── output_formatters/       # 输出格式化模块
│   ├── json_formatter.py           # 变量JSON格式输出
│   └── graph_json_formatter.py     # 图JSON格式输出（NEW）
├── config/                  # 配置文件（NEW）
│   ├── at_type_mapping.json        # AT_type映射规则
│   └── eta_rules.json              # eta计算规则
├── main_extractor.py        # 主提取脚本
├── batch_extractor_auto.py  # 批量提取脚本
└── input/XML格式控制程序/   # 输入XML文件
```

## 🚀 快速开始

### 1. 仅提取变量

```bash
# 单个文件
python main_extractor.py

# 批量处理
python batch_extractor_auto.py
```

### 2. 提取变量 + 图结构

```bash
# 单个文件（包含边提取）
python main_extractor.py --extract-edges

# 批量处理（包含边提取）
python batch_extractor_auto.py --extract-edges
```

### 3. 指定文件

```bash
python main_extractor.py "input\XML格式控制程序\10\UserView\其他文件.xml" --extract-edges
```

## 📊 输出格式

### 变量输出

系统为每个XML文件生成**两个变量JSON文件**：

#### 1. 干净版（Clean）- `*_clean.json`

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

#### 2. 带证据版（With-Evidence）- `*_with_evidence.json`

包含变量字段值 + 证据映射，用于审计和复核。

### 图结构输出（NEW）

使用 `--extract-edges` 参数时，系统额外生成**两个图JSON文件**：

#### 1. 图干净版 - `*_graph_clean.json`

```json
{
  "metadata": {
    "station": "10",
    "program": "SCS02",
    "xml_file": "...",
    "extracted_at": "2026-02-23T...",
    "extractor_version": "1.0.0"
  },
  "nodes": [
    {
      "aliases": ["HLS10GC001XB203.DI", "启动火检风机B", "10HLS10GC001XB203"],
      "name": "10_SCS02_HLS10GC001XB203.DI",
      "type": "bool",
      ...
    }
  ],
  "edges": [
    {
      "src": "10_SCS02_HLS10GC001XB114.DV",
      "dst": "10_SCS02_HLS10GC001XB203.DI",
      "type": "call",
      "eta": 0.6,
      "eps": 1.0,
      "meta": {
        "block": "HLS10GC001XB203DR",
        "block_type": "HSSCS6",
        "origin": "SCS02.xml:element[id=10]",
        "element_path": [4, 10, 5]
      }
    }
  ]
}
```

#### 2. 图带证据版 - `*_graph_with_evidence.json`

包含每条边的完整提取依据：

```json
{
  "edge": {
    "src": "10_SCS02_HLS10GC001XB114.DV",
    "dst": "10_SCS02_HLS10GC001XB203.DI",
    "type": "call",
    "eta": 0.6,
    ...
  },
  "evidence": {
    "e_src": "element(id=4) → 变量字典查找 → ...",
    "e_dst": "element(id=5) → 变量字典查找 → ...",
    "e_type": {"规则": "isinst=TRUE 的功能块 → call", ...},
    "e_eta": {"规则": "AT_type=HSSCS6 → ...", ...},
    "e_connection": "追踪路径：4 → 10 → 5"
  }
}
```

## 📊 输出文件组织

```
output/
├── extracted_variables/      # 变量输出
│   ├── 10_SCS02_clean.json
│   └── 10_SCS02_with_evidence.json
└── extracted_graphs/         # 图结构输出（--extract-edges）
    ├── 10_SCS02_graph_clean.json
    └── 10_SCS02_graph_with_evidence.json
```

```

## 变量带证据版示例

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
      }
    }
  }
]
```

## 📝 变量提取规则

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

## 🕸️ 图结构提取规则（NEW）

### 边类型分类

基于 XML 中的 `AT_type` 字段分类：

- **call（连线依赖）**
  - 功能块（如 `HSSCS6`, `HSTP`, `PID`, `HFOP`）
  - `isinst=TRUE` 的功能块实例
  - 未知 `AT_type` 默认为 call

- **guard（守卫依赖）**
  - 逻辑运算符（`AND`, `OR`, `NOT`, `XOR`）
  - 比较运算符（`LT`, `GT`, `LE`, `GE`, `EQ`, `NE`）
  - 影响条件判断的依赖

- **data（数据依赖）**
  - 算术运算符（`ADD`, `SUB`, `MUL`, `DIV`, `MOD`）
  - 直接赋值和表达式求值

### eta 权重计算

权重反映依赖关系的语义强度：

- **eta = 1.0**：条件与赋值类依赖（IF/CASE守卫、直接赋值、算术求值）
- **eta = 0.8**：限速/限幅类算子（Rate Limiter、Slew Rate）
- **eta = 0.6**：PID 和 HFOP 功能块链路

### 连接追踪

系统自动递归追踪 `box` 元素的输入输出：
- 从 `input` 元素的 `inputid` 向后追踪到源变量
- 从 `box` 向前追踪到目标 `output` 变量
- 记录完整的 `element_path`（经过的元素ID）

## 🔧 配置文件

### config/at_type_mapping.json

定义 `AT_type` 到边类型和 eta 的映射：

```json
{
  "mappings": {
    "LOGICAL_OPERATORS": {
      "types": ["AND", "OR", "NOT", "XOR"],
      "edge_type": "guard",
      "eta": 1.0
    },
    "PID_BLOCKS": {
      "patterns": ["*PID*"],
      "edge_type": "call",
      "eta": 0.6
    }
  }
}
```

支持：
- **精确匹配**：`"types": ["AND", "OR"]` - 精确匹配 AT_type
- **模式匹配**：`"patterns": ["*PID*"]` - 支持通配符 `*`

### config/eta_rules.json

定义 eta 计算规则：

```json
{
  "rules": [
    {
      "name": "PID控制器",
      "condition": {"at_type_contains": ["PID"]},
      "eta": 0.6
    }
  ],
  "default_eta": 1.0
}
```

支持条件：
- `at_type_contains`: AT_type 包含指定关键词
- `at_type_starts_with`: AT_type 以指定前缀开头
- `edge_type`: 边类型匹配

## 🔧 自定义配置

### 修改变量提取规则

各字段的提取规则分别在独立的模块中，可以单独修改：

- 修改 Name 规则：编辑 `extractors/name_extractor.py`
- 修改 Type 规则：编辑 `extractors/type_extractor.py`
- 修改 Attackable 关键词：编辑 `extractors/attackable_extractor.py`
- 修改变量筛选规则：编辑 `filters/variable_filter.py`

### 修改边提取规则

- **修改 AT_type 映射**：编辑 `config/at_type_mapping.json`
  - 添加新的运算符或功能块类型
  - 调整默认分类
  
- **修改 eta 规则**：编辑 `config/eta_rules.json`
  - 调整各功能块的权重值
  - 添加新的计算规则

### 添加新字段

1. 在 `extractors/` 创建新的提取器（继承 `BaseExtractor`）
2. 在 `main_extractor.py` 中导入并使用
3. 在 `output_formatters/json_formatter.py` 中添加到输出格式

## 📦 输出目录

```
output/
├── extracted_variables/      # 变量JSON
│   ├── 10_SCS02_clean.json
│   ├── 10_SCS02_with_evidence.json
│   └── ...
└── extracted_graphs/         # 图JSON（使用--extract-edges时）
    ├── 10_SCS02_graph_clean.json
    ├── 10_SCS02_graph_with_evidence.json
    └── ...
```

## 💡 使用示例

### 示例1：只提取变量

```bash
python batch_extractor_auto.py
```

输出：
- `output/extracted_variables/10_SCS02_clean.json`
- `output/extracted_variables/10_SCS02_with_evidence.json`

### 示例2：提取变量和图结构

```bash
python batch_extractor_auto.py --extract-edges
```

输出：
- 变量JSON（同上）
- `output/extracted_graphs/10_SCS02_graph_clean.json`
- `output/extracted_graphs/10_SCS02_graph_with_evidence.json`

### 示例3：调整 PID 功能块的 eta 值

编辑 `config/eta_rules.json`：

```json
{
  "rules": [
    {
      "name": "PID控制器",
      "condition": {"at_type_contains": ["PID"]},
      "eta": 0.5
    }
  ]
}
```

重新运行提取：

```bash
python main_extractor.py --extract-edges
```

### 示例4：添加新的边类型映射

编辑 `config/at_type_mapping.json`，添加新映射：

```json
{
  "mappings": {
    "MY_CUSTOM_BLOCK": {
      "types": ["CUSTOM_FB"],
      "edge_type": "call",
      "eta": 0.9
    }
  }
}
```

## 🔍 技术特性

### 变量提取
- **多编码支持**：自动尝试 GBK、GB2312、UTF-8、Latin-1 编码
- **智能过滤**：仅提取工程点位和常量，过滤中间元素
- **规则驱动**：8个字段分别由独立提取器实现，易于维护

### 图结构提取
- **递归追踪**：自动追踪 box 元素的多层连接关系
- **循环检测**：防止无限递归
- **类型分类**：基于 AT_type 自动分类为 data/guard/call
- **权重计算**：基于功能块类型计算语义权重
- **证据可追溯**：记录完整的分类和计算依据

### 输出格式
- **双输出**：clean（符合论文格式）+ with-evidence（包含审计信息）
- **UTF-8 编码**：正确显示中文内容
- **结构化 JSON**：易于后续分析和处理

## ❓ 常见问题

### Q1: 为什么有些变量没有被提取？

只提取**工程点位**和**常量**，内部中间变量会被过滤。

**工程点位判断标准**：
- `<text>` 包含后缀：`.DI/.DV/.AV/.AI/.AO/.DO/.PV/.MV/.SP`
- `<text>` 包含 `@` 符号
- `<ttype>5</ttype>` 的常量

### Q2: 为什么有些边的 src 或 dst 显示为空？

边只连接**已提取的变量**。如果源/目标元素不满足变量筛选规则，该边会被过滤掉。

### Q3: 中文乱码怎么办？

系统已自动处理多种编码。如果仍有问题，检查 XML 文件是否为 GBK 或 GB2312 编码。

### Q4: 如何调整 eta 权重？

编辑 `config/eta_rules.json` 文件，修改对应规则的 `eta` 值。

### Q5: 如何查看某个 AT_type 被分类为哪种边类型？

查看 `*_graph_with_evidence.json` 中的 `evidence.e_type` 字段，包含完整的分类依据。

## 📚 依赖

仅使用 Python 标准库，无需安装第三方依赖。

## 🎯 版本

- **v1.0.0**：变量提取基础功能
- **v2.0.0**：新增图结构提取功能（NEW）
