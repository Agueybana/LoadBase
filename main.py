#!/usr/bin/env python3
"""
Codebase Prompt Generator

This script offers two modes:
  • Bulk selection:
      - Ask for the target folder of your codebase.
      - Load a persistent ignore file (ignore_paths.txt) that lists file or directory paths to ignore.
      - Let you add (or update) ignore paths interactively.
      - Recursively scan the codebase (excluding files/folders that match an ignore path).
  • Individual selection:
      - Optionally load file paths from 'target_files.txt' (or fallback to 'individual_files.sh') if available.
      - Then allow you to add additional file paths one at a time.
      - Generate a shell script 'individual_files.sh' with the selected file paths.

For both modes, the script:
  • Reads each file’s contents (skipping files with empty contents) and builds a single prompt string in the format:
      My codebase includes
      'path/to/file1' with 'file1 contents',
      'path/to/file2' with 'file2 contents',
      …
      .
  • Saves the final prompt in "codebase_prompt.txt".

No external dependencies are required.
"""

import os
import sys
from pathlib import Path

# File names for the ignore list, output prompt, and individual files script.
IGNORE_FILE = 'ignore_paths.txt'
OUTPUT_FILE = 'codebase_prompt.txt'
INDIVIDUAL_FILES_SCRIPT = 'individual_files.sh'
TARGET_FILES_FILE = 'target_files.txt'


def load_ignore_paths():
    """Load existing ignore paths from the ignore file, if it exists."""
    ignore_set = set()
    if os.path.exists(IGNORE_FILE):
        with open(IGNORE_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line:
                    ignore_set.add(line)
    return ignore_set


def save_ignore_paths(ignore_set):
    """Save the ignore paths to the ignore file."""
    with open(IGNORE_FILE, 'w', encoding='utf-8') as f:
        for path in sorted(ignore_set):
            f.write(path + "\n")


def prompt_for_ignore_paths(existing_ignore_set):
    """
    Prompt the user to enter file or directory paths to ignore.
    Paths can be entered either as relative (to the target folder) or absolute paths.
    Duplicate entries are ignored.
    """
    print("\nCurrent ignore paths:")
    if existing_ignore_set:
        for path in sorted(existing_ignore_set):
            print(" -", path)
    else:
        print(" (none)")
    print("\nEnter file or directory paths to ignore. Type 'done' when finished.")

    while True:
        user_input = input("Ignore path (or 'done'): ").strip()
        if user_input.lower() == 'done':
            break
        if not user_input:
            continue
        if user_input in existing_ignore_set:
            print(f"'{user_input}' is already in the ignore list. Skipping duplicate.")
        else:
            existing_ignore_set.add(user_input)
            print(f"Added '{user_input}' to ignore list.")
    return existing_ignore_set


def should_ignore(file_path, target_folder, ignore_set):
    """
    Determine whether a file should be ignored.
    If an ignore entry is an absolute path, compare it to the file's absolute path.
    Otherwise, compare the file's path relative to the target folder.
    """
    abs_file = file_path.resolve()
    try:
        rel_file = file_path.relative_to(target_folder).as_posix()
    except ValueError:
        # If file_path is not under target_folder, ignore it.
        return True

    for ignore in ignore_set:
        if os.path.isabs(ignore):
            # Check against the absolute path string.
            if str(abs_file).startswith(ignore):
                return True
        else:
            # Check against the relative path string.
            if rel_file.startswith(ignore):
                return True
    return False


def get_all_files(target_folder, ignore_set):
    """
    Recursively walk the target folder and return a list of file paths (as Path objects)
    that do not match any of the ignore paths.
    """
    files_to_include = []
    target_path = Path(target_folder)
    for file_path in target_path.rglob('*'):
        if file_path.is_file():
            if not should_ignore(file_path, target_path, ignore_set):
                files_to_include.append(file_path)
    return files_to_include


def generate_prompt(target_folder, files):
    """
    Generate a single prompt string that lists each file (by its relative path)
    along with its full contents in the format:

    My codebase includes
    'relative/path/to/file1' with 'contents of file1',
    'relative/path/to/file2' with 'contents of file2',
    ...
    .

    Files that are empty (after stripping whitespace) are skipped.
    """
    prompt_lines = []
    prompt_lines.append("My codebase includes")
    target_path = Path(target_folder)
    file_entries = []

    for file_path in files:
        relative_path = file_path.relative_to(target_path).as_posix()
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                contents = f.read()
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            continue

        # Skip if the file is empty after stripping whitespace.
        if not contents.strip():
            continue

        # Escape single quotes to avoid format issues.
        relative_path_escaped = relative_path.replace("'", "\\'")
        contents_escaped = contents.replace("'", "\\'")
        entry = f"'{relative_path_escaped}' with '{contents_escaped}'"
        file_entries.append(entry)

    # Join the file entries with commas (and newlines for readability)
    prompt_body = ",\n".join(file_entries)
    prompt_lines.append(prompt_body)
    prompt_lines.append(".")
    return "\n".join(prompt_lines)


def generate_prompt_individual(files):
    """
    Generate a prompt string for individually selected files.
    Uses the full file path as provided and includes each file's content in the format:

    My codebase includes
    'path/to/file1' with 'contents of file1',
    'path/to/file2' with 'contents of file2',
    ...
    .

    Files that are empty (after stripping whitespace) are skipped.
    """
    prompt_lines = []
    prompt_lines.append("My codebase includes")
    file_entries = []

    for file_path in files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                contents = f.read()
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            continue

        if not contents.strip():
            continue

        file_identifier = str(file_path)
        file_identifier_escaped = file_identifier.replace("'", "\\'")
        contents_escaped = contents.replace("'", "\\'")
        entry = f"'{file_identifier_escaped}' with '{contents_escaped}'"
        file_entries.append(entry)

    prompt_body = ",\n".join(file_entries)
    prompt_lines.append(prompt_body)
    prompt_lines.append(".")
    return "\n".join(prompt_lines)


def save_individual_files_script(files):
    """
    Generate a shell script with the list of individually selected file paths.
    """
    with open(INDIVIDUAL_FILES_SCRIPT, 'w', encoding='utf-8') as f:
        f.write("#!/bin/bash\n")
        f.write("# Script containing file paths used for prompt generation.\n")
        f.write("# You can use this file as input for future runs.\n\n")
        for file_path in files:
            f.write(str(file_path) + "\n")
    print(f"Script with file paths saved to '{INDIVIDUAL_FILES_SCRIPT}'.")


def load_individual_files_from_file():
    """
    Load individual file paths from 'target_files.txt' if available.
    If not, attempt to load from 'individual_files.sh' (ignoring shebang/comments).
    Returns a list of Path objects.
    """
    file_paths = []
    # First, try target_files.txt
    if os.path.exists(TARGET_FILES_FILE):
        with open(TARGET_FILES_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                file_path = line.strip()
                if file_path:
                    if os.path.isfile(file_path):
                        file_paths.append(Path(file_path))
                    else:
                        print(f"Warning: '{file_path}' from '{TARGET_FILES_FILE}' is not a valid file. Skipping.")
        if file_paths:
            print(f"Loaded {len(file_paths)} file paths from '{TARGET_FILES_FILE}'.")
            return file_paths
        else:
            print(f"'{TARGET_FILES_FILE}' exists but contains no valid file paths.")
    # Fallback to individual_files.sh if target_files.txt did not yield any files.
    if os.path.exists(INDIVIDUAL_FILES_SCRIPT):
        with open(INDIVIDUAL_FILES_SCRIPT, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                # Skip shebang and comment lines
                if line.startswith("#") or not line:
                    continue
                if os.path.isfile(line):
                    file_paths.append(Path(line))
                else:
                    print(f"Warning: '{line}' from '{INDIVIDUAL_FILES_SCRIPT}' is not a valid file. Skipping.")
        if file_paths:
            print(f"Loaded {len(file_paths)} file paths from '{INDIVIDUAL_FILES_SCRIPT}'.")
            return file_paths
        else:
            print(f"'{INDIVIDUAL_FILES_SCRIPT}' exists but contains no valid file paths.")
    print("No valid file paths could be loaded from either target file.")
    return None


def main():
    print("=== Codebase Prompt Generator ===")

    # Ask user for selection mode.
    while True:
        mode = input("Select mode: (bulk/individual): ").strip().lower()
        if mode in ('bulk', 'individual'):
            break
        print("Invalid input. Please enter 'bulk' or 'individual'.")

    if mode == 'bulk':
        # Bulk selection mode: use a target folder and ignore paths.
        target_folder = input("Enter the target folder path of your codebase: ").strip()
        if not os.path.isdir(target_folder):
            print(f"Error: '{target_folder}' is not a valid directory.")
            sys.exit(1)

        # Load (or initialize) the ignore paths.
        ignore_set = load_ignore_paths()

        # Ask the user if they want to update the ignore list.
        update_ignore = input("Would you like to update the ignore paths? (y/n): ").strip().lower()
        if update_ignore == 'y':
            ignore_set = prompt_for_ignore_paths(ignore_set)
            save_ignore_paths(ignore_set)
            print(f"\nIgnore paths updated and saved to '{IGNORE_FILE}'.")
        else:
            print("\nUsing existing ignore paths.")

        # Scan the target folder.
        print("\nScanning codebase...")
        files = get_all_files(target_folder, ignore_set)
        print(f"Found {len(files)} files to include in the prompt.")

        # Generate the final prompt text.
        prompt_text = generate_prompt(target_folder, files)
    else:
        # Individual selection mode.
        individual_files = []

        # Ask if user wants to load paths from file.
        load_from_file_option = input(
            f"Load file paths from '{TARGET_FILES_FILE}' (or fallback to '{INDIVIDUAL_FILES_SCRIPT}') if available? (y/n): ").strip().lower()
        if load_from_file_option == 'y':
            loaded_files = load_individual_files_from_file()
            if loaded_files:
                individual_files.extend(loaded_files)

        # Now allow the user to add additional file paths.
        print("You may now add additional file paths. Type 'done' when finished.")
        while True:
            file_input = input("File path (or 'done'): ").strip()
            if file_input.lower() == "done":
                break
            if not os.path.isfile(file_input):
                print(f"Warning: '{file_input}' is not a valid file. Please try again.")
                continue
            individual_files.append(Path(file_input))

        if individual_files:
            print(f"Collected {len(individual_files)} files for inclusion in the prompt.")
            # Generate the final prompt text using the individually selected files.
            prompt_text = generate_prompt_individual(individual_files)
            # Generate script with file paths.
            save_individual_files_script(individual_files)
        else:
            prompt_text = "No files selected for individual prompt generation."
            print("No files were selected for prompt generation.")

    # Write the prompt to the output file.
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(prompt_text)
    print(f"\nPrompt generated and saved to '{OUTPUT_FILE}'.")


if __name__ == '__main__':
    main()
