# GitHubリポジトリクローナー

このプログラムは、CSVファイルに記載されたGitHubリポジトリを一括でクローンするためのツールです。

## 必要条件

- Python 3.8以上
- pip

## インストール方法

1. リポジトリをクローン
```bash
git clone <repository-url>
cd <repository-directory>
```

2. 依存関係のインストール
```bash
pip install -r requirements.txt
```

## 使用方法

1. CSVファイルの準備
以下の形式でCSVファイルを作成してください：
```
reponame,repourl
example-repo,https://github.com/username/example-repo.git
```

2. プログラムの実行
```bash
python repo_cloner.py <CSVファイルのパス>
```

## 出力

- クローン開始時：`クローン開始: <リポジトリ名>`
- クローン成功時：`クローン成功: <リポジトリ名>`
- クローン失敗時：`クローン失敗: <リポジトリ名> - エラー: <エラーメッセージ>`
- 処理完了時：合計、成功、失敗したリポジトリ数の集計結果

## 注意事項

- クローンしたリポジトリは `repos` ディレクトリに保存されます
- クローンに失敗したリポジトリはスキップされ、次のリポジトリの処理に進みます
- 既に存在するリポジトリは上書きされません 