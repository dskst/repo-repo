import os
import subprocess
from pathlib import Path
import re
from collections import defaultdict

def extract_repo_info(repo_url: str) -> tuple[str, str]:
    """
    Function to extract organization name and repository name from GitHub repository URL

    Args:
        repo_url: GitHub repository URL

    Returns:
        tuple[str, str]: (organization name, repository name)
    """
    # Split URL by slash
    parts = repo_url.rstrip('/').split('/')
    if len(parts) < 2:
        raise ValueError(f"Invalid repository URL: {repo_url}")

    # Last part is repository name, second to last is organization name
    repo_name = parts[-1]
    org_name = parts[-2]

    return org_name, repo_name

def run_command(command: str, cwd: str) -> str:
    """
    Function to execute a command and return its output

    Args:
        command: Command to execute
        cwd: Directory to execute the command in

    Returns:
        str: Command output
    """
    try:
        result = subprocess.run(
            command,
            cwd=cwd,
            shell=True,
            check=True,
            text=True,
            capture_output=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Command execution error: {command}")
        print(f"Error details: {e.stderr}")
        return ""

def analyze_developers(git_log_output: str) -> str:
    """
    Function to aggregate developers by domain

    Args:
        git_log_output: Output of git shortlog -sne

    Returns:
        str: Aggregated results by domain
    """
    # Regular expression to extract email address and commit count
    pattern = r'^\s*(\d+)\s+.*<([^>]+)>$'

    # Aggregate commit counts by domain
    domain_commits = defaultdict(int)

    for line in git_log_output.splitlines():
        match = re.match(pattern, line)
        if match:
            commits = int(match.group(1))
            email = match.group(2)
            domain = email.split('@')[-1] if '@' in email else 'unknown'
            domain_commits[domain] += commits

    # Sort by commit count in descending order
    sorted_domains = sorted(domain_commits.items(), key=lambda x: x[1], reverse=True)

    # Convert results to string
    result = []
    for domain, commits in sorted_domains:
        result.append(f"{commits},{domain}")

    return '\n'.join(result) 