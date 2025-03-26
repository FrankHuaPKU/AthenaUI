# AthenaUI

```
WARNING: This project is under active development and not all features are available yet.
```

## 项目简介 Introduction

AthenaUI是专为Athena++开发的一套终端用户界面(TUI)框架，旨在简化Athena++的使用流程，使用户能够通过直观的界面进行模拟配置、运行和后处理，而无需接触复杂的命令行交互。

### 主要功能 Features

- **配置模拟**：用于配置模拟参数，目前仅支持剪切盒模拟（`pgen/hgb.cpp`）
- **运行管理**：提供模拟运行监控和控制功能
- **后处理**：支持常规后处理算法与可视化



## 使用方法 Usage

### 配置与测试 Configuration and Test

利用`config.sh`脚本配置Athena++与AthenaUI的基础运行环境。

首先`cd`到`AthenUI`根目录，运行配置脚本
   ```bash
   source config.sh
   ```
再根据自动提示信息配置环境，并完成测试。如果测试正常通过，将提示以下信息：
   ```bash
   Results:
      mpi.mpi_linwave: passed; time elapsed: 210 s
      pgen.hdf5_reader_parallel: passed; time elapsed: 50.6 s
      shearingbox.mri2d: passed; time elapsed: 95.6 s

   Summary: 3 out of 3 tests passed


   ==============================================

   Tests completed. Please review the output above.

   If the tests were successful, you can initialize the AthenaUI environment by running:
   source init.sh

   ==============================================
   ```
如果测试未通过，请根据提示信息检查配置（也可以手动修改`current.user`配置文件）。

### 日常使用 Running commands

首先初始化环境：
   ```bash
   source init.sh
   ```
此时会加载并打印出当前兼容的所有命令：（例如）
   - `run`: 配置新的模拟
   - `slc`: 生成2D切片图
   - `spc`: 绘制湍流谱
调用命令即可启动对应的TUI，实现对应功能。

### 快捷方式 Shortcut

为避免每次使用AthenaUI时都要`cd`到根目录再`source init.sh`，可以在`~/.bashrc`文件中添加每个用户专属的自定义命令，实现从任意目录启动AthenaUI：

```bash
alias [your_alias]='cd $ATHENAUI_PATH && source init.sh'
```

## 贡献与支持 Contribution and Support

如有问题或建议，请联系开发团队。 