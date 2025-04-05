# AthenaUI

```
WARNING: This project is under active development and not all features are available yet.
```

## 项目简介 Introduction

AthenaUI是专为Athena++开发的一套终端用户界面(TUI)框架，旨在简化Athena++的使用流程，使用户能够通过直观的界面进行模拟配置、运行和后处理，而无需接触复杂的命令行交互。

### 主要功能 Features

- **配置模拟**：用于配置模拟参数，目前仅支持剪切盒模拟（Athena++中的`pgen/hgb.cpp`）
- **运行管理**：提供模拟运行监控和控制功能
- **后处理**：支持常规后处理算法与可视化



## 使用方法 Usage

如果环境支持联网，尽量使用`git clone`安装项目（如果有开发需求，自然是要先Fork一份比较方便）

```bash
git clone https://github.com/FrankHuaPKU/AthenaUI.git
```

如果无法联网，或者`git clone`安装失败，则推荐在Release页面直接下载最新版本。

### 配置与测试 Configuration and Test

利用`config.sh`脚本配置Athena++与AthenaUI的基础运行环境。首先`cd`到`AthenUI`根目录，运行配置脚本
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

### 调用命令 Running Commands

为了便于使用，这里提供两种情况下的用法。如果在本地运行模拟，或者远程服务器支持SSH连接，则推荐在VSCode等IDE中使用AthenaUI（当然集成了AI功能的Cursor更加方便，也是我目前的主要方案）。当然，这两种方法也可以同时使用，互不冲突。


#### VSCode等IDE（Recommended）

首先在`.bashrc`文件中添加如下命令：

```bash
source /path/to/your/AthenaUI/init.sh
```

例如：
```bash
# Author: hyy
# Date: Mar 31, 2025
source /public1/home/sc51248/hyy/Athena++/AthenaUI/init.sh
```

这样每次打开VSCode时，都会自动加载AthenaUI相关命令，并打印提示语，例如：

```bash
╔═══════════════════════════════════════════╗
║                                           ║
║    Welcome to AthenaUI! Version: 0.1.0    ║
║                                           ║
╚═══════════════════════════════════════════╝

目前支持的自定义命令：
  run：启动Athena++模拟（目前仅支持剪切盒模拟）
  mon：监控当前模拟case运行进度
```
展示欢迎语以及当前支持的所有功能，用户可直接参考提示信息使用。


#### 终端环境

直接在终端中使用AthenaUI时，每次启动终端往往不会位于`AthenaUI`根目录，因此需要每次手动`cd`到根目录再`source init.sh`，略显麻烦，因此考虑进一部自动化：在`.bashrc`文件中添加以下命令：

```bash
alias [your_alias]='cd /path/to/your/AthenaUI/ && source init.sh'
```
例如：
```bash
# Author: hyy
# Date: Apr 5, 2025
alias hyy='cd /public1/home/sc51248/hyy/Athena++/AthenaUI/ && source init.sh'
```

这样在任何目录下都只需一条命令即可启动AthenaUI，并且在当前对话下持续生效。在输入你的自定义命令并回车后，同样会自动打印提示语，例如：

```bash
╔═══════════════════════════════════════════╗
║                                           ║
║    Welcome to AthenaUI! Version: 0.1.0    ║
║                                           ║
╚═══════════════════════════════════════════╝

目前支持的自定义命令：
  run：启动Athena++模拟（目前仅支持剪切盒模拟）
  mon：监控当前模拟case运行进度
```
展示欢迎语以及当前支持的所有功能，用户可直接参考提示信息使用。


## 贡献与支持 Contribution and Support

如有问题或建议，请联系开发团队。 