---
layout: post
title: cmake的include命令详解
date: 2024-09-05 15:32 +0800
tags: [cmake]
---

## 一、前言

提出一个include命令，很多时候是为了隔离开一些很细节琐碎的内容，然后提供给外部一个一定宏观意义上的功能实现。这样就能够满足接口隔离原则

+ 场景一：我们并不关心一个功能是如何实现的，或者是某些协作者并不关心，他只关心接口能完成什么样的内容。  
+ 场景二：我们想要快速的理清这个cmake构建的过程，那么就可以将一部分内容放置于其他的文件中。  
+ 场景三：我们很有可能使用的是他人提供的或者是cmake官方提供的拓展，此时我们想要使用它的功能的话，就需要include这个模块或者是文件  
+ 场景四：我们很多时候把一些自己定义并且专门处理cmake定义的函数放在一个固定的目录下，例如cmake目录下。然后我们在include这个文件。这个时候需要将当前项目下cmake的目录告诉cmake，在这个目录下还存在着我自己定义的一些cmake命令，命名格式为fileName.cmake，再利用include命令引入。第一步就是list(APPEND CMAKE_MODULE_PATH ${CMAKE_CURRENT_SOURCE_DIR}/cmake)；然后再include(fileName)即可。

## 二、命令介绍  

```cmake
include(<file> [OPTIONAL] [RESULT_VARIABLE <var>] [NO_POLICY_SCOPE])
```

参数介绍：

* <file> 就是表示引入哪一个文件  
* [OPTIONAL]：如果文件不存在，CMake 不会报错, 即include(file.cmake OPTIONAL),这样即使file.cmake不存在的话也不会出问题  
* RESULT_VARIABLE： 包含文件的结果存储在这里。如果文件包含成功，变量会被设置为空字符串，否则会被设置为 NOTFOUND，因此我们判断它是否等于NOTFOUND来判断是否成功读取
* NO_POLICY_SCOPE：包含文件时，不会影响调用者的政策设置，这个没怎么用过  

## 三、执行内容  

在include一个文件的过程中，除了宏定义、函数定义等定义类的命令不会执行之外，其他的都会立即执行。  

### 3.1 立即执行的命令  

这些命令在文件被包含时立即执行，其效果会立即生效：

+ 变量设置：set()

+ 条件判断：if(), elseif(), else(), endif()

+ 循环：foreach(), endforeach(), while(), endwhile()

+ 消息：message()

+ 文件操作：file()

+ 属性设置：set_property(), set_target_properties(), set_source_files_properties()

+ 包含其他文件：include()

+ 增量操作：list(APPEND ...), list(REMOVE_ITEM ...)


### 3.2 不立即执行的命令  

这些命令通常用于定义一些配置或者操作，但是不会立即执行。它们通常在函数或宏被调用时才实际执行：

+ 函数定义：function(), endfunction()

+ 宏定义：macro(), endmacro()

+ 自定义命令：add_custom_command()

+ 自定义目标：add_custom_target()

## 四、举例  

+ 立即执行的命令
    - set(MY_VARIABLE "configured value")
    - message("Config file is included")

+ 定义函数和宏
    - 函数定义  
        ```cmake 
        function(my_function)
            message("Function my_function() is called")
        endfunction()
        ```
    - 宏定义
        ```cmake
        macro(my_macro)
            message("Macro my_macro() is called")
        endmacro()
        ```

