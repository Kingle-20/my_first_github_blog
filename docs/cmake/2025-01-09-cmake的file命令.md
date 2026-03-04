---
layout: post
title: cmake的cmake的file命令详解
date: 2025-01-09 14:08 +0800
tags: [cmake]
toc: true
---

## 一、前言

很多时候，我们想要在cmake中对通过文件的方式来获取或者是发布信息，通过这些信息来帮助我们配置整个c++程序。一般在命令行中，我们可以使用下面的方式来实现文件的操作：

```cmake
cmake -E copy OriginalFile DestinationFile  #拷贝文件
cmake -E rename <oldname> <newname>  #重命名文件
cmake -E remove <file>  #删除文件
cmake -E make_directory <directory>  #删除目录
cmake -E echo <message> > <file> #写入内容到文件中
cmake -E echo_append <message> >> <file> #以追加的方式写入内容到文件中
cmake -E touch <file>  #更新文件的时间戳
```

亦或者是在CMakeLists.txt中，调用execute_process的方式调用命令行的方式实现，如：

```cmake
execute_process(
    COMMAND ${CMAKE_COMMAND} -E copy ${binary_path} ${target_path}
)
```

但是这样难免会显示比较复杂，而cmake提供了file命令，方便书写配置文件。

## 二、正文

对于文件，常见需求就是读取、写入、删除、拷贝等。它的常见格式如下：

```cmake
file(op Files ...)
```

即先指定一个操作，然后紧接着文件，然后接着是跟着操作的相关的其他参数，有一个特别是GLOB和GLOB_RECURSE。

### 2.1 读取文件

```cmake
file(READ "path/to/file.txt" OUTPUT_VARIABLE)
```

把文件中的内容读取到OUTPUT_VARIABLE中。

### 2.2 写入文件

```cmake
file(WRITE "path/to/file.txt" "This is the content")
file(WRITE "path/to/file.txt" ${INPUT_TEXT})
file(APPEND "path/to/file.txt" ${INPUT_TEXT})
```

把指定的字符串写入到指定的文件中，当文件不存在时，创建文件。第三个命令是末尾附加上相应的内容  

### 2.3 删除文件或者目录

```cmake
file(REMOVE "path/to/file.txt")
file(REMOVE_RECURSE "path/to/file.txt")
```  

第一个是删除目录，第二个是递归的删除目录  

### 2.4 拷贝文件  

```cmake
file(COPY "path/to/file.txt" DESTINATION "dest/")
```

拷贝到指定目录下。值得注意的是，当目的地已经存在了文件，可能会导致拷贝失败，这个时候需要先调用file(REMOVE "dest/")将文件删除就可以了。  

### 2.5 重命名文件  

```cmake
file(RENAME "oldname.txt" "newname.txt")
```

### 2.6 创建文件夹  

```cmake
file(MAKE_DIRECTORY "path/to/new_directory")
```

### 2.7 计算相对路径  

```cmake
file(RELATIVE_PATH REL_PATH "/home/user" "/home/user/docs/file.txt")
```

### 2.8 转化为cmake格式的路径

```cmake
file(TO_CMAKE_PATH "path/to/file.txt" UNIX_PATH)
```

### 2.9 转化为本地系统的格式  

```cmake
file(TO_NATIVE_PATH "path/to/file.txt" NATIVE_PATH)
```

### 2.10 下载文件到指定路径  

```cmake
file(DOWNLOAD "http://example.com/file.zip" "path/to/destination/file.zip")
```

### 2.11 捕捉满足指定条件的文件名  

```cmake
file(GLOB  FILES "src/*.cpp")
file(GLOB_RECURSE FILES "src/*.cpp")
```

第一种：查找符合指定模式的文件并将文件名存储到变量中，不递归。

第二种：查找符合指定模式的文件并将文件名存储到变量中，递归查找子目录。

### 2.12 MD5, SHA1, SHA256, SHA512  

```cmake
file(MD5 "path/to/file.txt" NATIVE_PATH)
```

计算文件的哈希值  

## 三、后记

总体上看，file命令是文件的一般操作（读取、写入）和目录的一些操作以及与文件相关的内容都可以考虑使用它。
