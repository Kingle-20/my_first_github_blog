---
layout: post
title: mini-forge的vscode配置教程
date: 2025-11-05 22:48 +0800
tags: [software]
---

## 一、软件安装

在miniforge的官方github仓库下载对应平台的软件后，可通过对应的安装方式进行安装。如果是windows平台下，需要将软件安装位置的加入到环境变量中。

以我的安装位置为例，`D:\ProgramFiles\MiniForge\shell\condabin`中，`D:\ProgramFiles\MiniForge`是安装位置，添加上`shell\condabin`放到环境变量中即可。

## 二、vscode配置

1. 安装python插件
   + 打开 VS Code，点击左侧扩展图标（或按 Ctrl+Shift+X）。
   + 搜索 “Python”，选择由 Microsoft 提供的扩展并点击“安装”。

2. 选择 Python 解释器
    + 打开 VS Code，按 Ctrl+Shift+P 调出命令面板。
    + 输入 Python: Select Interpreter 并选择该命令。
    + 在列表中选择 Miniforge 的 Python 环境。如果想要选择创建自己的环境，需要先创建该环境后，激活该环境再进行此操作。

3. 修改 vscode 的配置（可选）
    + 在vscode中打开settings.json，添加  
        ```
        {
            "python.defaultInterpreterPath": "D:\ProgramFiles\MiniForge\",
            "python.condaPath": "D:\ProgramFiles\MiniForge\shell\condabin", # 
            "python.terminal.activateEnvironment": true,
        }
        ```

## 三、conda常用命令

1. 创建环境  
    ```bash
    conda create --name myenv python=3.9 # 创建名为myenv的，版本为3.9
    ```

2. 激活环境  
   ```bash
    conda activate myenv # 激活名为myenv的环境
   ```

3. 导出和导入环境
    + 为了方便在不同机器之间复制环境，可以将环境导出为environment.yml文件：
        ```bash
        conda env export > environment.yml
        ```
    + 在另一台机器上，可以使用以下命令根据environment.yml文件创建相同的环境：
        ```bash
        conda env create -f environment.yml
        ```

4. 删除虚拟环境
    ```bash
    conda env remove --name myenv
    ```

5. 增加软件源的频道
    ```bash
    conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud/conda-forge/
    conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/main/
    conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/free/
    ```

6. 查看软件源频道
    ```bash
    conda config --show channels
    ```

7. 移除频道和优先级
    ```bash
    conda config --remove channels 频道名 # 移除频道
    conda config --prepend channels 频道名 # 置顶频道
    ```

8. 更新软件包
    ```bash
    conda update --all # 更新所有软件包
    conda update conda # 指定更新软件包
    ```
    