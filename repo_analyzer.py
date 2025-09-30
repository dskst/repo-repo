import os
import sys
import pandas as pd
from pathlib import Path
from datetime import datetime
from math import exp
from repo_utils import extract_repo_info, run_command, analyze_developers

def analyze_repository(repo_url: str, base_dir: str, output_base_dir: str) -> bool:
    """
    リポジトリを分析する関数

    Args:
        repo_url: リポジトリのURL
        base_dir: リポジトリのベースディレクトリ
        output_base_dir: 出力先のベースディレクトリ

    Returns:
        bool: 分析が成功したかどうか
    """
    try:
        # URLから組織名とリポジトリ名を抽出
        org_name, repo_name = extract_repo_info(repo_url)

        # リポジトリのパス
        repo_path = os.path.join(base_dir, org_name, repo_name)

        # 出力先ディレクトリの作成
        org_output_dir = os.path.join(output_base_dir, org_name)
        Path(org_output_dir).mkdir(exist_ok=True)

        # 出力ファイルのパス
        output_file = os.path.join(org_output_dir, f"{repo_name}.md")

        # すでに分析済みの場合はスキップ
        if os.path.exists(output_file):
            print(f"スキップ: {org_name}/{repo_name} (すでに分析済み)")
            return True

        print(f"分析開始: {org_name}/{repo_name}")

        # コード行数の取得
        cloc_output = run_command("cloc .", repo_path)

        # コミット履歴の取得
        git_log = run_command("git log --pretty=format:%H,%ct", repo_path)

        # コミットの重み付け計算
        now = datetime.now().timestamp()
        decay = 30 * 24 * 60 * 60  # 30日を秒に変換
        total_weight = 0.0

        for line in git_log.splitlines():
            commit_hash, timestamp = line.split(',')
            timestamp = float(timestamp)
            weight = exp(-(now - timestamp) / decay)
            total_weight += weight

        # 開発者の情報を取得
        git_shortlog = run_command("git shortlog -sne", repo_path)
        developers = analyze_developers(git_shortlog)

        # 結果をMarkdownファイルに書き出し
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"# {org_name}/{repo_name}\n\n")
            f.write(f"## コード行数\n")
            f.write("```\n")
            f.write(f"{cloc_output}")
            f.write("```\n\n")
            f.write(f"## 変更頻度スコア\n")
            f.write(f"{total_weight:.8f}\n\n")
            f.write(f"## 開発者\n")
            f.write(f"```\n{git_shortlog}```\n\n")
            f.write("### 開発者ドメイン\n")
            f.write(f"```\n{developers}\n```\n")

        print(f"分析成功: {org_name}/{repo_name}")
        return True

    except Exception as e:
        print(f"分析失敗: {repo_url} - エラー: {str(e)}")
        return False

def analyze_local_repository(repo_path: str = ".", output_file: str = "analysis_result.md") -> bool:
    """
    カレントディレクトリまたは指定したディレクトリを分析する関数

    Args:
        repo_path: 分析対象のディレクトリパス（デフォルト: カレントディレクトリ）
        output_file: 出力ファイル名（デフォルト: analysis_result.md）

    Returns:
        bool: 分析が成功したかどうか
    """
    try:
        repo_path = os.path.abspath(repo_path)
        repo_name = os.path.basename(repo_path)

        print(f"分析開始: {repo_path}")

        # コード行数の取得
        cloc_output = run_command("cloc .", repo_path)

        # コミット履歴の取得
        git_log = run_command("git log --pretty=format:%H,%ct", repo_path)

        # コミットの重み付け計算
        now = datetime.now().timestamp()
        decay = 30 * 24 * 60 * 60  # 30日を秒に変換
        total_weight = 0.0

        for line in git_log.splitlines():
            if not line.strip():
                continue
            commit_hash, timestamp = line.split(',')
            timestamp = float(timestamp)
            weight = exp(-(now - timestamp) / decay)
            total_weight += weight

        # 開発者の情報を取得
        git_shortlog = run_command("git shortlog -sne", repo_path)
        developers = analyze_developers(git_shortlog)

        # 結果をMarkdownファイルに書き出し
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"# {repo_name}\n\n")
            f.write(f"## コード行数\n")
            f.write("```\n")
            f.write(f"{cloc_output}")
            f.write("```\n\n")
            f.write(f"## 変更頻度スコア\n")
            f.write(f"{total_weight:.8f}\n\n")
            f.write(f"## 開発者\n")
            f.write(f"```\n{git_shortlog}```\n\n")
            f.write("### 開発者ドメイン\n")
            f.write(f"```\n{developers}\n```\n")

        print(f"分析成功: {repo_path}")
        print(f"結果を {output_file} に出力しました")
        return True

    except Exception as e:
        print(f"分析失敗: {repo_path} - エラー: {str(e)}")
        return False

def main():
    # コマンドライン引数の確認
    if len(sys.argv) < 2:
        print("使用方法:")
        print("  CSVからの分析: python repo_analyzer.py <CSVファイルのパス>")
        print("  カレントディレクトリの分析: python repo_analyzer.py --local [出力ファイル名]")
        sys.exit(1)

    # ローカル分析モード
    if sys.argv[1] == "--local":
        output_file = sys.argv[2] if len(sys.argv) > 2 else "analysis_result.md"
        analyze_local_repository(".", output_file)
        sys.exit(0)

    csv_path = sys.argv[1]
    base_dir = "repos"
    output_base_dir = "analysis_results"

    # 出力ディレクトリの作成
    Path(output_base_dir).mkdir(exist_ok=True)

    try:
        # CSVファイルの読み込み（repourlのみ）
        df = pd.read_csv(csv_path, names=['repourl'])

        # 分析結果の集計
        total = len(df)
        success = 0
        failed = 0
        skipped = 0

        # 各リポジトリの分析
        for _, row in df.iterrows():
            success_flag = analyze_repository(row['repourl'], base_dir, output_base_dir)
            if success_flag:
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