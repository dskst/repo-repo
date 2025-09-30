# GitHub Repository Cloner

This program is a tool for batch cloning and analyzing GitHub repositories listed in a CSV file.

## Requirements

- Python 3.8 or higher
- pip
- cloc (code line counting tool)

## Installation

1. Clone the repository
```bash
git clone <repository-url>
cd <repository-directory>
```

2. Install dependencies
```bash
pip install -r requirements.txt
```

3. Install cloc
```bash
# For macOS
brew install cloc

# For Ubuntu/Debian
sudo apt-get install cloc

# For Windows
choco install cloc
```

## Usage

### Cloning Repositories

1. Prepare a CSV file
Create a CSV file in the following format:
```
reponame,repourl
example-repo,https://github.com/username/example-repo.git
```

2. Run the program
```bash
python repo_cloner.py <CSV file path>
```

### Analyzing Repositories

1. Analyze repositories cloned from CSV file
```bash
python repo_analyzer.py <CSV file path>
```

2. Analyze current directory
```bash
# Analyze with default output filename (analysis_result.md)
python repo_analyzer.py --local

# Specify output filename
python repo_analyzer.py --local <output filename>
```

## Output

### Clone Output

- Clone start: `Clone started: <repository name>`
- Clone success: `Clone successful: <repository name>`
- Clone failure: `Clone failed: <repository name> - Error: <error message>`
- Completion: Summary of total, successful, and failed repositories

### Analysis Output

- Analysis results are saved in the `analysis_results` directory
- A `<repository name>.md` file is created for each repository
- Analysis results include the following information:
  - Lines of code (cloc output)
  - Developer information (git shortlog output)

## Notes

- Cloned repositories are saved in the `repos` directory
- Failed repositories are skipped and the process continues to the next repository
- Existing repositories will not be overwritten
- Analysis results are saved in the `analysis_results` directory 