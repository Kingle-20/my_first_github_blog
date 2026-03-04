---
layout: post
title: cmake的cmake的option命令详解
date: 2025-01-09 15:48 +0800
tags: [cmake]
toc: true
---

## 一、前言  

一个库往往会有各种选择，一些常见的，与选择有关的需求如下：

1. 编译方式灵活性
    + 支持通过同一份CMake配置生成静态库或动态库，无需修改CMakeLists.txt文件。
2. 用户自定义选择
    + 允许用户通过命令行参数（如-DBUILD_SHARED_LIBS=ON/OFF）指定链接方式（静态/动态）。
3. 默认行为兼容性
    + 未明确指定时提供合理的默认编译方式（如默认静态库），避免因缺少输入而报错。
4. 多版本共存支持
    + 支持同时生成静态库和动态库（如分别输出.a和.so/.dll），供用户按需选择。
5. 透明化配置
    + 库的开发者无需为不同链接方式编写重复逻辑，CMake自动处理差异（如符号可见性、编译选项）。


因此，针对上面的需求，cmake提供option命令，它表示了可以设置默认cmake的布尔值（ON/OFF）。库的使用者只需要根据库作者的参考文件，不同修改库的文件，直接通过命令：

```powershell
cmake -DENABLE_VAR=ON 
```

即可影响这个库的option命令设置的ENABLE_VAR变量的值，从而控制整个库的行为。

## 二、语法介绍  

语法格式如下：

```cmake
option(OPTION_NAME "Description of the option" [initial value])
```

1. __OPTION_NAME: 选项的名称。通常是一个大写字母的字符串，以表示它是一个 CMake 选项。__  

2. __"Description of the option": 对选项的简短描述。该描述将在配置过程中的 CMake GUI 或命令行工具中显示。__  

3. __[initial value]: 选项的初始值，可以是 ON 或 OFF。如果未指定，默认值为 OFF。__  

## 三、应用举例  

### 3.1 宏定义的方式

笔者想到的有两种方式影响编译。第一种就是根据宏定义，然后通过增加宏定义的方式来控制整个编译：

1. 全局作用域上的添加宏定义
    ```cmake 
    add_definitions(-DMACRO_NAME=VALUE)
    ```
2. 针对特定目标增加宏定义  
    ```cmake 
    target_compile_definitions(target_name PUBLIC/PRIVATE/INTERFACE MACRO_NAME=VALUE)
    ```

那么在源文件中就有：

```c++
#ifdef MACRO_NAME
    func1();
#else 
    func2();
#endif
```

通过这样方式来控制编译运行。  

### 3.2 c++17以后方式（笔者推荐）

现在c++的if constexpr命令语句能够实现编译期设置库资源。那么我们就可以这样方式

* 第一步，将CMakeLists.txt中生成一个配置头文件。  
* 第二步，将配置头文件包含到要影响的源代码文件中。  
* 第三步，使用if constexpr控制编译。  

## 四、配置头文件

### 4.1 转换方案

如何利用cmake生成配置头文件呢？cmake中有一个工具是根据模板文件，将模板文件中的内容替换为实际的内容。因此我们可以利用这个特性来实现生成配置头文件。
> + 模板文件与一般文件不同点为，模板文件中包含了@TEMPLATE_VAR@，通过双@包含的一个变量名。
> + 其工作原理是：__读取前面设置的变量，然后将模板文件中@TEMPLATE_VAR@这些变量里面存储的字符串__。
> + 假设我们在CMakeLists.txt的前面部分使用option命令或者是set命令设置了变量名，如set(var1 "999"),那么在模板文件中，有一条语句`int x = @var1@`，那么var1就会被替换999。

那么如何结合option来生成配置头文件呢？一个解决思路是，将option的值转化为cmake中的一个字符串变量，然后再使用configue_file命令，利用模板文件中这个变量的形参替换为实参，从而生成配置头文件。

### 4.2 值得注意的问题

+ 问题1：option中是on或者是off的字符，需要转换为c++中的bool值。
    ```cmake
    #[[
    @brief 将cmake中的option命令的on和off转化为c/c++中的true/false字样的字符串

    @param cmake_bool cmake中的on或者off  
    @param c_or_cplusplus_bool 存储在true/false的变量
    ]]
    function(ConvertOptionToBool cmake_bool c_or_cplusplus_bool)
        if (${cmake_bool})
            set(${c_or_cplusplus_bool} "true" PARENT_SCOPE)
        else()
            set(${c_or_cplusplus_bool} "false" PARENT_SCOPE)
        endif()
    endfunction()
    ```
+ 问题2：由于cmake在配置之后就不会再次配置，因此我们需要每次运行时，强制让cmake重新进行配置
    ```cmake
    #[[
    @brief 根据cmake的模板文件生成相应的配置文件

    @param ConfigureTemplateFile 使用的配置模板文件（需要包含路径）  
    @param GenerateFileName 生成的配置文件所在位置 （需要包含路径）
    ]]
    function(RegenerateConfigFunction ConfigureTemplateFile GenerateFileName)
        # 如果 binary_path 存在，删除该文件
        if (EXISTS ${GenerateFileName})
            file(REMOVE ${GenerateFileName})
            message(STATUS "Removed ${GenerateFileName}")
        endif()

        # 配置文件替换
        configure_file(
            ${ConfigureTemplateFile}
            ${GenerateFileName}
        )
    endfunction()
    ```
+ 问题三：由于cmake都是调用后端的makefile或者是ninja进行编译，他们的特性是根据当前文件修改时间和编译时间来判断是否需要重新编译。因此，需要解决当配置文件发生变化时，才修改配置头文件。
    ```cmake
    #[[
    @brief 比较GenerateFile文件是否与原文件是否一样，如果不一样就从原文件复制一份

    @param OriginalFile 使用的配置模板文件（需要包含路径）  
    @param GenerateFileName 生成的配置文件所在位置 （需要包含路径）
    ]]
    function(CompareAndSyncConfig OriginalFile GenerateFile)
        if (EXISTS ${OriginalFile} AND EXISTS ${GenerateFile})
            # 读取文件内容
            file(READ ${OriginalFile} CONTENT_OriginalFile)
            file(READ ${GenerateFile} CONTENT_GenerateFile)

            # 比较文件内容
            if (NOT "${CONTENT_OriginalFile}" STREQUAL "${CONTENT_GenerateFile}")
                file(REMOVE ${GenerateFile})    
                file(COPY ${OriginalFile} DESTINATION ${GenerateFile})
                message(STATUS "Configurations do not match")
            else()
                message(STATUS "Configurations match")
            endif()
        else()
            if (EXISTS ${OriginalFile})
                file(COPY ${OriginalFile} DESTINATION ${GenerateFile})
                message(STATUS "Configuration file synced: ${GenerateFile}")
            else()
                message(FATAL_ERROR "One or both configuration files do not exist.")
            endif()
        endif()
    endfunction()
    ```

总结一下上面三个函数的作用：

1. ConvertOptionToBool，这个函数是将option函数设置的变量转化为字符串化的true或者是false；
2. 第二个命令是每一次运行cmake编译时，都会重新生成一个配置头文件副本；
3. 第三个命令是将重新生成的头文件副本和之前的文件比较，如果一模一样的话，不会进行任何操作，否则拷贝到相应的位置。

### 4.3 整体流程示例

+ 第一步，生成配置头文件：
    1. 构造模板模板头文件
        ```cmake
        #ifndef CONFIG_H
        #define CONFIG_H
        namespace RobotOption{
        constexpr bool k_UserFeature = @USE_FEATURE_X_VALUE@;
        };
        #endif // CONFIG_H
        ```
    2. 编写CmakeLists.txt，需要包含option和调用转换过程
        ```cmake
        option(USE_FEATURE_X "Enable Feature X" OFF)
        set(USE_FEATURE_X_VALUE)

        ConvertOptionToBool(USE_FEATURE_X USE_FEATURE_X_VALUE)
        RegenerateConfigFunction("${CMAKE_CURRENT_SOURCE_DIR}/config.h.in" "${CMAKE_CURRENT_BINARY_DIR}/config.h")
        CompareAndSyncConfig( "${CMAKE_CURRENT_BINARY_DIR}/config.h" "${CMAKE_CURRENT_SOURCE_DIR}/config.h")
        ```

+ 第二步，使用#include命令包含这个头文件
    ```c
    #include "config.h"
    ```

+ 第三步， 使用条件编译  
    ```c++
    void func1(void) {
        if constexpr (RobotOption::k_UserFeature) {
            //do something
        } else {
            //do something
        }
    }
    ```

## 五、后记

使用if constexpr的方式，可以将生成的配置头文件包含到所需要的源文件中，这样当配置项改变时，能够明显缩短编译时间。  
