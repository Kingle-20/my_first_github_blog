---
layout: post
title: powershell快速入门
date: 2025-05-28 18:48 +0800
tags: [ps1]
math: true
---

一般而言，图灵机被描述为数据结构+算法。既然如此，一门新的语言必然要提供如何描述数据以及操作数据的方法。而有些操作比较麻烦复杂，因此一般编程语言就将这些复杂操作或者是难以用本语言描述的功能通过库的方式提供给使用者。因此我们整个架构分为了三个部分：基础语法，函数定义以及powershell提供的库的逻辑。

## 一、基础语法

### 1.1 变量与数据类型

#### 1.1.1 变量定义

powershell和其他常见的脚本语言一样，并没有对定义变量时强制要求变量类型，但是，它也提供了强制指定变量类型的方式。

+ `$varname`，使用`$`前缀，后面就是变量名。
+ `[typename] $varname`，强制指定变量名的类型。
+ `$arr = 1, "two", 3.0`，定义数组，它支持不同类型的数据放到一个数组中。

#### 1.1.2 变量使用

`$varname`放在等式左边就是赋值，放在右边就是读取这个变量的值。使用这个变量需要带上`$`符号。

#### 1.1.3 强制类型转换

通过`[typename]`来对变量进行强制转化，`[type] $var`（如 `[datetime]"2025-01-01"`），powershell支持以下类型：

+ 基础数值类型：
```ps1
[int] $i = 10          # 32位整数
[long] $l = 100L       # 64位整数
[float] $f = 3.14f     # 单精度浮点数
[double] $d = 3.14     # 双精度浮点数（默认小数类型）
[decimal] $m = 3.14m   # 高精度十进制数（适合财务计算）
```
+ 其他常用类型:
```ps1
[string] $s = "Hello"  # 字符串
[char] $c = 'A'        # 单个字符
[bool] $b = $true      # 布尔值
[datetime] $dt = Get-Date # 日期时间
[array] $arr = 1,2,3   # 数组
[hashtable] $ht = @{}  # 哈希表
```
+ 特殊类型：
```ps1
[version] $v = "1.2.3" # 版本号
[guid] $guid = [guid]::NewGuid() # GUID
[xml] $xml = "<root></root>" # XML文档
```

注意事项：
1. PowerShell 默认会尝试自动类型转换：
```ps1
[int] $num = "123" # 字符串会自动转为整数
```
2. 类型检查是运行时进行的：
```ps1
[int] $i = "abc" # 运行时会抛出异常
```
3. 可以使用`::MaxValue/::MinValue` 查看范围：
```ps1
[int] $i = "abc" # 运行时会抛出异常
```
4. 对于更复杂的类型（如自定义类），需要先加载包含该类型的程序集.

虽然 PowerShell 支持强类型声明，但它本质上仍然是动态类型语言，类型检查发生在运行时而非编译时。

### 1.2 运算符

+ 算术/逻辑：
    - `+-*/ % `，加减乘除。
    - `-and -or -not`，与或非。
    - `-eq` 等于， `-ne`不等于， `-ceq` 区分大小写的等于, `-cne` 区分大小写的不等于。
    - `-gt`（大于）, `-ge`（大于等于）, `-lt`（小于）,`-le`（小于等于）。
+ 匹配运算符
    - -like（通配符匹配，如 "file*"）、-notlike
    - -match（正则表达式匹配）、-notmatch
    - -contains（集合包含）、-notcontains
    - -in（值在集合中）、-notin
+ 类型检查
    - -is（类型匹配，如 $var -is [string]）、-isnot
+ 位运算符
    - -band（按位与）、-bor（按位或）
    - -bxor（按位异或）、-bnot（按位取反）
    - -shl（左移）、-shr（右移）
+ 字符串拼接
    - `+`（连接字符串）
    - -join（合并数组为字符串）

+ 数组操作
    - -split（分割字符串为数组）、
    - -replace（替换字符串）
    - ..（范围运算符，如 1..5 生成 1,2,3,4,5）

+ 属性/方法调用
    - .（访问属性或方法，如 $obj.Property）
    - ::（静态方法调用，如 [DateTime]::Now）
    - `[]`访问.NET对象符号

+ 管道与重定向
    - |（管道）、
    - `>`（输出到文件）、
    - `>>`（追加到文件）

+ 特殊运算符
    - $()（子表达式）、
    - @()（数组初始化）
    - &（调用命令或脚本块）、
    - ?.（空条件运算符，PowerShell 7+）

+ 特殊运算符：
```ps1
-is     # 类型检查（如 `$i -is [int]`）
-as     # 安全转换（类似`dynamic_cast`）
-join   # 字符串拼接（`-join (1..3)` → "123"）
```

### 1.3 控制流

+ 分支：
```ps1
if ($x -gt 10) { ... } 
elseif (...) { ... }   # 注意无 `else if`
else { ... }
```
+ 循环：
```ps1
foreach ($item in $collection) { ... }  # 范围：`1..10`
while ($condition) { ... }
do { ... } until ($condition)
```

## 二、函数

### 2.1 基础函数
```ps1
function Add-Numbers {
    param ([int]$a, [int]$b)
    return $a + $b
}
```

对比C++：无返回类型声明，参数通过param块定义

### 2.2 管道输入
```ps1
function Get-Square {
    process { $_ * $_ }  # $_ 是管道当前对象
}
1..3 | Get-Square        # 输出 1, 4, 9
```

## 三、 核心库与对象操作

在powershell中基本都是通过cmdlet提供库的功能，其底层是.net对象。由于微软的主要设计方向是.NET化，通过.net来与操作系统交互，最终，他们花费了很大的努力搞出了一堆东西。那么开发一种脚本语言的时候就想能不能直接使用.NET的成果呢，那么它们就提出将这些.net对象包装一下，然后写脚本的人更好方便使用，然后就提出了cmdlet这个概念。cmdlet这个概念类似于遥控器与电视的关系，我们通过cmdlet就可以操作电视机了，而在脚本中，这个电视机就是操作系统。通过cmdlet返回的就是.net对象。

### 3.1 .NET互操作
直接调用.NET：
```ps1
[System.IO.File]::WriteAllText("test.txt", "Hello")  # 静态方法
$list = [System.Collections.Generic.List[int]]::new() # 构造函数
```

### 3.2 常用cmdlet

cmdlet有很多，在powershell中常常直接介绍的就是如何操作这些cmdlet，而且这一部分非常的多，也不可能把所有的学习，只是说使用的时候问问AI，某个功能可以用哪个cmdlet实现。而且很多类功能是后续不断开发的，它们在版本升级时就引入了，而且其他人也提供了一些cmdlet，可以从github这些地方下载这些拓展包。

### 3.3 流式处理

powershell也提供将上一个结果传递给下一个处理的入参，仿照如下：
```ps1
1..10 | Where-Object { $_ % 2 -eq 0 } | ForEach-Object { $_ * 10 }
```
对比C++：类似ranges::filter + ranges::transform。

## 四、高级特性

### 4.1 错误处理

使用try-catch结构处理：
```ps1
try { 1/0 }
catch [System.DivideByZeroException] { Write-Host "除零错误" }
finally { ... }

```

### 4.2 并发与作业

1. 后台作业
```ps1
Start-Job { Get-Process } | Receive-Job -Wait
```
2. 并行管道：
```ps1
1..100 | ForEach-Object -Parallel { $_ * 2 } -ThrottleLimit 5
```

### 4.3 自定义类

```ps1
class Rectangle {
    [int] $Width
    [int] $Height
    Rectangle([int]$w, [int]$h) { $this.Width = $w; $this.Height = $h }
    [int] Area() { return $this.Width * $this.Height }
}
```

## 五、实战工具

### 5.1 参数化脚本

在 PowerShell 中，参数化脚本（Parameterized Scripts） 是指通过定义参数使脚本能够接收外部输入，从而增强脚本的灵活性和可重用性。其核心是通过 param 块声明参数，类似于函数参数的定义方式。

#### 5.1.1 基础参数化脚本示例

+ 创建一个名为 Demo-Script.ps1 的文件
```ps1
# 脚本开头的 param 块定义参数
param (
    [string]$Name = "默认值",
    [int]$Count = 1
)
# 使用参数
for ($i = 1; $i -le $Count; $i++) {
    Write-Output "Hello, $Name (第 $i 次)"
}
```
+ 调用方式
```
# 按参数名传递
.\Demo-Script.ps1 -Name "Alice" -Count 3

# 按位置传递（需与param块中顺序一致）
.\Demo-Script.ps1 "Bob" 2

# 使用默认值
.\Demo-Script.ps1
```
#### 5.1.2 高级参数特性

1. 强制参数Mandatory
```ps1
param (
    [Parameter(Mandatory=$true)]
    [string]$RequiredParam
)
```
如果未提供该参数，PowerShell 会提示用户输入。

其中`[Parameter(Mandatory=$true)]`表示强制要求提供参数的请求，但是它单次有效，即
```ps1
param (
    [Parameter(Mandatory=$true)]  # 仅强制此参数
    [string]$Name,
    
    [int]$Age = 18               # 非强制，有默认值
)
```
它只标记`$Name`变量强制，不强制下面一个
2. 参数验证
```ps1
param (
    [ValidateRange(1, 100)]
    [int]$Percentage,

    [ValidateSet("Low", "Medium", "High")]
    [string]$Priority
)
```
3. 开关参数（Switch）
```ps1
param (
    [switch]$Force  # 不需要值，存在即为$true
)
if ($Force) { Write-Output "强制模式已启用" }
```
调用时使用 -Force 而不需要指定值。
4. 管道输入
```ps1
param (
    [Parameter(ValueFromPipeline=$true)]
    [string]$InputText
)
process {
    $InputText.ToUpper()
}
```
可通过管道调用：
```
"text" | .\Demo-Script.ps1
```

### 模块发布

这一部分不太懂后续补充。

