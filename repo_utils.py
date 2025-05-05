import os
import subprocess
from pathlib import Path
import re
from collections import defaultdict

def extract_repo_info(repo_url: str) -> tuple[str, str]:
    """
    GitHubのリポジトリURLから組織名とリポジトリ名を抽出する関数
    
    Args:
        repo_url: GitHubのリポジトリURL
    
    Returns:
        tuple[str, str]: (組織名, リポジトリ名)
    """
    # URLをスラッシュで分割
    parts = repo_url.rstrip('/').split('/')
    if len(parts) < 2:
        raise ValueError(f"無効なリポジトリURLです: {repo_url}")
    
    # 末尾がリポジトリ名、その一つ前が組織名
    repo_name = parts[-1]
    org_name = parts[-2]
    
    return org_name, repo_name

def run_command(command: str, cwd: str) -> str:
    """
    コマンドを実行し、その出力を返す関数
    
    Args:
        command: 実行するコマンド
        cwd: コマンドを実行するディレクトリ
    
    Returns:
        str: コマンドの出力
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
        print(f"コマンド実行エラー: {command}")
        print(f"エラー内容: {e.stderr}")
        return ""

def analyze_developers(git_log_output: str) -> str:
    """
    開発者のドメインごとの集計を行う関数
    
    Args:
        git_log_output: git shortlog -sne の出力
    
    Returns:
        str: ドメインごとの集計結果
    """
    # メールアドレスとコミット数を抽出する正規表現
    pattern = r'^\s*(\d+)\s+.*<([^>]+)>$'
    
    # ドメインごとのコミット数を集計
    domain_commits = defaultdict(int)
    
    for line in git_log_output.splitlines():
        match = re.match(pattern, line)
        if match:
            commits = int(match.group(1))
            email = match.group(2)
            domain = email.split('@')[-1] if '@' in email else 'unknown'
            domain_commits[domain] += commits
    
    # コミット数の降順でソート
    sorted_domains = sorted(domain_commits.items(), key=lambda x: x[1], reverse=True)
    
    # 結果を文字列に変換
    result = []
    for domain, commits in sorted_domains:
        result.append(f"{commits},{domain}")
    
    return '\n'.join(result) 