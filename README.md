# Code4LM
[English](./README.md) | [简体中文](./README_zh.md)

A simple and efficient command-line tool that merges all your project's source code into a single file, making it easy to copy and paste large codebases into Large Language Model (LLM) prompts.

## 🤔 What Problem Does It Solve?
When interacting with LLMs like ChatGPT, Gemini, or Claude for code-related tasks, we often need to provide the full context of a project. Manually copying and pasting content from multiple files is not only inefficient but also prone to errors.

Code4LM automates this process. With a single command, it scans your project and "packs" all relevant source files into a neatly organized text file, allowing you to copy the entire project's code at once.

## ✨ Key Features
📂 Smart Merging: Recursively traverses your project directory and merges all files with specified extensions.

🎯 Customizable File Types: Freely select which file types to include using the -exts flag (e.g., .py, .js, .md).

🙈 Flexible Exclusions: Easily exclude unnecessary directories (like node_modules or __pycache__) with --exclude and specific files with --exclude-files.

💧 Dry Run Mode: Use the --dry-run option to preview which files will be merged without actually creating a file.

⌨️ Pure Command-Line: Lightweight and easy to integrate into any workflow.

## ⚙️ Installation
Ensure you have Python 3.7+ installed. You can then install Code4LM directly from a Git repository (recommended) or from a local clone.

### Install from pip[Not Ready]:
```bash
pip install code4lm
```

### Install from GitHub:
```bash
pip install git+https://github.com/KylinMountain/code4lm.git
```

### Install from a Local Directory:

Clone or download the project to your local machine.

In your terminal, navigate to the project's root directory (where pyproject.toml is located).

Run the following command:
```
pip install .
```
Once installed, the code4lm command will be available globally in your system.

## 🚀 Usage
Simply run the `code4lm` command in the root directory of the project you want to process.

### Basic Usage
Running the command in a project directory will merge files using the default configuration:

```
code4lm
```

### Command-Line Options
```
usage: code4lm [-h] [--path PATH] [--output OUTPUT] [--exts EXTS] [--exclude EXCLUDE] [--exclude-files EXCLUDE_FILES] [--dry-run]

A tool to merge project source code files for Large Language Models.

options:
  -h, --help            show this help message and exit
  --path PATH           The root path of the project to process. (default: .)
  --output OUTPUT       The name of the output file. (default: all_code.txt)
  --exts EXTS           Comma-separated list of file extensions to include.
                        Example: .py,.js,.html
  --exclude EXCLUDE     Comma-separated list of directory names to exclude.
                        Example: venv,node_modules
  --exclude-files EXCLUDE_FILES
                        Comma-separated list of exact file names to exclude.
                        Example: secret.key,temp.log
  --dry-run             Perform a dry run to see which files would be merged without creating the output file.
```
### Examples
#### 1. Preview Which Files Will Be Merged (Dry Run)

See what will happen without writing any files:
```
code4lm --dry-run
```
#### 2. Merge a Frontend Project

Include only `.js` and `.css` files, while excluding the dist directory:
```
code4lm --exts ".js,.css" --exclude "dist" --output "frontend_bundle.txt"
```

#### 3. Exclude Specific Configuration Files

Skip merging config.dev.js and secret.json:
```
code4lm --exclude-files "config.dev.js,secret.json"
```

## 🤝 Contributing
Contributions of any kind are welcome! If you have a great idea or find a bug, feel free to submit a Pull Request or create an Issue.

## 📜 License
This project is licensed under the [MIT License](https://opensource.org/licenses/MIT).