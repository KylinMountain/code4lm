# Code4LM
[English](./README.md) | [简体中文](./README_zh.md)

一个简单高效的命令行工具，能将整个项目的源代码合并到一个文件中，让你轻松地将大型项目代码粘贴到大语言模型（LLM）的对话框中。

## 🤔 它解决了什么问题？
在与 ChatGPT、Gemini、Claude 等大语言模型进行代码相关的对话时，我们常常需要提供项目的完整上下文。手动逐个复制粘贴多个文件的内容不仅效率低下，而且容易出错。

Code4LM 通过一个简单的命令，自动化地扫描您的项目，将所有相关的代码文件“打包”成一个整洁的文本文件，让您能够一次性复制全部代码。

## ✨ 主要功能
📂 智能合并: 递归地遍历项目目录，将所有指定后缀的文件合并输出。

🎯 自定义文件类型: 通过 -exts 参数自由选择要包含的文件类型（如 .py, .js, .md）。

🙈 灵活排除: 通过 --exclude 排除不必要的目录（如 node_modules, __pycache__），并通过 --exclude-files 排除特定的文件。

💧 演习模式: 使用 --dry-run 选项可以在不生成文件的情况下，预览哪些文件将被合并。

⌨️ 纯命令行: 轻量级，易于集成到任何工作流中。

## ⚙️ 安装
确保您的电脑已安装 Python 3.7+。然后，您可以直接通过 pip 或者从项目的 Git 仓库安装（推荐），或者从本地克隆的目录安装。

### 快速安装(推荐):
```bash
pip install code4lm
```

### 从 GitHub 安装 (未来):
```bash
pip install git+https://github.com/your-username/code4lm.git
```

### 从本地目录安装:

克隆或下载项目到本地。

在终端中进入项目根目录（即 pyproject.toml 文件所在的目录）。

运行以下命令：
```bash
pip install .
```
安装完成后，code4lm 命令将在您的系统中全局可用。

## 🚀 使用方法
直接在您想要处理的项目根目录下运行 code4lm 命令即可。

### 基本用法
在项目目录下运行，将会使用默认配置进行合并：
```bash
code4lm
```

### 常用选项
```
用法: code4lm [-h] [--path PATH] [--output OUTPUT] [--exts EXTS] [--exclude EXCLUDE] [--exclude-files EXCLUDE_FILES] [--dry-run]

一个为大模型合并项目源代码文件的工具。

选项:
  -h, --help            显示帮助信息并退出
  --path PATH           要处理的项目根目录路径。 (默认: .)
  --output OUTPUT       输出文件名。 (默认: all_code.txt)
  --exts EXTS           要包含的文件后缀名，以逗号分隔。
                        示例: .py,.js,.html
  --exclude EXCLUDE     要排除的目录名，以逗号分隔。
                        示例: venv,node_modules
  --exclude-files EXCLUDE_FILES
                        要排除的精确文件名，以逗号分隔。
                        示例: secret.key,temp.log
  --dry-run             执行演习，查看哪些文件将被合并，但不实际生成文件。
```

### 示例
#### 1. 预览哪些文件将被合并 (演习模式)

在不生成任何文件的情况下，查看将要发生什么：
```bash
code4lm --dry-run
```

#### 2. 合并一个前端项目

只包含 .js 和 .css 文件，并排除 dist 目录：
```bash
code4lm --exts ".js,.css" --exclude "dist" --output "frontend_bundle.txt"
```

#### 3. 排除特定的配置文件

在合并时，跳过 `config.dev.js` 和 `secret.json` 这两个文件：
```bash
code4lm --exclude-files "config.dev.js,secret.json"
```

## 🤝 贡献
欢迎任何形式的贡献！如果您有好的想法或发现了 Bug，请随时提交 Pull Request 或创建 Issue。

## 📜 许可证
本项目基于 [MIT License](https://opensource.org/licenses/MIT) 开源。