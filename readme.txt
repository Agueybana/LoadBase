# LoadBase - Make a giant prompt with all your codebase
By Gabriel Suárez 2025


## Overview

LoadBase is a Python script designed to generate structured prompts containing the contents of a codebase. This allows users to provide AI models with comprehensive context when debugging, asking questions, or analyzing their projects.

### Features
- **Bulk Selection Mode**:
  - Select an entire folder as the target.
  - Uses an `ignore_paths.txt` file to exclude unwanted files and directories.
  - Allows interactive updates to ignored paths.
  - Recursively scans and processes the codebase.
- **Individual Selection Mode**:
  - Load file paths from `target_files.txt` (or fallback to `individual_files.sh`).
  - Manually add additional file paths one at a time.
  - Saves the selected file paths to `individual_files.sh` for future use.
- **Prompt Generation**:
  - Reads each file's contents, skipping empty files.
  - Outputs a structured prompt in `codebase_prompt.txt` in the format:
    ```
    My codebase includes
    'path/to/file1' with 'file1 contents',
    'path/to/file2' with 'file2 contents',
    …
    .
    ```
- **No External Dependencies**: LoadBase runs using only Python’s standard library.

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/Agueybana/LoadBase.git
   cd LoadBase
   ```
2. Ensure Python 3 is installed:
   ```bash
   python3 --version
   ```

## Usage

### Running LoadBase

Run the script interactively:
```bash
./loadbase.py
```
Or, if Python is not set as an executable:
```bash
python3 loadbase.py
```

### Selecting a Codebase (Bulk Mode)
1. Enter the path to the root folder of your codebase.
2. Review and update the `ignore_paths.txt` file if necessary.
3. The script will recursively scan the folder, excluding ignored files.
4. The generated prompt is saved to `codebase_prompt.txt`.

### Selecting Files Individually
1. Choose to load previously selected files from `target_files.txt` or `individual_files.sh`.
2. Add additional file paths manually if needed.
3. The prompt is saved to `codebase_prompt.txt`, and the selected files are saved in `individual_files.sh`.

## Best Practices

- **Remove API Keys and Sensitive Data**: The script does not automatically filter out API keys or secrets. Always review and sanitize the generated prompt before sharing.
- **Using the Prompt Effectively**: The prompt is structured for easy copy-pasting into AI models. The recommended workflow:
  1. Copy the relevant error message or question.
  2. Paste it along with the generated prompt into an AI model to get precise answers.
  3. If needed, refine the input by adding or removing files manually.

## Contributing

Contributions are welcome! Feel free to submit issues, feature requests, or pull requests.

## License

This project is licensed under the MIT License.

