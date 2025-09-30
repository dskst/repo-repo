import os
import sys
import pandas as pd
from pathlib import Path
from datetime import datetime
from math import exp
from repo_utils import extract_repo_info, run_command, analyze_developers

def analyze_repository(repo_url: str, base_dir: str, output_base_dir: str) -> bool:
    """
    Function to analyze a repository

    Args:
        repo_url: Repository URL
        base_dir: Base directory of repositories
        output_base_dir: Base directory for output

    Returns:
        bool: Whether the analysis was successful
    """
    try:
        # Extract organization name and repository name from URL
        org_name, repo_name = extract_repo_info(repo_url)

        # Repository path
        repo_path = os.path.join(base_dir, org_name, repo_name)

        # Create output directory
        org_output_dir = os.path.join(output_base_dir, org_name)
        Path(org_output_dir).mkdir(exist_ok=True)

        # Output file path
        output_file = os.path.join(org_output_dir, f"{repo_name}.md")

        # Skip if already analyzed
        if os.path.exists(output_file):
            print(f"Skip: {org_name}/{repo_name} (already analyzed)")
            return True

        print(f"Analysis started: {org_name}/{repo_name}")

        # Get lines of code
        cloc_output = run_command("cloc .", repo_path)

        # Get commit history
        git_log = run_command("git log --pretty=format:%H,%ct", repo_path)

        # Calculate weighted commit score
        now = datetime.now().timestamp()
        decay = 30 * 24 * 60 * 60  # Convert 30 days to seconds
        total_weight = 0.0

        for line in git_log.splitlines():
            commit_hash, timestamp = line.split(',')
            timestamp = float(timestamp)
            weight = exp(-(now - timestamp) / decay)
            total_weight += weight

        # Get developer information
        git_shortlog = run_command("git shortlog -sne", repo_path)
        developers = analyze_developers(git_shortlog)

        # Write results to Markdown file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"# {org_name}/{repo_name}\n\n")
            f.write(f"## Lines of Code\n")
            f.write("```\n")
            f.write(f"{cloc_output}")
            f.write("```\n\n")
            f.write(f"## Change Frequency Score\n")
            f.write(f"{total_weight:.8f}\n\n")
            f.write(f"## Developers\n")
            f.write(f"```\n{git_shortlog}```\n\n")
            f.write("### Developer Domains\n")
            f.write(f"```\n{developers}\n```\n")

        print(f"Analysis successful: {org_name}/{repo_name}")
        return True

    except Exception as e:
        print(f"Analysis failed: {repo_url} - Error: {str(e)}")
        return False

def analyze_local_repository(repo_path: str = ".", output_file: str = "analysis_result.md") -> bool:
    """
    Function to analyze the current directory or specified directory

    Args:
        repo_path: Directory path to analyze (default: current directory)
        output_file: Output filename (default: analysis_result.md)

    Returns:
        bool: Whether the analysis was successful
    """
    try:
        repo_path = os.path.abspath(repo_path)
        repo_name = os.path.basename(repo_path)

        print(f"Analysis started: {repo_path}")

        # Get lines of code
        cloc_output = run_command("cloc .", repo_path)

        # Get commit history
        git_log = run_command("git log --pretty=format:%H,%ct", repo_path)

        # Calculate weighted commit score
        now = datetime.now().timestamp()
        decay = 30 * 24 * 60 * 60  # Convert 30 days to seconds
        total_weight = 0.0

        for line in git_log.splitlines():
            if not line.strip():
                continue
            commit_hash, timestamp = line.split(',')
            timestamp = float(timestamp)
            weight = exp(-(now - timestamp) / decay)
            total_weight += weight

        # Get developer information
        git_shortlog = run_command("git shortlog -sne", repo_path)
        developers = analyze_developers(git_shortlog)

        # Write results to Markdown file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"# {repo_name}\n\n")
            f.write(f"## Lines of Code\n")
            f.write("```\n")
            f.write(f"{cloc_output}")
            f.write("```\n\n")
            f.write(f"## Change Frequency Score\n")
            f.write(f"{total_weight:.8f}\n\n")
            f.write(f"## Developers\n")
            f.write(f"```\n{git_shortlog}```\n\n")
            f.write("### Developer Domains\n")
            f.write(f"```\n{developers}\n```\n")

        print(f"Analysis successful: {repo_path}")
        print(f"Results written to {output_file}")
        return True

    except Exception as e:
        print(f"Analysis failed: {repo_path} - Error: {str(e)}")
        return False

def main():
    # Check command line arguments
    if len(sys.argv) < 2:
        print("Usage:")
        print("  Analyze from CSV: python repo_analyzer.py <CSV file path>")
        print("  Analyze current directory: python repo_analyzer.py --local [output filename]")
        sys.exit(1)

    # Local analysis mode
    if sys.argv[1] == "--local":
        output_file = sys.argv[2] if len(sys.argv) > 2 else "analysis_result.md"
        analyze_local_repository(".", output_file)
        sys.exit(0)

    csv_path = sys.argv[1]
    base_dir = "repos"
    output_base_dir = "analysis_results"

    # Create output directory
    Path(output_base_dir).mkdir(exist_ok=True)

    try:
        # Read CSV file (repourl only)
        df = pd.read_csv(csv_path, names=['repourl'])

        # Aggregate analysis results
        total = len(df)
        success = 0
        failed = 0
        skipped = 0

        # Analyze each repository
        for _, row in df.iterrows():
            success_flag = analyze_repository(row['repourl'], base_dir, output_base_dir)
            if success_flag:
                success += 1
            else:
                failed += 1

        # Display results
        print("\nProcessing completed")
        print(f"Total: {total} repositories")
        print(f"Success: {success} repositories")
        print(f"Failed: {failed} repositories")
        print(f"Skipped: {skipped} repositories")

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 