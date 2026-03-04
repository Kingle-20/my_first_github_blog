---
layout: post
title: cmake的cmake的target概念
date: 2025-01-15 15:48 +0800
tags: [cmake]
toc: true
---

## 一、前言

在现代cmake中，核心概念包括目标（target）以及目标属性和依赖的传播机制。通过目标之间进行属性(property)的传播。而属性就定义了整个包是如何进行构建的。  

## 二、目标（Target）概念

目标是指工程中需要构建的独立项目组件，可以是库（静态或者动态）、可执行文件等。

1. 目标通常使用 add_library 或 add_executable 等命令创建。  
2. 这个概念是将所需要编译或者是安装的资源生成一个统一体，生成具有归属权的目标，以便于管理。
    - 比如说，我有一个库liba.a，它有一些操作，和相应的属性，那么这个属性不需要其他使用这个库的人操作。
    - 当其他人想要使用这个库lib.a时，就直接使用某个命令,即(target_link_libraries)，然后lib.a中的属性传递给使用者，使用者并不关心这个库需要什么条件。

## 三、Target类型

一般而言，编译后都是二进制类型的，所以这些生成的二进制产物在默认情况下会有跟平台相关的前缀(PREFIX)和后缀(SUFFIX)。

什么是前缀和后缀呢？假设我们在unix平台下

```cmake
add_library(MyLibrary STATIC src/mylibrary.cpp)
```

这句话会生成的库文件通常会是 libMyLibrary.a，这里 lib 是默认前缀，而后缀就是.a。我们可以使用set_target_properties来修改相应的前缀和后缀。

二进制Target一般来说分为了两种：

1. 二进制可执行文件。使用add_executable命令生成。

2. 二进制库。
    - 使用add_library命令添加。
      ```cmake
      add_library(<name> [<type>] [EXCLUDE_FROM_ALL] <sources>...)
      ```
    - 其中，第二个参数`[<type>]`指定了库的类型。

库的类型有如下几种：

1. STATIC 静态库

2. SHARED 动态库

3. MODULE 动态加载库。动态加载库主要是程序运行期间，使用与操作系统相关的api动态解析相应的符号。例如下面
    ```c++
    void* handle = dlopen("path/to/your/library.so", RTLD_LAZY);  //使用操作系统api动态加载
    void (*func)() = (void (*)())dlsym(handle, "function_name");  //然后解析出相应的符号
    dlclose(handle);  //关闭动态加载句柄。
    ```
    + 具体可参考[Cmake MODULE模块库](https://zhuanlan.zhihu.com/p/661281489)  
    + 它和动态库的主要区别是，它不可以被target_link_libraries命令链接。
    + 而如果没有`[<type>] `被指定的话，那么cmake根据BUILD_SHARED_LIBS变量决定。

4. OBJECT 对象库。对象库本身并不生成一个归档文件，需要将其目标文件添加到另一个库或可执行文件。对象库可以设置和使用与其他库相同的目标属性。
    + 示例一：
        ```cmake
        add_library(my_object_library OBJECT source1.cpp source2.cpp) #添加对象库
        add_executable(my_executable $<TARGET_OBJECTS:my_object_library>) #添加可执行文件时直接添加到库或者可执行文件中
        add_library(my_shared_library SHARED $<TARGET_OBJECTS:my_object_library>)
        ```
    + 示例二：
        ```cmake
        add_library(archive OBJECT archive.cpp zip.cpp lzma.cpp)

        add_library(archiveExtras STATIC extras.cpp)
        target_link_libraries(archiveExtras PUBLIC archive)

        add_executable(test_exe test.cpp)
        target_link_libraries(test_exe archive)
        ```

__在cmake构建系统中，目标的构建是根据它们自身的构建规范，结合从链接依赖项中传播的使用要求来进行的。这两者都可以通过特定于目标的命令来指定。__  

因此，对象库的使用要求不仅仅在目标文件生成过程中应用，它们还会传播到使用这些对象文件的其他目标上。


## 四、PUBLIC、PRIVATE、INTERFACE的属性设置

1. __为什么需要提出这个？__
    + 根据前面所述，cmake的target在使用过程中具有传播性。
    + 因此为了控制传播性，就需要告诉，哪些属性是仅自己使用，哪些是给别人使用，哪些是大家一起使用，因此提出了上面的三种传播性质。
    + 这些关键词用于目标的属性设置，控制属性在项目内部和外部的可见性和可用性，关键是依赖的传播。

2. __这三种属性设计的意义是什么？__
    + PUBLIC：属性对当前目标可见，同时也传播给使用该目标的依赖目标。例如，当设置 target_include_directories 为 PUBLIC 时，包含目录会同时加入到依赖于这个目标的其它目标中。
    + PRIVATE：属性仅对当前目标可见，不传播给依赖目标。
    + INTERFACE：属性本身不对当前目标生效，仅传播给依赖目标。这通常用于INTERFACE库，即不包含编译行为的库。

## 五、Target Build Specification

二进制目标的构建规范由目标属性表示。每个编译和链接属性不仅受到自身值的影响，还受到对应的使用要求属性（以 INTERFACE_ 前缀命名），这些属性是从链接依赖的传递闭包中收集的。  

### 5.1 target编译属性  

1. COMPILE_DEFINITIONS 编译宏定义
    + 目标中用于编译源代码的编译定义列表。这些定义会以 -D 标志或同等方式传递给编译器，但顺序不固定。
    + 作为 SHARED 和 MODULE 库目标的一种特殊便利情况，DEFINE_SYMBOL 目标属性也被用作编译定义。

2. COMPILE_OPTIONS 编译选项  
    + 目标中用于编译源代码的编译选项列表。这些选项会作为标志按出现的顺序传递给编译器。

3. COMPILE_FEATURES 编译特性  
    + 目标中用于编译源代码所需的编译特性列表。通常，这些特性确保目标的源代码使用足够的语言标准级别进行编译。

4. INCLUDE_DIRECTORIES 包含的头文件。

5. SOURCES 源文件 与目标关联的源文件列表。

6. PRECOMPILE_HEADERS 预编译头文件。

7. AUTOMOC_MACRO_NAMES 主要使用在qt中。

8. AUTOUIC_OPTIONS 主要使用在qt中。

### 5.2 target链接属性

1. LINK_LIBRARIES
    + 对于可执行文件、共享库或模块库，链接器会根据链接库列表来找到它们。普通库会通过它们的路径或 `-l` 标志传递给链接器，而对象库会通过它们的对象文件路径传递。
    + 在编译和链接目标时，所需的使用需求从所有相关的普通库、接口库、对象库和导入目标中收集，并通过它们的 `INTERFACE_LINK_LIBRARIES` 属性传播。

2. LINK_DIRECTORIES  
    + 它用于为可执行文件、共享库或模块库的链接目标指定链接目录列表。

3. LINK_OPTIONS 
    + 它可以用于为可执行文件、共享库或模块库指定链接选项。
    + 这些选项将按照出现的顺序传递给链接器。一般在设置目标属性或者使用目标相关命令时使用。

4. LINK_DEPENDS  
    + CMake 中一种用于管理目标链接时的依赖文件文件列表的属性。
    + 这些依赖文件可能包括链接器脚本等特定的文件，它们的变化将触发重新链接目标文件（如可执行文件、共享库或模块库）。
    + 通过指定这些依赖文件，可以确保当这些文件发生修改时，CMake 能够正确地重新链接相关目标。  

## 六、属性传递性以及使用要求

目标的使用需求是通过 `target_link_libraries()` 连接目标时传递给消费者的设置，这些设置确保其可以正确编译和链接，并且它们通过传递性编译和链接属性来表现。

例如，如果目标 `A` 链接到目标 `B`，那么 `B` 的一些编译和链接设置（如包含目录、编译选项）会传递给 `A`。这些传递的属性代表了编译和链接时的各类设置（例如：包含目录、编译定义、链接库等），它们会自动从一个目标传播到其他使用它的目标。

请注意，使用需求的设计并不是为了让下游目标为了便利性而使用特定的 `COMPILE_OPTIONS`、`COMPILE_DEFINITIONS` 等。属性的内容必须是需求，而不仅仅是建议。

例如，如果某个编译选项是必须的（比如 `-D` 定义了某个宏），那么这个才是使用需求；如果只是方便使用而设定某个编译选项，这并不应当作为必需的使用需求。使用需求必须是实际编译和链接所必需的属性，而不是提供给使用者的建议性的方便性功能。

通常，如果一个依赖项仅在库的实现中使用，而不在头文件中使用，那么它应该在使用 `target_link_libraries()` 时用 `PRIVATE` 关键字指定。

如果一个依赖项也在库的头文件中使用（例如，用于类继承），那么它应该被指定为 `PUBLIC` 依赖项。如果一个依赖项并不在库的实现中使用，而仅在其头文件中使用，那么它应该被指定为 `INTERFACE` 依赖项。`target_link_libraries()` 命令可以多次使用每个关键字。 

使用要求通过读取依赖项的目标属性的 INTERFACE_ 变体并将值附加到操作数的非 INTERFACE_ 变体来传播。例如，读取依赖项的 INTERFACE_INCLUDE_DIRECTORIES 并将其附加到操作数的 INCLUDE_DIRECTORIES 中。在顺序相关且需要维护的情况下，如果 target_link_libraries() 调用导致的顺序不允许正确编译，可以使用适当的命令直接设置属性以更新顺序。例如，如果目标的链接库必须按照 lib1 lib2 lib3 的顺序指定，但包含目录必须按照 lib3 lib1 lib2 的顺序指定。

```cmake
target_link_libraries(myExe lib1 lib2 lib3)
```

## 六、传递性属性

编译属性和链接属性，均会被INTERFACE_PROPERTY_NAME传递。

### 6.1 编译属性

具体如下：

1. INTERFACE_COMPILE_DEFINITIONS
    + 用于编译目标消费者的源代码的编译定义列表。通常这些定义由目标的头文件使用。

2. INTERFACE_COMPILE_OPTIONS
    + 用于编译目标消费者的源代码的编译选项列表。

3. INTERFACE_COMPILE_FEATURES
    + 编译目标消费者的源代码所需的编译特性列表。通常这些特性用于确保在使用足够的语言标准级别编译消费者时处理目标的头文件。

4. INTERFACE_INCLUDE_DIRECTORIES
    + 用于编译目标消费者的源代码的包含目录列表。通常这些是目标头文件的位置。

5. INTERFACE_SYSTEM_INCLUDE_DIRECTORIES
    + 当指定为包含目录时，例如通过 INCLUDE_DIRECTORIES 或 INTERFACE_INCLUDE_DIRECTORIES，应在编译目标消费者的源代码时将其视为“系统”包含目录的目录列表。

6. INTERFACE_SOURCES
    + 与目标消费者关联的源文件列表。

7. INTERFACE_PRECOMPILE_HEADERS
    + 在编译目标消费者的源代码时预编译并包含的头文件列表。

8. INTERFACE_AUTOMOC_MACRO_NAMES
    + AUTOMOC 用于确定目标消费者的C++源代码是否需要由moc处理的宏名称列表。

9. INTERFACE_AUTOUIC_OPTIONS
    + AUTOUIC在为目标消费者调用uic时使用的选项列表。

### 6.3 链接属性

1. INTERFACE_LINK_LIBRARIES
    + 用于将目标消费者（如可执行文件、共享库或模块库）与链接库连接的链接库列表。这些是目标的传递依赖项。
    + 此外，为了编译和链接目标的消费者，使用需求是从命名常规库、接口库、对象库和导入目标的 INTERFACE_LINK_LIBRARIES 条目的传递关闭中收集的。

2. INTERFACE_LINK_DIRECTORIES
    + 用于将目标消费者（如可执行文件、共享库或模块库）与链接目录列表连接的链接目录列表。

3. INTERFACE_LINK_OPTIONS
    + 用于将目标消费者（如可执行文件、共享库或模块库）与链接选项连接的链接选项列表。

4. INTERFACE_LINK_DEPENDS
    + 链接目标消费者所依赖的文件列表（对于那些可执行文件、共享库或模块库）。

## 七、设置target属性的方法

### 7.1 set_target_properties函数

用于设置目标的属性。多个属性可以一起设置，每个属性用键值对表示。
```CMAKE
set_target_properties(target
  PROPERTIES
    PROPERTY1 VALUE1
    PROPERTY2 VALUE2
)
```

### 7.2 target_compile_definitions

用于为特定目标设置编译器定义，可以指定是PUBLIC、PRIVATE 还是 INTERFACE。

```CMAKE
target_compile_definitions(target
  PUBLIC
    MY_DEFINITION
  PRIVATE
    MY_PRIVATE_DEFINITION
)
```

### 7.3 target_compile_features

用于设置目标所需的编译特性，例如指定 C++ 标准。特性会自动转换为编译器选项。

```CMAKE
target_compile_features(target
  PRIVATE
    cxx_std_17
)
```

### 7.4 target_compile_options

用于为目标设置编译器选项。支持设置 PUBLIC、PRIVATE 和 INTERFACE。

```CMAKE
target_compile_options(target
  PRIVATE
    -Wall -Wextra
)
```

### 7.5 target_include_directories

用于设置目标的包含目录。支持设置 PUBLIC、PRIVATE 和 INTERFACE。

```CMAKE
target_include_directories(target
  PUBLIC
    ${CMAKE_CURRENT_SOURCE_DIR}/include
  PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/src
)
```

### 7.6 target_link_directories

用于为目标添加链接目录。注意这不是非常常用，通常使用 target_link_libraries 处理依赖关系。

```CMAKE
target_link_directories(target
  PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/lib
)
```

### 7.7 target_link_libraries

用于指定目标需要链接的库，同样支持 PUBLIC、PRIVATE 和 INTERFACE。通常推荐的使用方式。

```CMAKE
target_link_libraries(target
  PRIVATE
    libA
  PUBLIC
    libB
)
```

### 7.8 target_link_options

用于为目标设置链接器选项。支持 PUBLIC、PRIVATE 和 INTERFACE。

```CMAKE
target_link_options(target
  PRIVATE
    -Wl,--start-group
  PUBLIC
    -L/path/to/library
)
```

### 7.9 target_precompile_headers

用于为目标设置预编译头，能够显著加快编译速度。

```CMAKE
target_precompile_headers(target
  PRIVATE
    pch.hpp
)
```

### 7.10 target_sources

用于明确指定目标的源文件。支持设置 PUBLIC、PRIVATE 和 INTERFACE。

```CMAKE
target_sources(target
  PRIVATE
    src/main.cpp
  PUBLIC
    include/header.hpp
)
```

一般来说，我们在创建目标时，就可以其后设置源文件，从而向这个target添加相应的文件。一般来说，使用target_sources命令往往看起来很麻烦，但是它主要解决当需要能够单独添加文件的情况，或者是手动管理每一个文件的具体情节。

+ 当我们想要根据条件判断是否将某一个文件添加到Target中进行编译；
+ 当我们控制某些头文件的的访问属性，比如说某些头文件是给别人用的，有些头文件是仅给自己使用的，有一些是给共同使用的。

在CMAKE版本3.23之后，对target增加了一个HEADER_SET的属性，即头文件集合的概念。与此相关的还有HEADER_DIRS这个属性，该属性主要描述了头文件集的路径。cmake官方并不推荐我们直接对这些属性直接操作，而是使用target_sources命令进行直接操作。  

```cmake
target_sources(target
  PUBLIC
    FILE_SET HEADERS
    BASE_DIRS ${CMAKE_SOURCE_DIR}/lib/
    FILES ${CMAKE_SOURCE_DIR}/lib/internal/MyLibraryInternal.h
)
```

首先使用FILE_SET表示这是一个文件集合，后面紧跟HEADERS表示正在设置头文件集。FILE_SET可以设置的值有两个：

+ HEADERS，表示头文件集合。
+ CXX_MODULES，这个描述的是c++的模块的源文件。

值得注意的是，HEADERS目前只能够被一种作用域所修饰，不能设置多个作用域，否则cmake会迷惑。如下写法就是错误的：

```cmake
target_sources(target
  PUBLIC
    FILE_SET HEADERS
    BASE_DIRS ${CMAKE_SOURCE_DIR}/lib/
    FILES ${CMAKE_SOURCE_DIR}/lib/internal/MyLibraryInternal.h
  INTERFACE
    FILE_SET HEADERS
    BASE_DIRS ${CMAKE_SOURCE_DIR}/include/
    FILES ${CMAKE_SOURCE_DIR}/include/MyLibrary.h
)
```

紧接着的是BASE_DIRS说明符，这个表示截取的路径。

然后就是FILES表示某一个具体的文件。

FILES文件中包含了整个完整的路径，那么此时已经能够告诉cmake这个文件在哪里了，但是为什么还要增加一个BASE_DIRS呢？实际上存在这样的功能需求：假设我要把FILE_SET中某一个文件安装到某一个位置，另外一个位置是另外一个位置。那么这个时候cmake通过BASE_DIRS截取掉FILES中的多余的路径。例如

```cmake
  BASE_DIRS ${CMAKE_SOURCE_DIR}/
  FILES ${CMAKE_SOURCE_DIR}/include/MyLibrary.h
```

假设我安装到dir目录下，那么它的效果就是

```
dir/include/MyLibrary.h
```

同样的，选择不同的BASE_DIRS的话，如：

```cmake
  BASE_DIRS ${CMAKE_SOURCE_DIR}/include/
  FILES ${CMAKE_SOURCE_DIR}/include/MyLibrary.h
```

就会安装到

```
dir/MyLibrary.h
```

目前来看，这个主要就是能够控制每一个文件的安装位置。

当然，可以使用PUBLIC_HEADER属性，通过命令set_target_properties将头文件设置到target中，然后使用

```cmake
install( 
  Target_name
  EXPORT Target_name-export 
  PUBLIC_HEADER DESTINATION include
  ARCHIVE DESTINATION lib
  LIBRARY DESTINATION lib
  RUNTIME DESTINATION bin
)
```

将头文件安装到指定位置。  

## 八、伪目标

在构建系统中，一些目标类型并不表示构建系统的输出，而只是输入，诸如外部依赖项、别名或其他非构建工件。这些伪目标在生成的构建系统中没有表示。

### 8.1 IMPORTED目标 

先来看看官方的论述：

> *****
> 在 CMake 构建系统中，IMPORTED 目标表示一个已存在的依赖项。通常，这些目标由上游包定义，应该被视为不可更改的实体。
> 
> 在声明一个 IMPORTED 目标后，可以像处理其他常规目标一样，通过使用惯常的命令来调整其目标属性，例如 `target_compile_definitions()`、`target_include_directories()`、`target_compile_options()` > 或 `target_link_libraries()`。

> IMPORTED 目标可以填充值与二进制目标相同的使用要求属性，例如 `INTERFACE_INCLUDE_DIRECTORIES`、`INTERFACE_COMPILE_DEFINITIONS`、`INTERFACE_COMPILE_OPTIONS`、`INTERFACE_LINK_LIBRARIES` 以及 `INTERFACE_POSITION_INDEPENDENT_CODE` 等。

> 此外，还可以定义一个 GLOBAL IMPORTED 目标，这将在整个构建系统中全局可访问。

> __总结:__

> IMPORTED 目标在 CMake 中提供了一种灵活的方法来处理已有的外部依赖，使得对这些依赖项的引用和配置更为便捷且直观。

> *****

看着像哲学论述，换种方式理解。它能够解决什么场景问题和如何解决这个问题的。

先看有哪些场景需求：

1. **外部依赖集成**  
    需要将已编译好的第三方库（如`.a`/`.so`/`.dll`）集成到项目中，但：
    - 不希望重新编译这些库
    - 需要保持依赖项的版本一致性

2. **属性定制需求**  
    虽然依赖项已存在，但可能需要：
    - 添加额外的编译定义（如宏开关）
    - 补充头文件搜索路径
    - 调整链接选项

3. **全局可见性管理**  
    某些基础依赖需要被项目中多个子模块共享访问

它的解决方案为：将一个目标声明为IMPORTED目标，解决步骤如下：

```cmake
# 第一步，声明已存在的库目标
add_library(foo IMPORTED SHARED)
set_target_properties(foo PROPERTIES
  IMPORTED_LOCATION /path/to/libfoo.so
  INTERFACE_INCLUDE_DIRECTORIES /path/to/include
)

# 第二步，像普通目标一样定制属性
target_compile_definitions(foo INTERFACE USE_FEATURE_A)
target_link_libraries(foo INTERFACE pthread)
```

典型工作流如下：

1. 声明阶段
    + 通过find_package()或手动路径指定导入库文件

2. 配置阶段
    + 使用target_*命令补充必要属性

3. 使用阶段
    + 通过target_link_libraries()直接引用


### 8.2 Alias Targets

别名target，看名称就是给一个target创建一个其他的名称。它像是c++中的常量引用，是基于已存在的目标而创建的。如果别名有什么好处的话，alias这种类型的target也就具有什么好处。

cmake官方对它的定义为：
> 在 CMake 中，ALIAS 目标是一个名称，可以在只读上下文中与二进制目标名称互换使用。ALIAS 目标的主要用途包括随库一起提供的示例或单元测试可执行文件，这些文件可以是同一构建系统的一部分，也可以根据用户配置单独构建。

****

首先看如何创建一个别名目标，以下是一个示例演示如何定义和使用 ALIAS 目标：

```cmake
# 定义一个名为 lib1 的库目标
add_library(lib1 lib1.cpp)

# 安装该库及其导出文件
install(TARGETS lib1 EXPORT lib1Export ${dest_args})
install(EXPORT lib1Export NAMESPACE Upstream:: ${other_args})

# 创建一个 ALIAS 目标 Upstream::lib1
add_library(Upstream::lib1 ALIAS lib1)
```

此时，在另一个目录中，可以无条件地链接到 Upstream::lib1 目标，该目标可以是从包中导入的 IMPORTED 目标，也可以是作为同一构建系统一部分构建的 ALIAS 目标：

```CMAKE
if (NOT TARGET Upstream::lib1)
  find_package(lib1 REQUIRED)
endif()
add_executable(exe1 exe1.cpp)
target_link_libraries(exe1 Upstream::lib1)
```

***

cmake官方给了别名目标的使用场景：

> ALIAS 目标主要用于以下情形：
> 
> 1. 示例或单元测试可执行文件：这些文件可能伴随某个库一起提供，可以是同一构建系统的一部分或者根据用户配置单独构建。
> 
> 2. 统一引用：在不同目录之间可以无条件地引用同一个目标名称，不需关心其具体实现形式。
> 
> 3. 分层构建系统：ALIAS 可以使构建系统在引用时更具模块化和简洁性。
> 
> 总结，ALIAS 目标提供了一种便捷的方式，用于在大型或分层构建系统中使用一致的目标名称，同时确保这些目标的定义在整个构建系统中保持本地化和不可变。
> 

当时，我认为不太明显。可以根据如下开发时出现的问题进行解决：

1. 解决目标重命名与重构问题
    + 问题：如果一个库或者可执行文件需要修改名称时，就需要修改所用依赖于这个target的地方
    + 解决方案：通过别名目标，可以创建一个不变的"逻辑名称"，实际目标可以自由更改而不会破坏依赖关系

2. 统一接口与实现分离
    + 问题：项目可能需要在不同平台或配置下使用不同的实现
    + 解决方案：别名目标可以作为稳定接口，背后指向不同实现目标(如Threads::Threads别名在不同平台指向不同线程库实现)
    + 下面是根据不同平台创建同一个名称的库，然后再使用别名target实现平台无关，如下示例：
        ```cmake
        if(WIN32)
          message(STATUS "Windows platform detected - configuring Windows threads")
          
          if(MSVC)
              message(STATUS "Using MSVC compiler - adding _WIN32_WINNT define")
              add_library(PlatformThreads INTERFACE)
              target_compile_definitions(PlatformThreads INTERFACE _WIN32_WINNT=0x0601)
          endif()
          
          # Windows下使用Threads::Threads提供的实现
          if(NOT TARGET PlatformThreads)
              add_library(PlatformThreads INTERFACE)
          endif()
          target_link_libraries(PlatformThreads INTERFACE Threads::Threads)

        elseif(UNIX AND NOT APPLE)
            message(STATUS "UNIX-like system detected - configuring pthread")
            
            add_library(PlatformThreads INTERFACE)
            target_link_libraries(PlatformThreads INTERFACE Threads::Threads)
            
            # 添加pthread编译选项
            if(CMAKE_CXX_COMPILER_ID STREQUAL "GNU" OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
                target_compile_options(PlatformThreads INTERFACE -pthread)
            endif()

        elseif(APPLE)
            message(STATUS "macOS platform detected - configuring system threads")
            
            add_library(PlatformThreads INTERFACE)
            target_link_libraries(PlatformThreads INTERFACE Threads::Threads)
        endif()

        add_library(MyProject::Threads ALIAS PlatformThreads)

        add_executable(my_app main.cpp)
        target_link_libraries(my_app PRIVATE MyProject::Threads)
        ```

3. 简化依赖管理
    + 问题：复杂项目中依赖关系可能变得混乱，特别是当使用add_subdirectory包含外部项目时
    + 解决方案：通过别名可以创建一致的、项目范围内的目标名称，隐藏实现细节


4. 解决导出目标命名冲突
    + 问题：当多个子项目定义相同名称的目标时会发生冲突
    + 解决方案：每个项目可以使用自己的命名空间，然后通过别名导出统一命名的目标
    + 示例：
        ```cmake
        # 假设库liba有一个target foo
        # 假设库libb也有一个target foo
        # 如何直接使用target_link_libraries，cmake不知道链接哪一个库，因此通过别名库的方式来减低重名的概率。
        
        # 首先是liba
        add_library(foo STATIC foo.cpp)

        # 创建命名空间别名目标
        add_library(liba::foo ALIAS foo)

        # 设置目标属性
        target_include_directories(foo PUBLIC 
            $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
            $<INSTALL_INTERFACE:include>
        )

        # 然后libb库也有名为foo的目标
        add_library(foo STATIC bar_foo.cpp)

        # 使用不同的命名空间创建别名
        add_library(libb::foo ALIAS foo)

        # 设置目标属性
        target_compile_definitions(foo PUBLIC USE_BAR_VERSION=1)
        target_include_directories(foo PUBLIC 
            $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
            $<INSTALL_INTERFACE:include>
        )

        # 实际使用

        add_executable(my_app main.cpp)

        # 明确使用不同命名空间下的foo目标
        target_link_libraries(my_app PRIVATE
            liba::foo    # 使用libfoo提供的foo实现
            libb::foo    # 使用libbar提供的foo实现
        )
        ```

5. 提供更好的包管理支持
    + 问题：传统CMake在find_package后需要手动设置各种变量和路径
    + 解决方案：现代CMake包可以提供别名目标(如Boost::filesystem)，自动设置所有必要的依赖和属性
    + 示例：
        - 传统方案：
            ```cmake
              find_package(Boost REQUIRED COMPONENTS filesystem)

              # 需要手动处理所有变量
              include_directories(${Boost_INCLUDE_DIRS})  # 全局包含路径
              add_executable(my_app main.cpp)
              target_link_libraries(my_app ${Boost_LIBRARIES})  # 链接所有库

              # 还需要手动处理依赖的其他属性
              add_definitions(${Boost_DEFINITIONS})
            ```
        - 现代方案：
            ```cmake
            find_package(Boost REQUIRED COMPONENTS filesystem)

            add_executable(my_app main.cpp)
            target_link_libraries(my_app PRIVATE Boost::filesystem)  # 自动处理所有依赖
            ```

6. 实现可选组件和特性
    + 问题：传统方式难以优雅地处理可选组件
    + 解决方案：可以通过条件创建别名目标来表示可选功能，依赖关系更清晰

### 8.3 Interface Libraries  

在 CMake 中，INTERFACE 库目标不编译源文件，也不会在磁盘上生成库工件。

- 不编译任何源文件
- 不会生成实际的库文件（如`.a`或`.so`）
- 因此**没有`LOCATION`属性**

INTERFACE 库目标主要用于指定使用需求支持如下接口属性：

| 属性名称                              | 作用描述                    |
|---------------------------------------|----------------------------|
| `INTERFACE_INCLUDE_DIRECTORIES`       | 指定头文件目录              |
| `INTERFACE_COMPILE_DEFINITIONS`       | 定义编译预处理宏            |
| `INTERFACE_COMPILE_OPTIONS`           | 设置编译选项                |
| `INTERFACE_LINK_LIBRARIES`            | 声明链接库依赖              |
| `INTERFACE_SOURCES`                   | 指定接口源文件              |
| `INTERFACE_POSITION_INDEPENDENT_CODE` | 控制位置无关代码(PIC)选项   |

#### 8.3.1 使用 INTERFACE 库的主要场景

1. **头文件专用库**：
    + 例如，仅包含头文件的库。
2. **集中使用需求定义**：
    + 通过 INTERFACE 库将编译器特定的选项封装起来，并通过链目标的方式提供给消费者。

生成一个接口库的cmakelists.txt如下：

```cmake
add_library(myEigen INTERFACE)

target_sources(myEigen PUBLIC
  FILE_SET HEADERS
    BASE_DIRS src
    FILES src/eigen.h src/vector.h src/matrix.h
)
```

使用端：

```cmake
add_executable(exe1 exe1.cpp)
target_link_libraries(exe1 myEigen)
```

在上面的示例中，使用 FILE_SET 命令定义头文件集合时，BASE_DIRS 自动成为目标 myEigen 的使用需求中的包含目录。这些使用需求在编译时被使用，但对链接没有影响。

#### 8.3.2 安装和导出 INTERFACE 库

```CMAKE
add_library(Eigen INTERFACE)

target_sources(Eigen INTERFACE
  FILE_SET HEADERS
    BASE_DIRS src
    FILES src/eigen.h src/vector.h src/matrix.h
)

install(TARGETS Eigen EXPORT eigenExport
  FILE_SET HEADERS DESTINATION include/Eigen)
install(EXPORT eigenExport NAMESPACE Upstream::
  DESTINATION lib/cmake/Eigen
)
```

在上述示例中，使用 install() 命令可以将头文件集合和目标一同安装。头文件会被安装到 include/Eigen 目录。安装目标时，目标的导出文件也会生成，并放置到指定的路径中。使用 NAMESPACE 可以确保在使用这些导出文件时正确地命名空间前缀。  

