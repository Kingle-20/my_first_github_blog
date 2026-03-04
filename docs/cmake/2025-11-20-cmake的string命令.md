---
layout: post
title: cmake的string命令
date: 2025-11-20 19:48 +0800
tags: [cmake]
toc: true
---

## 一、前言

CMake 的 `string` 命令是一个功能强大的字符串处理工具集，它提供了查找、替换、正则表达式、哈希等二十多种操作。下面我将按照功能分类，详细介绍其常用子命令的语法和用法。

__string 命令通用语法:__

```cmake
string(<操作子命令> [<输出变量>] [<参数>...])
```

+ __操作子命令__：指定要执行的字符串操作，如 `FIND, REPLACE, REGEX` 等。

+ __输出变量__：操作结果会存储在这个变量中。

+ __参数__：操作所需的输入字符串或选项。


## 二、功能分类

### 2.1 搜索与比较

1. __`string(FIND ...)`__  
    + 功能：在字符串中查找子串，返回其索引位置（从0开始），未找到则返回 -1。
    + 语法：`string(FIND <字符串> <子串> <输出变量> [REVERSE])`
    + 示例：  
        ```cmake
        string(FIND "Hello World" "World" index)
        message(STATUS "索引位置: ${index}") # 输出: 6

        string(FIND "abcabc" "a" last_index REVERSE) # 从后往前找
        message(STATUS "最后出现的位置: ${last_index}") # 输出: 3
        ```

2. __`string(COMPARE ...)`__  
    + 功能：比较两个字符串，将比较结果（TRUE/FALSE）存入输出变量。
    + 语法：`string(COMPARE <操作符> <字符串1> <字符串2> <输出变量>)`
    + 操作符：`EQUAL, NOTEQUAL, LESS, GREATER` 等。 
    + 示例：  
        ```cmake
        string(COMPARE EQUAL "abc" "abc" is_equal)
        message(STATUS "字符串是否相等: ${is_equal}") # 输出: TRUE
        ```

### 2.2 修改与转换

1. __`string(REPLACE ...)`__  
    + 功能：将字符串中所有匹配的子串替换为新的内容。
    + 语法：`string(REPLACE <匹配子串> <替换子串> <输出变量> <输入字符串>)`
    + 示例：  
        ```cmake
        string(REPLACE " " ";" result "a b c d")
        message(STATUS "替换后: ${result}") # 输出: a;b;c;d (将空格替换为分号，常用于生成列表)
        ```

2. __`string(REGEX ...)`__  
    这是最强大的功能之一，支持正则表达式。  
    + `string(REGEX MATCH ...)`：匹配第一个结果。  
        ```cmake
        string(REGEX MATCH "[0-9]+" version "Version: 3.14.15")
        message(STATUS "匹配到的数字: ${version}") # 输出: 3
        ```
    + `string(REGEX MATCHALL ...)`：匹配所有结果，输出为列表。  
        ```cmake
        string(REGEX MATCHALL "[0-9]+" all_numbers "Version: 3.14.15")
        message(STATUS "所有数字: ${all_numbers}") # 输出: 3;14;15
        ```
    + `string(REGEX REPLACE ...)`：使用正则表达式进行替换。  
        ```        
        string(REGEX REPLACE ".*([0-9]\\.[0-9]+).*" "\\1" short_version "Version: 3.14.15")
        message(STATUS "主版本号: ${short_version}") # 输出: 3.14
        ```

3. __大小写转换__  
    + `string(TOLOWER <字符串> <输出变量>)`：转换为小写。
    + `string(TOUPPER <字符串> <输出变量>)`：转换为大写。
    + 示例：  
        ```cmake
        string(TOLOWER "Hello CMake" lower_result)
        message(STATUS "小写: ${lower_result}") # 输出: hello cmake
        ```

4. __字符串长度__
    + 功能：`string(LENGTH <字符串> <输出变量>)`
    + 示例：  
        ```
        string(LENGTH "Hello" len)
        message(STATUS "字符串长度: ${len}") # 输出: 5
        ```

5. __子串__
    + 功能：`string(SUBSTRING <字符串> <起始位置> <长度> <输出变量>)`
    + 注意：索引从0开始。
    + 示例：  
        ```
        string(SUBSTRING "Hello World" 6 5 sub)
        message(STATUS "子串: ${sub}") # 输出: World
        ```

### 2.3 前后缀操作

1. __添加/移除前后缀__  
    + `string(PREPEND <变量> [<前缀>...])`：直接修改原变量，为其添加前缀。  
        ```cmake
        set(MY_STR "World")
        string(PREPEND MY_STR "Hello ")
        message(STATUS "添加前缀后: ${MY_STR}") # 输出: Hello World
        ```
    + `string(APPEND <变量> [<后缀>...])`：直接修改原变量，为其添加后缀。  
        ```cmake
        set(MY_STR "Hello")
        string(APPEND MY_STR " World")
        message(STATUS "添加后缀后: ${MY_STR}") # 输出: Hello World
        ```
    + `string(STRIP <字符串> <输出变量>)`：移除字符串首尾的空白字符（空格、制表符、换行符）。  
        ```cmake
        string(STRIP "   CMake   " stripped)
        message(STATUS "去除空白后: '${stripped}'") # 输出: 'CMake'
        ```

### 2.4 编码与哈希

1. __生成哈希值__  
    + 功能：`string(<哈希算法> <输出变量> <输入字符串>)`
    + 哈希算法：`MD5, SHA1, SHA256, SHA384, SHA512`。
    + 示例：
        ```cmake
        string(SHA256 hash_value "Hello CMake")
        message(STATUS "SHA256 哈希: ${hash_value}")
        ```

2. __编解码操作__
    + `string(ASCII <数字> ... <数字> <输出变量>)`：将数字（ASCII码）转换为对应的字符。  
        ```cmake
        string(ASCII 65 66 67 letters)
        message(STATUS "ASCII 码转换: ${letters}") # 输出: ABC
        ```
    + `string(HEX <字符串> <输出变量>)`：将字符串中每个字符转换为对应的十六进制值。  
        ```cmake
        string(HEX "AB" hex_val)
        message(STATUS "十六进制表示: ${hex_val}") # 输出: 4142 (A=41, B=42)
        ```
    + `string(MAKE_C_IDENTIFIER <字符串> <输出变量>)`：将字符串转换为合法的C语言标识符（替换非法字符为下划线）。  
        ```cmake
        string(MAKE_C_IDENTIFIER "my-var.2" identifier)
        message(STATUS "C标识符: ${identifier}") # 输出: my_var_2
        ```

### 2.5 连接与分割列表

+ `string(CONCAT <输出变量> [<字符串1> ...])`：将多个字符串连接成一个。
    ```cmake
    string(CONCAT combined "Hello" " " "CMake")
    message(STATUS "连接后: ${combined}") # 输出: Hello CMake
    ```

+ `string(JOIN <分隔符> <输出变量> [<字符串1> ...])`：用指定分隔符连接多个字符串（或一个列表）。
    ```cmake
    set(my_list a b c d)
    string(JOIN ";" joined_list ${my_list})
    message(STATUS "连接列表: ${joined_list}") # 输出: a;b;c;d
    ```

## 三、实用技巧与注意事项

1. __字符串与列表__：CMake中字符串和列表（分号分隔）容易混淆。`string(REPLACE " " ";" ...) ` 是生成列表的常用方法。
2. __变量作用域__：`PREPEND` 和 `APPEND` 会直接<b>修改</b>原变量，而其他操作通常将结果存入新的输出变量，原变量不变。
3. __正则表达式转义__：在CMake中，正则表达式中的反斜杠 `\` 需要转义为 `\\`（如`\\d`代表数字）。
4. __大小写敏感__：大多数操作`（如FIND, COMPARE）`是大小写敏感的。如需不敏感，可先用 `TOLOWER` 转换。