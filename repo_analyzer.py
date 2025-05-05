import os
import sys
import subprocess
import pandas as pd
from pathlib import Path

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

def analyze_repository(repo_name: str, repo_path: str, output_dir: str) -> bool:
    """
    リポジトリを解析し、結果をMarkdownファイルに出力する関数
    
    Args:
        repo_name: リポジトリ名
        repo_path: リポジトリのパス
        output_dir: 出力ディレクトリ
    
    Returns:
        bool: 解析が成功したかどうか
    """
    try:
        # 出力ディレクトリの作成
        Path(output_dir).mkdir(exist_ok=True)
        
        # 出力ファイルのパス
        output_file = os.path.join(output_dir, f"{repo_name}.md")
        
        # 解析結果の取得
        cloc_output = run_command("cloc .", repo_path)
        git_log_output = run_command("git shortlog -sne", repo_path)
        
        # Markdownファイルの作成
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(f"# {repo_name}\n\n")
            f.write("## コード行数\n")
            f.write("```\n")
            f.write(cloc_output)
            f.write("```\n\n")
            f.write("## 開発者\n")
            f.write("```\n")
            f.write(git_log_output)
            f.write("```\n")
        
        print(f"解析完了: {repo_name}")
        return True
        
    except Exception as e:
        print(f"解析失敗: {repo_name} - エラー: {str(e)}")
        return False

def main():
    # コマンドライン引数の確認
    if len(sys.argv) != 2:
        print("使用方法: python repo_analyzer.py <CSVファイルのパス>")
        sys.exit(1)

    csv_path = sys.argv[1]
    base_dir = "repos"
    output_dir = "analysis_results"

    try:
        # CSVファイルの読み込み
        df = pd.read_csv(csv_path, names=['reponame', 'repourl'])
        
        # 解析結果の集計
        total = len(df)
        success = 0
        failed = 0

        # 各リポジトリの解析
        for _, row in df.iterrows():
            repo_path = os.path.join(base_dir, row['reponame'])
            if os.path.exists(repo_path):
                if analyze_repository(row['reponame'], repo_path, output_dir):
                    success += 1
                else:
                    failed += 1
            else:
                print(f"リポジトリが存在しません: {row['reponame']}")
                failed += 1

        # 結果の表示
        print("\n処理完了")
        print(f"合計: {total} リポジトリ")
        print(f"成功: {success} リポジトリ")
        print(f"失敗: {failed} リポジトリ")

    except Exception as e:
        print(f"エラーが発生しました: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 