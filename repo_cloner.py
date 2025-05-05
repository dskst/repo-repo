import os
import sys
import pandas as pd
from git import Repo
from pathlib import Path
from repo_utils import extract_repo_info

def clone_repository(repo_url: str, base_dir: str) -> tuple[bool, str, str]:
    """
    リポジトリをクローンする関数
    
    Args:
        repo_url: リポジトリのURL
        base_dir: クローン先のベースディレクトリ
    
    Returns:
        tuple[bool, str, str]: (成功したかどうか, 組織名, リポジトリ名)
    """
    try:
        # URLから組織名とリポジトリ名を抽出
        org_name, repo_name = extract_repo_info(repo_url)
        
        # 組織ごとのディレクトリを作成
        org_dir = os.path.join(base_dir, org_name)
        Path(org_dir).mkdir(exist_ok=True)
        
        # クローン先のパス
        target_dir = os.path.join(org_dir, repo_name)
        
        # すでにクローン済みの場合はスキップ
        if os.path.exists(target_dir):
            print(f"スキップ: {org_name}/{repo_name} (すでにクローン済み)")
            return True, org_name, repo_name
            
        print(f"クローン開始: {org_name}/{repo_name}")
        Repo.clone_from(repo_url, target_dir)
        print(f"クローン成功: {org_name}/{repo_name}")
        return True, org_name, repo_name
    except Exception as e:
        print(f"クローン失敗: {repo_url} - エラー: {str(e)}")
        return False, "", ""

def main():
    # コマンドライン引数の確認
    if len(sys.argv) != 2:
        print("使用方法: python repo_cloner.py <CSVファイルのパス>")
        sys.exit(1)

    csv_path = sys.argv[1]
    base_dir = "repos"

    # ベースディレクトリの作成
    Path(base_dir).mkdir(exist_ok=True)

    try:
        # CSVファイルの読み込み（repourlのみ）
        df = pd.read_csv(csv_path, names=['repourl'])
        
        # クローン結果の集計
        total = len(df)
        success = 0
        failed = 0
        skipped = 0

        # 各リポジトリのクローン
        for _, row in df.iterrows():
            success_flag, org_name, repo_name = clone_repository(row['repourl'], base_dir)
            if success_flag:
                if org_name and repo_name:
                    success += 1
                else:
                    skipped += 1
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