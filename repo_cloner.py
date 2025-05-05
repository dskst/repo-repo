import os
import sys
import pandas as pd
from git import Repo
from pathlib import Path

def clone_repository(repo_name: str, repo_url: str, base_dir: str) -> bool:
    """
    リポジトリをクローンする関数
    
    Args:
        repo_name: リポジトリ名
        repo_url: リポジトリのURL
        base_dir: クローン先のベースディレクトリ
    
    Returns:
        bool: クローンが成功したかどうか
    """
    try:
        target_dir = os.path.join(base_dir, repo_name)
        
        # すでにクローン済みの場合はスキップ
        if os.path.exists(target_dir):
            print(f"スキップ: {repo_name} (すでにクローン済み)")
            return True
            
        print(f"クローン開始: {repo_name}")
        Repo.clone_from(repo_url, target_dir)
        print(f"クローン成功: {repo_name}")
        return True
    except Exception as e:
        print(f"クローン失敗: {repo_name} - エラー: {str(e)}")
        return False

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
        # CSVファイルの読み込み
        df = pd.read_csv(csv_path, names=['reponame', 'repourl'])
        
        # クローン結果の集計
        total = len(df)
        success = 0
        failed = 0
        skipped = 0

        # 各リポジトリのクローン
        for _, row in df.iterrows():
            target_dir = os.path.join(base_dir, row['reponame'])
            if os.path.exists(target_dir):
                skipped += 1
                continue
                
            if clone_repository(row['reponame'], row['repourl'], base_dir):
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