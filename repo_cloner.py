import os
import sys
import pandas as pd
from git import Repo
from pathlib import Path
from repo_utils import extract_repo_info

def clone_repository(repo_url: str, base_dir: str) -> tuple[bool, str, str]:
    """
    Function to clone a repository

    Args:
        repo_url: Repository URL
        base_dir: Base directory for cloning

    Returns:
        tuple[bool, str, str]: (success status, organization name, repository name)
    """
    try:
        # Extract organization name and repository name from URL
        org_name, repo_name = extract_repo_info(repo_url)

        # Create directory for each organization
        org_dir = os.path.join(base_dir, org_name)
        Path(org_dir).mkdir(exist_ok=True)

        # Target clone path
        target_dir = os.path.join(org_dir, repo_name)

        # Skip if already cloned
        if os.path.exists(target_dir):
            print(f"Skip: {org_name}/{repo_name} (already cloned)")
            return True, org_name, repo_name

        print(f"Clone started: {org_name}/{repo_name}")
        Repo.clone_from(repo_url, target_dir)
        print(f"Clone successful: {org_name}/{repo_name}")
        return True, org_name, repo_name
    except Exception as e:
        print(f"Clone failed: {repo_url} - Error: {str(e)}")
        return False, "", ""

def main():
    # Check command line arguments
    if len(sys.argv) != 2:
        print("Usage: python repo_cloner.py <CSV file path>")
        sys.exit(1)

    csv_path = sys.argv[1]
    base_dir = "repos"

    # Create base directory
    Path(base_dir).mkdir(exist_ok=True)

    try:
        # Read CSV file (repourl only)
        df = pd.read_csv(csv_path, names=['repourl'])

        # Aggregate clone results
        total = len(df)
        success = 0
        failed = 0
        skipped = 0

        # Clone each repository
        for _, row in df.iterrows():
            success_flag, org_name, repo_name = clone_repository(row['repourl'], base_dir)
            if success_flag:
                if org_name and repo_name:
                    success += 1
                else:
                    skipped += 1
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