---
layout: post
title: cmake的install命令详解
math: true
date: 2024-09-04 15:32 +0800
tags: [cmake]
toc: true
---

## 第一章 前言

首先说一下包管理会有哪些常见的需求

### 1.1 主要需求

能够使用库作者所提供的静态库、动态库、以及可执行文件即可。

### 1.2 第一个版本的解决方案

第一步：库作者仅仅是提供一个库的和头文件即可，然后库使用者先将库编译完毕，然后把库和头文件安装到自己本地的位置。  
第二步：库使用者使用Target_link_library和target_include_directory等使用库提供的库和头文件，此时需要加入库和头文件所在的绝对路径  

### 1.3 不足点：

- 针对整个包而言，没有描述整个包的相关信息，比如版本信息等，没有对包里面的多个库之间的关系进行关联，比如lib1需要lib2存在才可以正常工作。  
- 针对使用者而言，每次需要使用绝对路径等方式，使用起来比较麻烦  
- 针对使用者而言，当整个库日益庞大后，使用者需要较为清楚整个包的结构关系，然后自行管理使用过程。这对于库使用者而言是不太好的，因为他们并不熟悉整个库，而管理整个库的工作应该是库作者所应该做的。  

而随着库的发展，其内容越来越多，信息越来越复杂，又衍生出了一些额外的需求或者是矛盾点：

1. 当库使用者使用多个不同的库时，发现有些时候链接了不同库提供者的相同名字的库。

因此有一个自然的想法：让一个专业的管理软件来控制整个过程，把复杂多变的问题交给一个软件进行管理，这个软件就是cmake。这样做的好处是库作者和使用者只要熟悉使用cmake的框架或者解决方案时，就可以很快的使用：

+ 库制作者需要把自己整个项目的内容完完整整的告诉给cmake，使用cmake所提供的方案构建出整个包的内容。
+ 而库使用者只需要熟悉cmake的使用方案，那么就可以很快熟练使用整个库。各自只是关心各自的内容即可。  

### 1.4 cmake需要解决使用者的需求

1. 这个包能够很方便的提供给使用者，使用者使用某种方式就可以很快查找到包，再查找到包之后，然后使用这个包中的动态库、静态库、可执行文件等资源。  
2. 使用者能够可以使用整个包的一部分，比如说，包的一个动态库。在cmake中，动态库和可执行文件这种均可以认为一个目标(Target)。  
3. 使用者能够通过cmake编译生成一个完整的包，这个包包含了库和安装到自定义的位置。  

### 1.5 cmake需要解决的库开发者的需求

1. 如何生成库的相关资源，例如动态库、静态库、头文件以及可执行文件等。
2. 如何生成管理这个库的这些信息，让cmake知道如何给库使用者提供相应的内容。这些信息决定了这个库具有哪些功能（与库支持cmake管理相关的功能，而不是库所能提供的功能）  

## 第二章 第一个需求的各自工作内容

### 2.1 工作流程解决的需求简介

#### 2.1.1 使用者责任

+ cmake提出使用find_package命令获取整个包的信息，然后使用者利用 Target_link_library和target_include_directory等方法包含或者是链接库和头文件。
+ 将库的管理信息交由库作者进行描述和生成。  

相对来说，库的使用者的工作较少：

+ 设置包的路径，从而告诉cmake去哪里搜索    
+ 验证包的配置信息，验证是否符合自己的要求  
+ 提取出包中关于头文件，动静态库文件的路径  

#### 2.1.2 库作者责任

find_package命令是获取整个包的配置信息，然后再将这个信息传递给使用者。  
而find_package命令是通过搜索指定路径下的包配置文件，因此库作者为了实现这个功能，需要提供它。主要为三个文件：

+ PackageConfig.cmake  
+ Package-config.cmake  
+ findfoo.cmake  

这三个文件提供其中一个就可以了，cmake默认的搜索先后是从上到下的顺序的，即：  
```mermaid
graph TD
    Start[开始查找配置文件] --> A[查找 PackageConfig.cmake]
    A -->|存在| Success1[使用 PackageConfig.cmake]
    A -->|不存在| B[查找 Package-config.cmake]
    B -->|存在| Success2[使用 Package-config.cmake]
    B -->|不存在| C[查找 findfoo.cmake]
    C -->|存在| Success3[使用 findfoo.cmake]
    C -->|不存在| Fail[查找失败]

    classDef success fill:#d0e0ff,stroke:#1a3c7c,color:#000;
    classDef fail fill:#ffd0d0,stroke:#7c1a1a;
    class Success1,Success2,Success3 success;
    class Fail fail;
```
因此，这三种配置文件就成了整个项目的入口文件了，也就是说，find_package只要所写包配置文件正确，那么它就可以正确工作。

### 2.2 解决责任的工作流

一般来说，不论是库开发者，还是库的使用者，在使用cmake管理项目的时候，双方都需要遵守一定的规则。一般来说，这都是由cmake官方所指定的，我们只能使用它的功能，所以需要了解各自的工作流。  

#### 2.2.1 库使用者的工作流

一个简单的示例：
```cmake
cmake_minimum_required(VERSION 3.12)
project(MyProject VERSION 1.0 LANGUAGES CXX)

# 设置包的搜索路径
set(CMAKE_PREFIX_PATH "/path/to/MyLibrary")

# 找到 MyLibrary 包
find_package(MyLibrary 1.0.0 REQUIRED)

# 创建可执行文件
add_executable(MyExecutable main.cpp)

# 链接 MyLibrary
target_link_libraries(MyExecutable PRIVATE MyLibrary::MyLibrary)

# 添加 MyLibrary 提供的包含目录
target_include_directories(MyExecutable PRIVATE
    $<TARGET_PROPERTY:MyLibrary::MyLibrary,INTERFACE_INCLUDE_DIRECTORIES>)
```

#### 2.2.2 库制作者的工作流

根据前面所说，只要我们提供正确的配置文件往往比较难。我们如果想要生成正确的，没有错误的配置文件，势必要非常了解cmake，这无形之中增加了很大的麻烦。因此有一种工作流是使用CMakePackageConfigHelpers帮助我们生成整个包的配置文件。

1. 使用CMakePackageConfigHelpers生成整个包的配置文件。  
2. 使用install将生成的包配置文件安装到指定位置。  

> CMakePackageConfigHelpers是一个cmake拓展功能，一般情况下不加载，因此，为了让它能够工作，一般使用`include(CMakePackageConfigHelpers)`引入这个拓展包中的函数或者是宏。
> 它主要包含了两个函数：
>
> 1. write_basic_package_version_file
>     + 这个函数用于生成一个版本文件（<PackageName>ConfigVersion.cmake），它描述了包的版本信息，并可用于版本检查。
>     + 这个版本文件允许 find_package() 命令在查找包时进行版本匹配.  
> 2. configure_package_config_file():
>     + 这个函数用于生成一个配置文件（<PackageName>Config.cmake），它包含对包相关的 CMake 变量、目标和查找路径的描述。
>     + 这个配置文件帮助 CMake 项目在使用 find_package() 时正确配置所需的构建设置

那么生成的packageConfig.cmake的作用是什么呢？

它主要是提供了一个cmake的入口，将各个组件中的Target内容在这里组合起来，相当于一个部门的主要领导者。那么它是怎么管理的呢？

它是通过include关于Target.cmake，从而引入包中各个组件的信息。更近一步，在整个包管理中会生成一定调用函数检查各个组件是否正确。  

另外还生成了一个MyProjectConfigVersion.cmake文件，它的作用就是辅助packageConfig.cmake文件进行管理的，个人理解为相当于参谋长的位置。

一个如下示例显示了生成和安装的过程  
```cmake 
include(CMakePackageConfigHelpers)

# 配置和生成包配置文件
configure_package_config_file(
  "${PROJECT_SOURCE_DIR}/cmake/${PROJECT_NAME}Config.cmake.in"
  "${PROJECT_BINARY_DIR}/${PROJECT_NAME}Config.cmake"
  INSTALL_DESTINATION ${CMAKE_INSTALL_DATAROOTDIR}/cmake/${PROJECT_NAME})

# 生成版本文件
write_basic_package_version_file(
  "${PROJECT_NAME}ConfigVersion.cmake"
  VERSION ${PROJECT_VERSION}
  COMPATIBILITY SameMajorVersion)

# 安装生成的配置文件和版本文件
install(FILES
    "${CMAKE_CURRENT_BINARY_DIR}/MyProjectConfig.cmake"
    "${CMAKE_CURRENT_BINARY_DIR}/MyProjectConfigVersion.cmake"
    DESTINATION lib/cmake/MyProject
)
```
##### 2.2.2.1 如何生成配置文件

在第一步中：其工作逻辑为：CMakePackageConfigHelpers提供了一些函数，主要使用`configure_package_config_file`和 `write_basic_package_version_file`这两个最常用的函数生成相应的配置文件。  

**生成packageConfig.cmake**
需要搞清楚如下几个问题：

1. 如何生成相应的PackageConfig.cmake 配置文件呢？  
configure_package_config_file根据Config.cmake.in模板文件生成相应的项目信息导出文件，这个模板文件定义了CMake在生成配置文件时应该包含和设置的内容。  
那么Config.cmake.in文件指导configure_package_config_file生成最终的配置文件。  

首先了解一下语法：
`configure_package_config_file`语法：  
```
configure_package_config_file(<INPUT> <OUTPUT> [OPTIONS])
<INPUT>: 输入模板文件的路径。
<OUTPUT>: 输出文件的路径。
[OPTIONS]: 可选项，主要包括目的地路径等
``` 
通常来说，使用模板文件作为输入，然后得到${PROJECT_NAME}Config.cmake文件，该文件提供给cmake的find_package使用。  

而一般的Config.cmake.in文件可能包含了以下内容：  
```cmake
@PACKAGE_INIT@

include("${CMAKE_CURRENT_LIST_DIR}/ProjectTargets.cmake")
check_required_components("@PROJECT_NAME@")
```
接下来挨个解释内容
- `@PACKAGE_INIT@`是一个占位符，用于在使用 configure_package_config_file() 函数生成实际配置文件时替换成预定义的初始化代码。这个宏通常用于设置一些基础配置或做一些初始化操作，确保生成的配置文件可以正常工作。
- `include("${CMAKE_CURRENT_LIST_DIR}/ProjectTargets.cmake")` 这行代码的作用是包含一个名为`ProjectTargets.cmake`的文件，该文件定义了项目的安装目标。从路径 `${CMAKE_CURRENT_LIST_DIR}/MyProjectTargets.cmake` 来看，`ProjectTargets.cmake` 文件相对于生成的 `Config.cmake`文件所在目录被存储，这个路径是动态的，可以适应不同的安装环境。它的目的是设置一些与项目相关的环境变量。  
- `check_required_components` 辅助宏通过检查所有必需组件的 `<Package>_<Component>_FOUND` 变量确保找到所有请求的非可选组件。即使包没有任何组件，也应在包配置文件的末尾调用此宏。这样，CMake 可以确保下游项目没有指定任何不存在的组件。如果 `check_required_components` 失败，则 `<Package>_FOUND` 变量设置为 FALSE，并认为未找到包。`set_and_check()` 宏应该在配置文件中使用，而不是用于设置目录和文件位置的普通 set() 命令。如果引用的文件或目录不存在，宏将失败.  

2. 模板文件和一般的cmake文件的区别是什么呢？  
区别就是有些变量是@var1@样式的，而configure_package_config_file() 函数类似于c语言的宏处理器，将宏替换为相应的内容即可。
3. 哪些变量可以作为模板变量呢？  
>  + cmake内置变量
>  + cmakelists的自定义变量  
>  + 通过pathvar 参数传入的变量  
4. 处理完之后所生成的配置文件的效果是什么呢？  
假设在CMakeLists.txt中定义了如下变量： 
```cmake
set(LIB_INSTALL_DIR "1")
set(INCLUDE_INSTALL_DIR "5555")
set(CMAKE_INSTALL_PREFIX "dsadsad")
```
在PackageConfig.cmake.in文件中有如下语句：
```cmake
set(MYPROJECT_LIB_DIR "@LIB_INSTALL_DIR@")
set(MYPROJECT_INCLUDE_DIR "@INCLUDE_INSTALL_DIR@")

message("CMAKE_INSTALL_PREFIX = @CMAKE_INSTALL_PREFIX@")
```
被configure_package_config_file函数处理完了之后的效果为：
```cmake
set(MYPROJECT_LIB_DIR "1")
set(MYPROJECT_INCLUDE_DIR "5555")

message("CMAKE_INSTALL_PREFIX = dsadsad")
```
可以看出，其作用效果就是宏处理器的文字替换效果。

**生成packageConfigVersion.cmake**  
使用write_basic_package_version_file生成相应的内容，它不需要任何其他的文件，只需要在CMakeLists.txt文件中定义过与版本相关的内容就可以。  
`write_basic_package_version_file`语法：  
```cmake
write_basic_package_version_file(<filename> [options])
<filename>: 生成的版本文件的路径。
[options]: 可选项，通常包括版本号和兼容性策略。
```
一般来说最后都是`${PROJECT_NAME}ConfigVersion.cmake`这样的文件命名方式
`VERSION ${PROJECT_VERSION}` 就是在project(mytestlib)的时候，所设置的信息：  
+ COMPATIBILITY SameMajorVersion:  
+ COMPATIBILITY 选项指定版本兼容性策略。常用的策略包括：  
+ AnyNewerVersion: 任何新版本都兼容。  
+ SameMajorVersion: 只有同一个大版本号的版本才兼容。  
+ ExactVersion: 只接受完全相同的版本。  
+ SameMajorVersion 表示要求相同的主版本号才能兼容。例如，如果版本是 1.2.3，那么 1.x.y 版本（如 1.4.0 或 1.2.5）都是兼容的，但 2.x.y 则不兼容。

**小结**
在这个过程中主要生成了两个配置文件  
+ 配置文件（ProjectConfig.cmake）:
  它通常包含了查找依赖项、设置变量以及加载导出目标的逻辑。它负责告诉 CMake 接下来需要做什么，例如加载 MyProjectTargets.cmake 文件。所以它是必需的，因为它扮演了协调者的角色。

+ 版本文件（ProjectConfigVersion.cmake）:
  它包含版本兼容性检查的逻辑，确保所需的版本满足要求。  

当用户在他们的 CMake 项目中使用 find_package(MyProject 1.2 REQUIRED) 时：
+ CMake 首先找到并加载 MyProjectConfig.cmake：如果找到并加载成功，接下来会执行MyProjectConfig.cmake 中的内容。
+ 通常，这个文件会包含类似 include("${CMAKE_CURRENT_LIST_DIR}/MyProjectTargets.cmake") 的语句，以引入导出的目标文件。
+ CMake 加载 MyProjectConfigVersion.cmake：
  用于检查版本兼容性。


##### 2.2.2.2 如何安装配置文件  
按照前面说的，此时只是生成了配置文件，还需要安装package的配置文件  
```cmake
# 安装生成的配置文件和版本文件
install(FILES
    "${CMAKE_CURRENT_BINARY_DIR}/MyProjectConfig.cmake"
    "${CMAKE_CURRENT_BINARY_DIR}/MyProjectConfigVersion.cmake"
    DESTINATION lib/cmake/MyProject
)
```
它的主要目的是将配置文件和库资源一起打包。  

## 第三章 第二个需求的各自工作内容  
### 3.1 解决使用者的责任  
实际上，使用者只需要知道有哪些静态库或者是动态库，然后直接链接整个库即可。然而，由于存在着动态库，静态库，接口库以及可能出现不同库之间存在着同名的库，因此cmake提出了namespace的概念，这样一般来说就极大概率的降低了链接存在着同名库的问题了。  

### 3.2 解决库作者的责任  
先说一下cmake中生成库的时候，使用的是面向对象的思想进行管理，亦即使用target的方式。那么每生成一个target，也就意味着库作者就需要提供这个target对象相关的信息，比如头文件在那里，动静态库在那里等等。之后cmake使用makefile等构建工具先生成一系列这类target相关的库资源，然后cmake为了提高个性化，库作者可以自行决定是否提供与target相关的配置文件。因此，库作者需要通过一定的方式生成这些配置文件。  
为了简化操作，cmake提供了一种工作流：  
第一步，一般而言，告诉cmake，一个target所需要的信息，然后再使用install(TARGETS)安装头文件、静态库或者是动态库，或者是可执行文件，我们在这里把它称为源文件衍生物。  
第二步，使用install命令，将这些源文件衍生物安装到指定位置。  
第三步，将target源文件衍生物和其他的相关信息生成一个配置文件，然后安装target相关的配置信息。  

1. 设置target的相关信息  
+ 设置target的哪些头文件是需要安装到指定位置的：  
  + 使用set_target_properties命令指定target的头文件安装属性 PUBLIC_HEADER；INTERFACE_HEADER  
  + 使用cmake的HEADER_SET概念，然后再安装  
+ 设置target的哪些源文件是需要编译的：  
2. 安装并导出TARGETS:  
```CMAKE
install(TARGETS myApp
    EXPORT myAppTarget
    PUBLIC_HEADER DESTINATION include
    ARCHIVE DESTINATION lib
    LIBRARY DESTINATION lib
    RUNTIME DESTINATION bin)
```
`myapp`是通过添加命令的方式生成的target，然后设置导出的目标名称为myAppTarget，这个名称可自行定义，但是为了容易看懂，targetname+Target的方式。值得注意的是，这里加了一个参数，EXPORT。这个是必要的，这个主要是让cmake就知道了配置这个target相关的必要信息了，然后再install(EXPORT)。  
3. 使用install命令，通过install(TARGET)标头，自动生成target.cmake文件并安装到指定的位置。
```cmake
install(EXPORT myAppTarget
    NAMESPACE test2::
    FILE myApp-targets.cmake
    DESTINATION lib/cmake/test2)
```
在第二步中，myAppTarget是前面install TARGETS时所导出的名称；命名空间就是防止不同库之间相同静动态库名称的解决方案；FILE表示生成的配置文件名字；安装位置表示使用make install之后，这个会安装到哪个相对位置下。  
4. 在整个packageConfig.cmake文件中，需要使用include所生成的target的配置文件，从而当find_package之后就可以成功读取与target相关的配置信息。

## 第四章 一个简单的构建示例

在这个示例代码中我们要解决三个部分：

1. 如何构建一个目标  
2. 告诉cmake，应该安装目标的哪些内容  
3. 以及他人使用这个目标时，我们能够提供给他们哪些内容  

假设拥有一个如下示例的源代码结构  
```plaintext
.
├── CMakeLists.txt
├── include
│ └── mylib.h
└── mylib.c
```
然后我们想要生成一个类似于linux下的源代码管理方式，即头文件放在include下，动态库以及静态库放在lib下，二进制可执行文件放在bin目录下  
那么就如同如下结构：  
```plaintext
├── install
│ ├── include
│ │ └── mylib.h
│ └── lib
│ | ├── cmake
│ │   └── mylib
│ │     ├── mylib-config.cmake
│ │     └── mylib-config-noconfig.cmake
│ ├── libmylib.a
```

其中install就是安装的目录，在cmake下存在着关于这个库的详细信息  
cmake目录下存在着各个已经编译好的库目录，比如mylib就是我们编译好之后关于mylib的项目信息，主要由各类.cmake结尾的文件所组成，  
当使用find_package(mylib)，并且指定了CMAKE_PREFIX_PATH这个变量，它就会挨个查找cmake目录下的下面的各个库信息，当目录名称和  
find_package中的包名一致时，它便会进入到这个目录下读取各类.cmake结尾的文件内容，当然也存在着其他的方法，后续再写博客.当我们用find_package(my_library ...)这条命令时，它去`{CMAKE_INSTALL_PREFIX}/lib`目录下一个名为`my_library*`的文件夹中自动去寻找一个类似`my_library-config.cmake`的文件，而我们的安装命名就是符合这个规则的，`lib/my_library-[major].[minor] - ${main_lib_dest}`。所以现在我们需要提供`my_library-config.cmake `文件.  

假设我们所要提供给别人的库中，需要先编译的是mylib.c  
```C
#include <stdio.h>
#include "mylib.h"
void hello()
{
    printf("hello");
}
```
给予他人的头文件mylib.h, 内容为  
```C
#ifndef MYLIB_H
#define MYLIB_H
#include <stdio.h>
void hello();
#endif
```
那么就需要解决前面所提到的三个问题。

### 问题一：如何构建一个目标  
首先是每一个cmakelists都需要声明的内容，即：  
版本最低要求以及项目名称  

```cmake 
cmake_minimum_required(VERSION xxx)

project(mytestlib)
```
由于现代cmake中推荐以目标对象(target)的方式来管理，然后再使用target_xx 类的cmake命令进行目标对象其他的属性设置。

首先，操作target，那么就需要先有target。cmake提供了如下几种方式创建一个target：

1. add_executable - 用于创建可执行文件。
2. add_library - 用于创建静态库或共享库。
3. add_custom_target - 用于创建一个自定义的目标，这个目标不生成输出文件，而是执行一组自定义命令。
4. add_custom_command - 用于添加生成文件所需的自定义命令。

本文主要聚焦于前两个命令，当添加完一个目标之后，那么我们target_xx类的命令给库或者是可执行文件相应的属性了。
```cmake 
add_library(mylib mylib.c include/mylib.h)
target_include_directories(mylib PUBLIC
    $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
    $<INSTALL_INTERFACE:include>)
```
这个中间涉及到了生成器的相关内容，它的主要目的是将目标构建阶段的头文件包含属性和目标的安装阶段的属性分开。

### 问题二：告诉cmake，应该安装哪些内容  
前面我们已经生成了一个静态库目标了。根据c/c++编译链接模型，别人使用我们所提供的库，最少需要两个部分：

1. 头文件  
2. 静态库
3. 动态库
4. 可执行文件  

此时就需要使用install命令，首先告诉cmake，我们所提供的库的头文件是什么，第二个是需要安装哪些内容： 
```cmake 
set_target_properties(mylib PROPERTIES PUBLIC_HEADER "include/mylib.h") 

install(TARGETS mylib
    EXPORT mylib-targets
    PUBLIC_HEADER DESTINATION include
    ARCHIVE DESTINATION lib
    LIBRARY DESTINATION lib
    RUNTIME DESTINATION bin)
```
首先需要给一个特定的库绑定它所相关的头文件，这个与是否安装无关，如果所安装的目标没有绑定头文件的话，那么在安装时，其include下。 
就没有库使用者所需要的头文件。

接下来解释一下install的一般格式  
```cmake 
install(<TYPE> files... DESTINATION <dir>
        [PERMISSIONS permissions...]
        [CONFIGURATIONS [Debug|Release|...]]
        [COMPONENT <component>]
        [OPTIONAL] [NAMELINK_ONLY|NAMELINK_SKIP])

```
可以看出这个命令是比较复杂的，其他的<TYPE>有以下几种：

+ PROGRAMS：用于安装可执行文件。
+ LIBRARY：用于安装库文件。
+ ARCHIVE：用于安装静态库文件。
+ RUNTIME：用于安装运行时文件（主要用于 Windows）。
+ OBJECTS：用于安装对象文件。
+ DIRECTORY：用于安装整个目录。
+ FILES：用于安装单个或多个文件

这六种是为了不同的目的所解决的类型。  

此外有两个是为了补充TARGETS所提出来的，即PUBLIC_HEADER和EXPORT是为了帮助TARGERTS进行安装之后能够正常工作进行的操作，后面的DESTINATION内容就是指定安装的路径，这个是必须指定的。其余的参数都是可选的，根据实际需要进行设定。

那么install中通常需要设定两个内容:
```
<type> xx DESTINATION <dir> [可选参数]  
```
此时当我们设置好这些内容之后，cmake就知道了我们安装哪些具体的内容

### 问题三：以及他人使用这个目标时，我们能够提供给他们哪些内容  
这个内容主要是为了它人使用find_package命令所准备的，如果库制作方不打算提供这种方式的话，那么就没有必要写；在问题二中，我们已经设置了安装属性，此时就需要利用信息生成一定的.cmake的信息，通过这些信息告诉库使用者这些相关信息；在哪里？使用的仍然是install命令。

我所接触到的方式有两种范式。  
第一种如下所示：  
```cmake 
install(EXPORT mylib-targets
    NAMESPACE mylib::
    FILE mylib-config.cmake
    DESTINATION lib/cmake/mylib)
```
值得注意的有：

- 在前面install目标时，需要设置TARGETS一个EXPORT属性，然后根据这些属性使用install命令指导生成.cmake文件信息，其中EXPORT是和前面install的目标所导出的名称是一致的，均为示例中的mylib-targets。
- 第二个是NAMESPACE，这个主要是为了区分不同项目的相同名称库，例如ProjectA中有一个库，其名称为mylib，而ProjectB中也有一个库，其名称也为mylib，假设一个项目AppC需要同时使用ProjectA的mylib，以及ProjectB的mylib。如果没有命名空间的话，cmake就无法知道到底链接哪一个mylib，当有了命令空间之后，就可以知道是ProjectA或者是ProjectA的mylib了。
- 使用FILE类型，这个声明了文件名称，第四个是DESTINATION，这个表示所生成的.cmake文件放到哪里去。

第二种方式是使用CMakePackageConfigHelpers对包进行一定的配置
```cmake 
include(CMakePackageConfigHelpers)

# 配置和生成包配置文件
configure_package_config_file(
  "${PROJECT_SOURCE_DIR}/cmake/${PROJECT_NAME}Config.cmake.in"
  "${PROJECT_BINARY_DIR}/${PROJECT_NAME}Config.cmake"
  INSTALL_DESTINATION ${CMAKE_INSTALL_DATAROOTDIR}/cmake/${PROJECT_NAME})

# 生成版本文件
write_basic_package_version_file(
  "${PROJECT_NAME}ConfigVersion.cmake"
  VERSION ${PROJECT_VERSION}
  COMPATIBILITY SameMajorVersion)

# 安装生成的配置文件和版本文件
install(FILES
    "${CMAKE_CURRENT_BINARY_DIR}/MyProjectConfig.cmake"
    "${CMAKE_CURRENT_BINARY_DIR}/MyProjectConfigVersion.cmake"
    DESTINATION lib/cmake/MyProject
)

# 安装导出的目标
install(EXPORT MyProjectTargets
    FILE MyProjectTargets.cmake
    NAMESPACE MyProject::
    DESTINATION lib/cmake/MyProject
)
```

在这个过程中主要生成了三个配置文件：

1. **配置文件（MyProjectConfig.cmake）**  
    - 它通常包含了查找依赖项、设置变量以及加载导出目标的逻辑。
    - 它负责告诉 CMake 接下来需要做什么，例如加载 MyProjectTargets.cmake 文件。
    - 所以它是必需的，因为它扮演了协调者的角色。
2. **版本文件（MyProjectConfigVersion.cmake）**
    - 它包含版本兼容性检查的逻辑，确保所需的版本满足要求。  
3. **导出的目标文件（MyProjectTargets.cmake）**
    - 它具体描述了如何使用该包内的目标，包括编译选项、链接库等信息  

当用户在他们的 CMake 项目中使用 find_package(MyProject 1.2 REQUIRED) 时：

+ CMake 首先找到并加载 `MyProjectConfig.cmake`；如果找到并加载成功，接下来会执行`MyProjectConfig.cmake`中的内容。
+ 通常，这个文件会包含类似`include("${CMAKE_CURRENT_LIST_DIR}/MyProjectTargets.cmake")`的语句，以引入导出的目标文件。
+ CMake 加载 MyProjectConfigVersion.cmake：用于检查版本兼容性。
+ CMake 从配置文件中找到导出的目标文件并加载：导入这些目标并将它们加入到用户的项目中。

install(FILES ...) 和 install(EXPORT ...) 是互补的。配置文件提供了高层次的逻辑和版本控制，而导出的目标文件则提供了详细的目标定义。两者结合使用确保了包的完整性和易用性  

## 参考文献  
1. [cmake 生成供find_package使用的自定义模块](https://blog.csdn.net/ktigerhero3/article/details/83863226)
2. [CMake库打包以及支持find_package](https://murphypei.github.io/blog/2018/11/cmake-install-find-package)