import argparse
import os
from pathlib import Path
from typing import List, Set


def merge_code(project_path: str, output_file: str, extensions: List[str], exclude_dirs: Set[str],
               exclude_files: Set[str], dry_run: bool):
    """
    Traverses a project directory, finds files with specified extensions,
    and merges their content into a single output file, excluding specified
    directories and files.

    Args:
        project_path: The root directory of the project to scan.
        output_file: The path to the file where the merged code will be saved.
        extensions: A list of file extensions to include (e.g., ['.py', '.js']).
        exclude_dirs: A set of directory names to exclude from the scan.
        exclude_files: A set of exact file names to exclude from the scan.
        dry_run: If True, prints the files that would be merged without creating the output file.
    """
    print("🚀 Starting code merge for code4lm...")
    if dry_run:
        print("💧 NOTE: This is a dry run. No file will be written.")
    print(f"📂 Project Path: {project_path}")
    print(f"🎯 Target Extensions: {extensions}")
    print(f"🙈 Excluded Dirs: {exclude_dirs}")
    if exclude_files:
        print(f"🙈 Excluded Files: {exclude_files}")
    print("----------------------------------------")

    # This list will hold the paths of files to be merged.
    files_to_merge = []

    for root, dirs, files in os.walk(project_path):
        # Modify the dirs list in-place to prevent os.walk from entering excluded directories
        dirs[:] = [d for d in dirs if d not in exclude_dirs]

        for filename in files:
            # Check if the current file should be excluded
            if filename in exclude_files:
                continue

            # Check if the file has one of the desired extensions
            if any(filename.endswith(ext) for ext in extensions):
                files_to_merge.append(Path(root) / filename)

    # If it's a dry run, just print the list of files and exit.
    if dry_run:
        print("🔍 The following files would be merged:")
        if not files_to_merge:
            print("   (No files found matching the criteria)")
        for file_path in files_to_merge:
            print(f"   - {file_path}")
        print("\n✅ Dry run complete.")
        return

    # If not a dry run, proceed with writing the file.
    try:
        with open(output_file, 'w', encoding='utf-8') as outfile:
            for file_path in files_to_merge:
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
    """
    Parses command-line arguments and runs the merge_code function.
    """
    parser = argparse.ArgumentParser(
        description="A tool to merge source code files from a project into a single file for LLMs.",
        formatter_class=argparse.RawTextHelpFormatter
    )

    parser.add_argument(
        '--path',
        type=str,
        default='.',
        help='The root path of the project to process.'
    )
    parser.add_argument(
        '--output',
        type=str,
        default='all_code.txt',
        help='The name of the output file.'
    )
    parser.add_argument(
        '--exts',
        type=str,
        default='.py,.js,.ts,.html,.css,.md,.go,.java,.cpp,.c,Dockerfile,docker-compose.yml,README.md',
        help='Comma-separated list of file extensions to include.\nExample: .py,.js,.html'
    )
    parser.add_argument(
        '--exclude',
        type=str,
        default='venv,node_modules,.git,.idea,dist,build,__pycache__',
        help='Comma-separated list of directory names to exclude.\nExample: venv,node_modules'
    )
    parser.add_argument(
        '--exclude-files',
        type=str,
        default='',
        help='Comma-separated list of exact file names to exclude.\nExample: secret.key,temp.log'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Perform a dry run to see which files would be merged without creating the output file.'
    )

    args = parser.parse_args()

    # Convert comma-separated strings to a list/set
    extensions_list = [ext.strip() for ext in args.exts.split(',')]
    exclude_dirs_set = {d.strip() for d in args.exclude.split(',')}
    exclude_files_set = {f.strip() for f in args.exclude_files.split(',') if f.strip()}

    merge_code(args.path, args.output, extensions_list, exclude_dirs_set, exclude_files_set, args.dry_run)


if __name__ == "__main__":
    main()
