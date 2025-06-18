import argparse
import os
import sys
import asyncio
from pathlib import Path
from typing import List, Set, Optional

import pathspec
from fastmcp import FastMCP, Context

DEFAULT_EXCLUDE_DIRS = {
    'venv', 'node_modules', '.git', '.idea', 'dist', 'build', '__pycache__'
}


def load_gitignore_spec(project_path: str) -> Optional[pathspec.PathSpec]:
    """Finds and parses the .gitignore file in the project root."""
    gitignore_file = Path(project_path) / '.gitignore'
    if not gitignore_file.is_file():
        return None
    try:
        with open(gitignore_file, 'r', encoding='utf-8') as f:
            spec = pathspec.PathSpec.from_lines('gitwildmatch', f)
        return spec
    except IOError:
        return None


def create_directory_tree(root_dir: str, exclude_dirs: Set[str], exclude_files: Set[str],
                          extensions: List[str], gitignore_spec: Optional[pathspec.PathSpec]) -> str:
    """Generates a string representation of the directory tree, respecting exclusion rules."""
    tree_lines = []
    root_path = Path(root_dir)

    def recursive_walk(current_dir: Path, prefix: str):
        try:
            # Sort directories first, then files
            dir_contents = sorted(list(current_dir.iterdir()), key=lambda p: (p.is_file(), p.name.lower()))
        except (FileNotFoundError, PermissionError):
            return

        # Filter items to be rendered based on exclusion rules
        items_to_render = []
        for item_path in dir_contents:
            relative_path_str = str(item_path.relative_to(root_path))
            if item_path.is_dir():
                relative_path_str += '/'

            if gitignore_spec and gitignore_spec.match_file(relative_path_str):
                continue
            if item_path.name in exclude_dirs:
                continue

            # For directories, we let them be rendered. For files, we apply more checks.
            if item_path.is_file():
                if item_path.name in exclude_files:
                    continue
                # The file must match one of the extensions to be included in the tree
                if not any(item_path.name.endswith(ext) for ext in extensions):
                    continue
            items_to_render.append(item_path)

        # Build the tree string
        for i, item_path in enumerate(items_to_render):
            is_last_item = (i == len(items_to_render) - 1)
            connector = "└── " if is_last_item else "├── "
            tree_lines.append(f"{prefix}{connector}{item_path.name}")
            if item_path.is_dir():
                new_prefix = prefix + ("    " if is_last_item else "│   ")
                recursive_walk(item_path, new_prefix)

    tree_lines.append(f"{root_path.resolve().name}/")
    recursive_walk(root_path, "")
    return "\n".join(tree_lines)


def find_files_to_process(project_path: str, extensions: List[str], exclude_dirs: Set[str],
                          exclude_files: Set[str], gitignore_spec: Optional[pathspec.PathSpec]) -> List[Path]:
    """
    Finds all files matching the criteria without reading their content.
    Returns a sorted list of Path objects relative to the project root.
    """
    files_to_process = []
    project_root = Path(project_path)

    for root, dirs, files in os.walk(project_path, topdown=True):
        current_path = Path(root)
        # --- Directory Exclusion Logic ---
        original_dirs = list(dirs)
        dirs[:] = []
        for d in original_dirs:
            # Use relative path for gitignore matching
            dir_path_relative_str = str((current_path / d).relative_to(project_root)) + '/'
            if d in exclude_dirs or (gitignore_spec and gitignore_spec.match_file(dir_path_relative_str)):
                continue
            dirs.append(d)

        # --- File Inclusion/Exclusion Logic ---
        for filename in files:
            file_path = current_path / filename
            file_path_relative = file_path.relative_to(project_root)
            if filename in exclude_files or (gitignore_spec and gitignore_spec.match_file(str(file_path_relative))):
                continue
            # Check for exact matches or suffix matches in extensions list
            if any(file_path.name == ext or file_path.name.endswith(ext) for ext in extensions):
                files_to_process.append(file_path_relative)

    return sorted(files_to_process)


def generate_output_string(project_path: str, extensions: List[str], exclude_dirs: Set[str],
                           exclude_files: Set[str], gitignore_spec: Optional[pathspec.PathSpec],
                           logger=print) -> str:
    """
    Core logic to generate the merged code string. It walks the filesystem,
    builds the directory tree, and concatenates file contents.
    """
    output_parts = []
    project_root = Path(project_path)

    logger("🌳 Generating directory tree...")
    tree_string = create_directory_tree(project_path, exclude_dirs, exclude_files, extensions, gitignore_spec)
    output_parts.append("# ===== Project Directory Tree =====\n")
    output_parts.append(tree_string)
    output_parts.append("\n\n# ===================================\n")
    logger("✅ Directory tree generated.")

    logger("🔍 Finding files to merge...")
    files_to_merge_relative = find_files_to_process(project_path, extensions, exclude_dirs, exclude_files,
                                                    gitignore_spec)

    logger(f"📖 Found {len(files_to_merge_relative)} files to merge. Reading content...")
    for file_path_relative in files_to_merge_relative:
        file_path_absolute = project_root / file_path_relative
        try:
            with open(file_path_absolute, 'r', encoding='utf-8', errors='ignore') as infile:
                content = infile.read()
                # Use relative path for display
                separator = f"\n\n# ===== File Path: {file_path_relative} =====\n\n"
                output_parts.append(separator)
                output_parts.append(content)
                logger(f"✅ Merged: {file_path_relative}")
        except Exception as e:
            logger(f"⚠️  Could not read file (skipped): {file_path_relative} | Reason: {e}")

    return "".join(output_parts)


# ===== CLI Functionality (Largely unchanged) =====

def merge_code(project_path: str, output_file: str, extensions: List[str], exclude_dirs: Set[str],
               exclude_files: Set[str], dry_run: bool, gitignore_spec: Optional[pathspec.PathSpec]):
    # This function now uses the refactored generate_output_string
    print("🚀 Starting code merge for code4lm...")
    if dry_run:
        print("💧 NOTE: This is a dry run. No file will be written.")
    # ... (rest of the printing logic is the same)
    output_content = generate_output_string(project_path, extensions, exclude_dirs, exclude_files, gitignore_spec)
    if dry_run:
        print("\n\n# ===== Generated Output =====\n")
        print(output_content)
        print("\n✅ Dry run complete.")
        return
    try:
        with open(output_file, 'w', encoding='utf-8') as outfile:
            outfile.write(output_content)
        print("----------------------------------------")
        print(f"🎉 Success! All code has been merged into {output_file}")
    except IOError as e:
        print(f"❌ Failed to create or write to output file: {e}")


def main_cli():
    """Parses command-line arguments and runs the merge_code function."""
    parser = argparse.ArgumentParser(
        description="A tool to merge source code files from a project into a single file for LLMs.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument('--path', type=str, default='.', help='The root path of the project to process.')
    parser.add_argument('--output', type=str, default='all_code.txt', help='The name of the output file.')
    parser.add_argument('--exts', type=str,
                        default='.py,.js,.ts,.html,.css,.md,.go,.java,.cpp,.c,Dockerfile,docker-compose.yml,README.md',
                        help='Comma-separated list of file extensions or full filenames to include.\nExample: .py,.js,README.md')
    parser.add_argument('--exclude', type=str, default='',
                        help='Comma-separated list of ADDITIONAL directory names to exclude.\nThe default list is '
                             'already included:\n' f'({", ".join(sorted(list(DEFAULT_EXCLUDE_DIRS)))})')
    parser.add_argument('--exclude-files', type=str, default='',
                        help='Comma-separated list of exact file names to exclude.\nExample: secret.key,temp.log')
    parser.add_argument('--no-gitignore', action='store_true', help='Do not respect .gitignore files.')
    parser.add_argument('--dry-run', action='store_true',
                        help='Perform a dry run to see which files would be merged without creating the output file.')
    args = parser.parse_args(sys.argv[1:])
    gitignore_spec = load_gitignore_spec(args.path) if not args.no_gitignore else None
    exclude_dirs_set = set(DEFAULT_EXCLUDE_DIRS)
    if args.exclude:
        exclude_dirs_set.update(d.strip() for d in args.exclude.split(',') if d.strip())
    extensions_list = [ext.strip() for ext in args.exts.split(',')]
    exclude_files_set = {f.strip() for f in args.exclude_files.split(',') if f.strip()}
    merge_code(args.path, args.output, extensions_list, exclude_dirs_set, exclude_files_set, args.dry_run,
               gitignore_spec)


# ===== MCP Server Functionality (Refactored) =====
mcp = FastMCP(
    name="Code4LM Interactive Code Browser"
)

# --- Default Parameters ---
DEFAULT_EXTS_STR = '.py,.js,.ts,.html,.css,.md,.go,.java,.cpp,.c,Dockerfile,docker-compose.yml,README.md'


# --- Helper for Parameter Processing ---
def process_mcp_args(extensions, exclude_dirs, exclude_files, no_gitignore, path):
    gitignore_spec = load_gitignore_spec(path) if not no_gitignore else None

    final_exclude_dirs = set(DEFAULT_EXCLUDE_DIRS)
    if exclude_dirs:
        final_exclude_dirs.update(exclude_dirs)

    final_exclude_files = set(exclude_files) if exclude_files else set()

    ext_str = extensions if extensions else DEFAULT_EXTS_STR
    final_extensions = [ext.strip() for ext in ext_str.split(',')]

    return final_extensions, final_exclude_dirs, final_exclude_files, gitignore_spec


# NEW TOOL 1: List project structure
@mcp.tool
async def list_project_structure(
        ctx: Context,
        path: str,
        extensions: Optional[str] = None,
        exclude_dirs: Optional[List[str]] = None,
        exclude_files: Optional[List[str]] = None,
        no_gitignore: bool = False,
) -> str:
    """
    Scans a project directory, returning its file structure tree and a list of processable files.

    This is a discovery tool. It shows available files based on filters without reading them.
    Use 'get_files_content' to read specific files from the returned list.

    Args:
        ctx: The MCP context.
        path: The root path of the project.
        extensions: Comma-separated file extensions/names to include (e.g., '.py,.js,README.md'). Uses defaults if None.
        exclude_dirs: List of additional directory names to exclude.
        exclude_files: List of exact file names to exclude.
        no_gitignore: If True, .gitignore is ignored.

    Returns:
        A formatted string with the directory tree and the list of matched files.
    """
    await ctx.info(f"🚀 Listing structure for project: {path}")

    final_exts, final_excludes, final_files, gitignore_spec = process_mcp_args(extensions, exclude_dirs, exclude_files,
                                                                               no_gitignore, path)

    loop = asyncio.get_running_loop()

    def run_sync_tasks():
        tree = create_directory_tree(path, final_excludes, final_files, final_exts, gitignore_spec)
        files = find_files_to_process(path, final_exts, final_excludes, final_files, gitignore_spec)
        return tree, files

    tree_string, files_found = await loop.run_in_executor(None, run_sync_tasks)

    files_list_str = "\n".join([str(p) for p in files_found])

    output = (
        f"# ===== Project Directory Tree for '{Path(path).name}' =====\n"
        f"{tree_string}\n\n"
        f"# ===== Matched Files ({len(files_found)}) =====\n"
        "# Use these relative paths with the 'get_files_content' tool.\n"
        f"{files_list_str}"
    )

    await ctx.info("✅ Project structure analysis complete.")
    return output


# NEW TOOL 2: Get content of specific files
@mcp.tool
async def get_files_content(
        ctx: Context,
        project_path: str,
        relative_file_paths: List[str]
) -> str:
    """
    Reads and returns the content of specific files from a project.

    Args:
        ctx: The MCP context.
        project_path: The root path of the project (e.g., '.').
        relative_file_paths: A list of relative paths to read (e.g., ["src/main.py", "README.md"]).
                             Obtain these from the 'list_project_structure' tool.
    """
    await ctx.info(f"📖 Reading {len(relative_file_paths)} file(s) from '{project_path}'...")

    output_parts = []
    project_root = Path(project_path)

    for relative_path_str in relative_file_paths:
        file_path = (project_root / relative_path_str).resolve()

        # Security check: Ensure the file is within the project directory
        if not str(file_path).startswith(str(project_root.resolve())):
            msg = f"🚫 Security Alert: Access denied to '{relative_path_str}' (outside project root)."
            await ctx.warning(msg)
            output_parts.append(f"# ===== Access Denied: {relative_path_str} =====\n")
            continue

        if not file_path.is_file():
            msg = f"⚠️ File not found (skipped): {relative_path_str}"
            await ctx.warning(msg)
            output_parts.append(f"# ===== File Not Found: {relative_path_str} =====\n")
            continue

        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as infile:
                content = infile.read()
                separator = f"\n\n# ===== File Path: {relative_path_str} =====\n\n"
                output_parts.append(separator)
                output_parts.append(content)
                await ctx.info(f"✅ Read: {relative_path_str}")
        except Exception as e:
            msg = f"⚠️ Could not read file (skipped): {relative_path_str} | Reason: {e}"
            await ctx.error(msg)
            output_parts.append(f"# ===== Error Reading File: {relative_path_str} | Reason: {e} =====\n")

    if not output_parts:
        return "No files were read. Please check the file paths."

    await ctx.info("✅ All requested files have been processed.")
    return "".join(output_parts)


# ===== Main Entrypoint =====

def run_entrypoint():
    """
    This function is the entry point for the 'code4lm' command-line script.
    It checks for the 'serve' command to decide whether to start the MCP server
    or run the standard CLI tool.
    """
    if len(sys.argv) > 1 and sys.argv[1] == 'serve':
        if mcp:
            sys.argv.pop(1)
            print("🚀 Starting FastMCP server for Code4LM...")
            print("Registered tools: list_project_structure, get_files_content")
            mcp.run()
        else:
            print("Could not start MCP server because 'fastmcp' is not installed.")
    else:
        main_cli()


if __name__ == "__main__":
    run_entrypoint()
