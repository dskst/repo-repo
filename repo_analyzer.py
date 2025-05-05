import os
import sys
import subprocess
import pandas as pd
from pathlib import Path
import math
import time

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

def calc_hotness(commit_timestamps, decay=30*24*60*60):
    """
    変更頻度スコアを計算（指数減衰）
    Args:
        commit_timestamps: コミットのUNIXタイムスタンプ（リスト）
        decay: 減衰パラメータ（秒）
    Returns:
        float: スコア
    """
    now = int(time.time())
    score = 0
    for ts in commit_timestamps:
        weight = math.exp(-(now - ts) / decay)
        score += weight
    return score

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
        
        # すでに分析済みの場合はスキップ
        if os.path.exists(output_file):
            print(f"スキップ: {repo_name} (すでに分析済み)")
            return True
        
        # 解析結果の取得
        cloc_output = run_command("cloc .", repo_path)
        git_log_output = run_command("git shortlog -sne", repo_path)

        # コミット時刻の取得
        commit_times_str = run_command("git log --pretty=format:\"%ct\"", repo_path)
        commit_timestamps = [int(line) for line in commit_times_str.strip().splitlines() if line.strip().isdigit()]
        hotness_score = calc_hotness(commit_timestamps)

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
            f.write("```\n\n")
            f.write("## 変更頻度スコア\n")
            f.write(f"{hotness_score:.8f}\n")
        
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
        skipped = 0

        # 各リポジトリの解析
        for _, row in df.iterrows():
            repo_path = os.path.join(base_dir, row['reponame'])
            if not os.path.exists(repo_path):
                print(f"リポジトリが存在しません: {row['reponame']}")
                failed += 1
                continue
                
            if analyze_repository(row['reponame'], repo_path, output_dir):
                success += 1
            else:
                failed += 1

        # 結果の表示
        print("\n処理完了")
        print(f"合計: {total} リポジトリ")
        print(f"成功: {success} リポジトリ")
        print(f"失敗: {failed} リポジトリ")
        print(f"スキップ: {skipped} リポジトリ")

    except Exception as e:
        print(f"エラーが発生しました: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 