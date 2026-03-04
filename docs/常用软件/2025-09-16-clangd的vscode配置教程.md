---
layout: post
title: clangd的配置
date: 2025-09-16 22:48 +0800
tags: [software]
---

## 一、下载安装

Clangd 是基于 **Clang 编译器** 构建的 C/C++ 语言服务器，遵循 **Language Server Protocol (LSP)** 协议，能够在编辑器中提供智能代码补全、语法诊断、跳转定义、查找引用等现代化开发功能。它通过分析源代码和编译构建信息（如编译标志、头文件路径等），构建出精确的语法树和符号索引，从而实现对代码的深度理解与实时交互。

1. 安装一个 clangd 的语言服务器。
2. 一个可安装 clangd 插件的编辑器，推荐使用 VSCode。
3. 告诉 clangd 该项目是如何构建的。

### 1.1 安装 clangd 语言服务器

从 [clangd 的 GitHub 仓库](https://github.com/clangd/clangd) 中直接下载对应系统的二进制文件，解压后将 `clangd` 的可执行文件路径添加到系统环境变量中。

### 1.2 在 VSCode 中安装 clangd 插件

- 能够联网的用户可以直接在 VSCode 编辑器中搜索并安装 `clangd` 插件。
- 无法联网的用户可以通过 [VSCode 插件市场](https://marketplace.visualstudio.com/vscode) 下载 `.vsix` 文件，然后通过命令面板选择“Extensions: Install from VSIX”进行离线安装。

## 二、主要功能

- ✅ 代码补全
- ✅ 代码诊断和缺陷修复
- ✅ 查找声明、定义和引用
- ✅ 使用 `Ctrl+P`，在弹出窗口中输入 `@` 和符号名（如 `@func1`），即可快速跳转到该符号的定义位置
- ✅ 悬停提示与语法高亮

## 三、深入理解

### 3.1 Debug 日志

当 clangd 正在工作时，它会通过 Language Server Protocol (LSP) 向客户端发送解析日志。  
你可以在 VSCode 中查看这些日志：

> 面板 → 视图 → 输出 → 在输出面板中选择 **clangd**

### 3.2 命令行标志

可通过 `settings.json` 文件中的 `clangd.arguments` 数组传入自定义参数。  
示例：
```json
{
  "clangd.arguments": [
    "--log=verbose",
    "--background-index"
  ]
}
```

### 3.3 自定义 clangd 可执行文件路径

如果你使用的是非标准路径的 clangd，可以在 settings.json 中设置：

```json
{
  "clangd.path": "/your/custom/path/to/clangd"
}
```

### 3.4 项目构建配置

为了让 clangd 正确理解你的代码结构，必须将项目构建时使用的编译标志（flags）告知 clangd。

默认情况下，clangd 会假设你使用的是 clang some_file.cc 这样的简单命令进行编译。这通常会导致大量编译错误。以下是解决方法：

#### 3.4.1 使用 compile_commands.json

这个文件包含了整个项目的编译命令和标志，通常由构建系统生成。
clangd 会按以下顺序在其父目录或子目录中查找该文件：

+ 当前文件所在目录
+ 当前目录下的 build 子目录
+ 上级目录
+ 上级目录下的 build 子目录

例如：  
如果你正在编辑 $src/gui/window.cc，clangd 会依次查找：

+ $src/gui/compile_commands.json
+ $src/gui/build/compile_commands.json
+ $src/compile_commands.json
+ $src/build/compile_commands.json

#### 3.4.2 如何生成 compile_commands.json（适用于 CMake 项目）

在运行 CMake 构建时添加以下选项：

```bash
cmake -DCMAKE_EXPORT_COMPILE_COMMANDS=1 <your-source-dir>
```

生成后，compile_commands.json 会被写入构建目录。  
如果构建目录不是源码根目录或其 build 子目录，则建议将其复制或创建硬链接到源码根目录下：

```bash
# 示例：从 build 目录复制到源码根目录
cp build/compile_commands.json src/
# 或使用硬链接（节省空间）
ln build/compile_commands.json src/compile_commands.json
```

#### 3.4.3 指定compile_commands.json所在路径

当一个项目较深，或者是compile_commands.json并没有在标准的build目录下时，可以通过项目顶级的settings.json中指定compile_commands.json的所在位置，以帮助vscode中的changd插件找到对应文件是如何进行编译的。

```
{
    "clangd.arguments": [
        "--compile-commands-dir=build-name",
    ],
}
```

通过参数`--compile-commands-dir`来指定位置。

### 3.5 编译器路径指定

当项目使用交叉编译器时，clangd服务器可能会误用本地的编译器来对本地的源文件进行解析，这个时候需要指定编译器的位置。

```
{
    "clangd.arguments": [
        "--query-driver=complile_path/bin/aarch64-ca73-linux-gnu-g++",
    ],
}
```

### 3.6 重启clangd服务

很多时候，clangd 会出现代码补全不生效的问题，尤其是在项目首次打开、或删除了 `compile_commands.json` 文件之后。这通常是因为 clangd 缺少编译配置信息，导致无法正确解析代码结构。

此时，需要手动触发 clangd 重新解析项目并重建语法索引。解决方法如下：

1. 按下 `Ctrl + Shift + P` 打开命令面板（Command Palette）  
2. 输入 `clangd: Restart Language Server`  
3. 使用鼠标或键盘选择该命令并执行  

执行后，clangd 会重新启动语言服务器，并根据当前项目中的 `compile_commands.json`（或重新探测构建信息）对源代码进行重新索引，从而恢复代码补全、跳转定义、悬停提示等核心功能。

💡 建议：在修改构建配置或移动项目后，若发现 clangd 表现异常，优先尝试此操作。

## 四、一些问题

### 4.1 vscode中的clangd插件的运行状态始终显示无法激活

__原因分析：__

clangd 插件在实现代码补全等功能前，需要读取项目中的 `compile_commands.json` 文件，获取编译配置信息。随后，插件会将源代码文件通过 LSP（Language Server Protocol）发送给本地的 `clangd` 语言服务器。服务器端调用内置的 Clang 编译器组件，对代码进行解析，构建语法树和符号表等中间数据。解析结果再通过 LSP 回传给插件，由插件结合编辑器上下文，实现智能补全、跳转定义、查找引用等功能。

整个过程依赖 LSP 与本地 clangd 服务器的稳定通信，确保代码分析高效准确。

__问题排查：__

当其他插件（如简体中文语言包）在远程连接（Remote-SSH）等场景下占用 LSP 时，会导致 clangd 无法正常启动，从而出现插件显示“无法激活”的问题。

