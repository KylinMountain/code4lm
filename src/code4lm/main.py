import argparse
import os
import pathspec
from pathlib import Path
from typing import List, Set, Optional


# Define the default set of directories to exclude.
DEFAULT_EXCLUDE_DIRS = {
    'venv', 'node_modules', '.git', '.idea', 'dist', 'build', '__pycache__'
}


def load_gitignore_spec(project_path: str) -> Optional[pathspec.PathSpec]:
    """
    Finds and parses the .gitignore file in the project root.
    Returns a PathSpec object if .gitignore is found, otherwise None.
    """
    gitignore_file = Path(project_path) / '.gitignore'
    if not gitignore_file.is_file():
        return None
    with open(gitignore_file, 'r', encoding='utf-8') as f:
        # Use 'gitwildmatch' for standard .gitignore pattern matching
        spec = pathspec.PathSpec.from_lines('gitwildmatch', f)
    return spec


def create_directory_tree(root_dir: str, exclude_dirs: Set[str], exclude_files: Set[str],
                          extensions: List[str], gitignore_spec: Optional[pathspec.PathSpec]) -> str:
    """
    Generates a string representation of the directory tree, respecting exclusion rules.
    """
    tree_lines = []
    root_path = Path(root_dir)

    def recursive_walk(current_dir: Path, prefix: str):
        try:
            dir_contents = sorted(list(current_dir.iterdir()), key=lambda p: (p.is_file(), p.name.lower()))
        except (FileNotFoundError, PermissionError):
            return

        items_to_render = []
        for item_path in dir_contents:
            relative_path = item_path.relative_to(root_path)

            # For directories, add a trailing slash for more accurate .gitignore matching
            relative_path_str = str(relative_path)
            if item_path.is_dir():
                relative_path_str += '/'

            # 1. Check against .gitignore rules first
            if gitignore_spec and gitignore_spec.match_file(relative_path_str):
                continue
            # 2. Check against command-line --exclude dirs
            if item_path.name in exclude_dirs:
                continue
            # 3. Check against command-line --exclude-files and extensions
            if item_path.is_file():
                if item_path.name in exclude_files:
                    continue
                if not any(item_path.name.endswith(ext) for ext in extensions):
                    continue
            items_to_render.append(item_path)

        for i, item_path in enumerate(items_to_render):
            is_last_item = (i == len(items_to_render) - 1)
            connector = "└── " if is_last_item else "├── "
            tree_lines.append(f"{prefix}{connector}{item_path.name}")

            if item_path.is_dir():
                new_prefix = prefix + ("    " if is_last_item else "│   ")
                recursive_walk(item_path, new_prefix)

    tree_lines.append(f"{root_path.name}/")
    recursive_walk(root_path, "")
    return "\n".join(tree_lines)


def merge_code(project_path: str, output_file: str, extensions: List[str], exclude_dirs: Set[str],
               exclude_files: Set[str], dry_run: bool, gitignore_spec: Optional[pathspec.PathSpec]):
    """
    Traverses a project directory, finds files with specified extensions,
    and merges their content into a single output file, respecting all exclusion rules.
    """
    print("🚀 Starting code merge for code4lm...")
    if dry_run:
        print("💧 NOTE: This is a dry run. No file will be written.")
    print(f"📂 Project Path: {project_path}")
    print(f"🎯 Target Extensions: {extensions}")
    print(f"🙈 Excluded Dirs (from --exclude): {sorted(list(exclude_dirs.difference(DEFAULT_EXCLUDE_DIRS)))}")
    if exclude_files:
        print(f"🙈 Excluded Files: {exclude_files}")
    if gitignore_spec:
        print("✅ Applying .gitignore rules.")
    print("----------------------------------------")

    files_to_merge = []
    project_root = Path(project_path)

    for root, dirs, files in os.walk(project_path, topdown=True):
        current_path = Path(root)

        # Filter directories using all rule sets
        original_dirs = list(dirs)
        dirs[:] = []
        for d in original_dirs:
            dir_path = current_path / d
            dir_path_relative = dir_path.relative_to(project_root)
            # Add trailing slash for directory matching
            dir_path_relative_str = str(dir_path_relative) + '/'

            if d in exclude_dirs:
                continue
            if gitignore_spec and gitignore_spec.match_file(dir_path_relative_str):
                continue
            dirs.append(d)

        # Filter files using all rule sets
        for filename in files:
            file_path = current_path / filename
            file_path_relative = file_path.relative_to(project_root)

            if filename in exclude_files:
                continue
            if gitignore_spec and gitignore_spec.match_file(str(file_path_relative)):
                continue
            if any(filename.endswith(ext) for ext in extensions):
                files_to_merge.append(file_path)

    if dry_run:
        print("🌳 The following directory tree would be generated (respecting all rules):")
        tree_string = create_directory_tree(project_path, exclude_dirs, exclude_files, extensions, gitignore_spec)
        print(tree_string)
        print("\n----------------------------------------")
        print("🔍 The following files would be merged:")
        if not files_to_merge:
            print("    (No files found matching the criteria)")
        for file_path in sorted(files_to_merge):
            print(f"    - {file_path}")
        print("\n✅ Dry run complete.")
        return

    try:
        with open(output_file, 'w', encoding='utf-8') as outfile:
            print("🌳 Generating directory tree...")
            tree_string = create_directory_tree(project_path, exclude_dirs, exclude_files, extensions, gitignore_spec)
            outfile.write("# ===== Project Directory Tree =====\n\n")
            outfile.write(tree_string)
            outfile.write("\n\n# ===================================\n")
            print("✅ Directory tree written to file.")

            for file_path in sorted(files_to_merge):
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as infile:
                        content = infile.read()
                        separator = f"\n\n# ===== File Path: {file_path} =====\n\n"
                        outfile.write(separator)
                        outfile.write(content)
                        print(f"✅ Merged: {file_path}")
                except Exception as e:
                    print(f"⚠️  Could not read file (skipped): {file_path} | Reason: {e}")
    except IOError as e:
        print(f"❌ Failed to create or write to output file: {e}")
        return

    print("----------------------------------------")
    print(f"🎉 Success! All code has been merged into {output_file}")


def main():
    parser = argparse.ArgumentParser(
        description="A tool to merge source code files from a project into a single file for LLMs.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    # ... (other arguments: --path, --output, --exts)
    parser.add_argument('--path', type=str, default='.', help='The root path of the project to process.')
    parser.add_argument('--output', type=str, default='all_code.txt', help='The name of the output file.')
    parser.add_argument('--exts', type=str,
                        default='.py,.js,.ts,.html,.css,.md,.go,.java,.cpp,.c,Dockerfile,docker-compose.yml,README.md',
                        help='Comma-separated list of file extensions to include.\nExample: .py,.js,.html')

    parser.add_argument(
        '--exclude', type=str, default='',
        help='Comma-separated list of ADDITIONAL directory names to exclude.\n'
             'The default list is already included:\n'
             f'({", ".join(sorted(list(DEFAULT_EXCLUDE_DIRS)))})'
    )
    parser.add_argument(
        '--exclude-files', type=str, default='',
        help='Comma-separated list of exact file names to exclude.\nExample: secret.key,temp.log'
    )
    parser.add_argument(
        '--no-gitignore', action='store_true',
        help='Do not respect .gitignore files.'
    )
    parser.add_argument(
        '--dry-run', action='store_true',
        help='Perform a dry run to see which files would be merged without creating the output file.'
    )

    args = parser.parse_args()

    # Load .gitignore rules unless disabled
    gitignore_spec = None
    if not args.no_gitignore:
        gitignore_spec = load_gitignore_spec(args.path)

    # Combine default and user-provided exclusion directories
    exclude_dirs_set = set(DEFAULT_EXCLUDE_DIRS)
    if args.exclude:
        user_excluded_dirs = {d.strip() for d in args.exclude.split(',') if d.strip()}
        exclude_dirs_set.update(user_excluded_dirs)

    extensions_list = [ext.strip() for ext in args.exts.split(',')]
    exclude_files_set = {f.strip() for f in args.exclude_files.split(',') if f.strip()}

    merge_code(args.path, args.output, extensions_list, exclude_dirs_set, exclude_files_set, args.dry_run,
               gitignore_spec)


if __name__ == "__main__":
    main()
