
# clang-format 配置选项完整分类指南

## 零、序章

在深入使用 `clang-format` 的过程中，许多开发者都会遇到一个共同的困境：**官方文档虽然详尽，但组织结构过于技术化，难以快速定位所需配置**。当我们需要调整特定代码结构的格式化规则时，往往需要在数百个配置项中反复搜索，效率低下且容易遗漏相关选项。

### 0.1 传统分类的局限性

clang-format 官方文档主要按照配置项的字母顺序排列，这种组织方式存在几个明显问题：

1. **功能关联性被割裂** - 相关的配置项分散在不同字母区域
2. **使用场景不明确** - 难以根据具体的编码需求快速找到对应配置
3. **学习曲线陡峭** - 新用户需要阅读大量不相关的配置说明才能找到所需内容

### 0.2 基于代码结构的分类优势

本分类指南采用**基于 C++ 代码结构的功能性分类方法**，具有以下显著优势：

1. **直观的查找体验**
   - 当需要调整函数格式时，直接查看"函数和参数格式"章节
   - 需要优化模板代码布局时，专注"模板和概念"部分
   - 统一团队的大括号风格，只需关注"大括号和代码块格式"

2. **完整的配置视图**
   - 相关配置项集中展示，避免遗漏重要选项
   - 配置之间的依赖关系和协同作用一目了然
   - 提供配置组合的最佳实践建议
  
3. **贴合实际开发 workflow**
   - 按照代码审查中常见的问题场景组织内容
   - 针对特定代码结构提供完整的格式化解决方案
   - 便于团队制定统一的编码规范

### 0.3 分类方法论

本指南的分类基于以下原则：

+ **功能相关性优先** - 将实现相同格式化目标的配置项归为一类
+ **代码结构导向** - 按照 C++ 语言结构（函数、类、模板等）组织分类
+ **使用频率加权** - 常用配置优先展示，特殊配置单独归类
+ **跨语言兼容** - 同时考虑 C++、Objective-C、Java 等语言的特殊需求

## 一、大括号和代码块格式

### 1.1 大括号换行风格

```yaml
BreakBeforeBraces: [Attach, Linux, Mozilla, Stroustrup, Allman, Whitesmiths, GNU, WebKit, Custom]
```

### 1.2 自定义大括号换行（当BreakBeforeBraces为Custom时）

```yaml
BraceWrapping:
  AfterCaseLabel, AfterClass, AfterControlStatement, AfterEnum, AfterFunction
  AfterNamespace, AfterStruct, AfterUnion, AfterExternBlock
  BeforeCatch, BeforeElse, BeforeLambdaBody, BeforeWhile
  IndentBraces, SplitEmptyFunction, SplitEmptyRecord, SplitEmptyNamespace
```

### 1.3 短代码块单行显示

```yaml
AllowShortBlocksOnASingleLine: [Never, Empty, Always]
AllowShortFunctionsOnASingleLine: [None, InlineOnly, Empty, Inline, All]
AllowShortIfStatementsOnASingleLine: [Never, WithoutElse, OnlyFirstIf, AllIfsAndElse]
AllowShortLoopsOnASingleLine: bool
AllowShortNamespacesOnASingleLine: bool
```

### 1.4 大括号相关

```yaml
SpaceInEmptyBraces: [Always, Block, Never]
InsertBraces: bool  # 自动插入大括号
RemoveBracesLLVM: bool  # 移除可选大括号
```

## 二、缩进配置

### 2.1 基本缩进设置

```yaml
IndentWidth: unsigned
AccessModifierOffset: int
ContinuationIndentWidth: unsigned
ConstructorInitializerIndentWidth: unsigned
```

### 2.2 特殊结构缩进

```yaml
IndentCaseLabels: bool
IndentCaseBlocks: bool
IndentGotoLabels: bool
IndentAccessModifiers: bool
IndentWrappedFunctionNames: bool
IndentExternBlock: [AfterExternBlock, NoIndent, Indent]
IndentExportBlock: bool
```

### 2.3 预处理指令缩进

```yaml
IndentPPDirectives: [None, AfterHash, BeforeHash, Leave]
PPIndentWidth: int
```

## 三、函数和参数格式

### 3.1 函数声明和定义

```yaml
BreakAfterReturnType: [Automatic, ExceptShortType, All, TopLevel, AllDefinitions, TopLevelDefinitions]
BreakFunctionDefinitionParameters: bool
```

### 3.2 参数打包和换行

```yaml
BinPackArguments: bool
BinPackParameters: [BinPack, OnePerLine, AlwaysOnePerLine]
BinPackLongBracedList: bool
AllowAllArgumentsOnNextLine: bool
AllowAllParametersOfDeclarationOnNextLine: bool
```

### 3.3 函数调用括号处理

```yaml
AlignAfterOpenBracket: bool
BreakAfterOpenBracketFunction: bool
BreakBeforeCloseBracketFunction: bool
```

## 四、模板和概念

### 4.1 模板声明格式

```yaml
BreakTemplateDeclarations: [Leave, No, MultiLine, Yes]
BreakBeforeTemplateCloser: bool
```

### 4.2 概念和requires子句

```yaml
BreakBeforeConceptDeclarations: [Never, Allowed, Always]
RequiresClausePosition: [OwnLine, OwnLineWithBrace, WithPreceding, WithFollowing, SingleLine]
IndentRequiresClause: bool
RequiresExpressionIndentation: [OuterScope, Keyword]
```

## 五、Lambda表达式

### 5.1 Lambda格式控制

```yaml
AllowShortLambdasOnASingleLine: [None, Empty, Inline, All]
LambdaBodyIndentation: [Signature, OuterScope]
BraceWrapping:
  BeforeLambdaBody: bool
```

## 六、控制语句

### 6.1 条件语句

```yaml
AllowShortIfStatementsOnASingleLine: [Never, WithoutElse, OnlyFirstIf, AllIfsAndElse]
BreakAfterOpenBracketIf: bool
BreakBeforeCloseBracketIf: bool
```

### 6.2 循环语句

```yaml
AllowShortLoopsOnASingleLine: bool
BreakAfterOpenBracketLoop: bool
BreakBeforeCloseBracketLoop: bool
```

### 6.3 switch语句

```yaml
AllowShortCaseLabelsOnASingleLine: bool
AllowShortCaseExpressionOnASingleLine: bool
AlignConsecutiveShortCaseStatements:  # case语句对齐
  Enabled: bool
  AlignCaseArrows: bool
  AlignCaseColons: bool
BreakAfterOpenBracketSwitch: bool
BreakBeforeCloseBracketSwitch: bool
```

## 七、类和结构体

### 7.1 访问修饰符

```yaml
EmptyLineBeforeAccessModifier: [Never, Leave, LogicalBlock, Always]
EmptyLineAfterAccessModifier: [Never, Leave, Always]
IndentAccessModifiers: bool
```

### 7.2 构造函数和继承

```yaml
PackConstructorInitializers: [Never, BinPack, CurrentLine, NextLine, NextLineOnly]
BreakConstructorInitializers: [BeforeColon, BeforeComma, AfterColon]
BreakInheritanceList: [BeforeColon, BeforeComma, AfterColon, AfterComma]
```

### 7.3 位域和成员

```yaml
AlignConsecutiveBitFields:  # 位域对齐
  Enabled: bool
BitFieldColonSpacing: [Both, None, Before, After]
```

## 八、命名空间

### 8.1 命名空间格式

```yaml
NamespaceIndentation: [None, Inner, All]
CompactNamespaces: bool
WrapNamespaceBodyWithEmptyLines: [Never, Always, Leave]
FixNamespaceComments: bool
ShortNamespaceLines: unsigned
```

## 九、预处理指令和宏

### 9.1 包含文件处理

```yaml
SortIncludes:
  Enabled: bool
  IgnoreCase: bool
  IgnoreExtension: bool
IncludeBlocks: [Preserve, Merge, Regroup]
IncludeCategories:  # 包含文件分类
IncludeIsMainRegex: string
IncludeIsMainSourceRegex: string
```

### 9.2 宏定义和格式化

```yaml
AlignConsecutiveMacros:  # 宏定义对齐
AlignEscapedNewlines: [DontAlign, Left, LeftWithLastLine, Right]  # 转义换行对齐
MacroBlockBegin: string  # 宏块开始
MacroBlockEnd: string    # 宏块结束
Macros: list             # 宏定义列表
```

### 9.3 宏特殊处理

```yaml
MacrosSkippedByRemoveParentheses: list  # 跳过括号移除的宏
StatementAttributeLikeMacros: list      # 类似属性的宏
StatementMacros: list                   # 语句宏
WhitespaceSensitiveMacros: list         # 空白敏感宏
```

## 十、注释格式

### 10.1 注释对齐和重排

```yaml
AlignTrailingComments:
  Kind: [Leave, Always, Never]
  OverEmptyLines: unsigned
  AlignPPAndNotPP: bool
ReflowComments: [Never, IndentOnly, Always]
SpacesInLineCommentPrefix:
  Minimum: int
  Maximum: int
SpacesBeforeTrailingComments: unsigned
```

## 十一、操作符和表达式对齐

### 11.1 操作符对齐

```yaml
AlignOperands: [DontAlign, Align, AlignAfterOperator]
BreakBeforeBinaryOperators: [None, NonAssignment, All]
BreakBinaryOperations: [Never, OnePerLine, RespectPrecedence]
BreakBeforeTernaryOperators: bool
```

### 11.2 连续对齐家族

```yaml
AlignConsecutiveAssignments:    # 赋值对齐
AlignConsecutiveDeclarations:   # 声明对齐  
AlignConsecutiveMacros:         # 宏对齐
AlignConsecutiveBitFields:      # 位域对齐
AlignConsecutiveShortCaseStatements: # case语句对齐
```

## 十二、容器和初始化列表

### 12.1 大括号初始化列表

```yaml
Cpp11BracedListStyle: [Block, FunctionCall, AlignFirstComment]
BracedInitializerIndentWidth: int
SpaceBeforeCpp11BracedList: bool
```

### 12.2 数组和结构体数组

```yaml
AlignArrayOfStructures: [Left, Right, None]
BreakArrays: bool
SpacesInContainerLiterals: bool
```

## 十三、指针、引用和限定符

### 13.1 指针和引用对齐

```yaml
PointerAlignment: [Left, Right, Middle]
ReferenceAlignment: [Pointer, Left, Right, Middle]
DerivePointerAlignment: bool
```

### 13.2 限定符处理

```yaml
QualifierAlignment: [Leave, Left, Right, Custom]
QualifierOrder: list  # 必须包含"type"
SpaceAroundPointerQualifiers: [Default, Before, After, Both]
```

## 十四、语言特性和字面量

### 14.1 数字字面量

```yaml
IntegerLiteralSeparator:  # 整数字面量分隔符
  Binary, BinaryMinDigits, Decimal, DecimalMinDigits, Hex, HexMinDigits
NumericLiteralCase:       # 数字字面量大小写
  ExponentLetter, HexDigit, Prefix, Suffix
```

### 14.2 字符串字面量

```yaml
BreakStringLiterals: bool
BreakAdjacentStringLiterals: bool
AlwaysBreakBeforeMultilineStrings: bool
```

### 14.3 语言标准

```yaml
Standard: [c++03, c++11, c++14, c++17, c++20, Latest, Auto]
```

## 十五、文件级和空白控制

### 15.1 行和文件控制

```yaml
ColumnLimit: unsigned  # 0表示无限制
LineEnding: [LF, CRLF, DeriveLF, DeriveCRLF]
InsertNewlineAtEOF: bool
KeepFormFeed: bool
```

### 15.2 空白行控制

```yaml
KeepEmptyLines:
  AtEndOfFile: bool
  AtStartOfBlock: bool
  AtStartOfFile: bool
MaxEmptyLinesToKeep: unsigned
RemoveEmptyLinesInUnwrappedLines: bool
```

### 15.3 制表符使用

```yaml
UseTab: [Never, ForIndentation, ForContinuationAndIndentation, AlignWithSpaces, Always]
TabWidth: unsigned
```

## 十六、特殊语言支持

### 16.1 Objective-C特定配置

```yaml
ObjCBinPackProtocolList: [Auto, Always, Never]
ObjCBlockIndentWidth: unsigned
ObjCBreakBeforeNestedBlockParam: bool
ObjCPropertyAttributeOrder: list
ObjCSpaceAfterProperty: bool
ObjCSpaceBeforeProtocolList: bool
```

### 16.2 JavaScript/Java特定配置

```yaml
InsertTrailingCommas: [None, Wrapped]  # JavaScript尾随逗号
SortJavaStaticImport: [Before, After]  # Java静态导入排序
```

### 16.3 TableGen配置

```yaml
TableGenBreakInsideDAGArg: [DontBreak, BreakElements, BreakAll]
TableGenBreakingDAGArgOperators: list
```

### 16.4 Verilog配置

```yaml
VerilogBreakBetweenInstancePorts: bool
```

## 十七、高级和实验性功能

### 17.1 括号处理

```yaml
RemoveParentheses: [Leave, MultipleParentheses, ReturnStatement]
RemoveSemicolon: bool
```

### 17.2 自动插入和修复

```yaml
InsertBraces: bool
FixNamespaceComments: bool
EnumTrailingComma: [Leave, Insert, Remove]
```

### 17.3 原始字符串和代码块

```yaml
RawStringFormats: list
OneLineFormatOffRegex: string
```

这样的分类更加全面和系统化，涵盖了文档中的所有配置选项，并按照功能相关性进行了合理分组。