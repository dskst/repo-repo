# GitHubリポジトリクローナー

このプログラムは、CSVファイルに記載されたGitHubリポジトリを一括でクローンし、解析するためのツールです。

## 必要条件

- Python 3.8以上
- pip
- cloc (コード行数カウントツール)

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

3. clocのインストール
```bash
# macOSの場合
brew install cloc

# Ubuntu/Debianの場合
sudo apt-get install cloc

# Windowsの場合
choco install cloc
```

## 使用方法

### リポジトリのクローン

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

### リポジトリの解析

1. CSVファイルからクローンしたリポジトリの解析
```bash
python repo_analyzer.py <CSVファイルのパス>
```

2. カレントディレクトリの解析
```bash
# デフォルトの出力ファイル名（analysis_result.md）で解析
python repo_analyzer.py --local

# 出力ファイル名を指定
python repo_analyzer.py --local <出力ファイル名>
```

## 出力

### クローン時の出力

- クローン開始時：`クローン開始: <リポジトリ名>`
- クローン成功時：`クローン成功: <リポジトリ名>`
- クローン失敗時：`クローン失敗: <リポジトリ名> - エラー: <エラーメッセージ>`
- 処理完了時：合計、成功、失敗したリポジトリ数の集計結果

### 解析時の出力

- 解析結果は `analysis_results` ディレクトリに保存されます
- 各リポジトリごとに `<リポジトリ名>.md` ファイルが作成されます
- 解析結果には以下の情報が含まれます：
  - コード行数（clocの出力）
  - 開発者情報（git shortlogの出力）

## 注意事項

- クローンしたリポジトリは `repos` ディレクトリに保存されます
- クローンに失敗したリポジトリはスキップされ、次のリポジトリの処理に進みます
- 既に存在するリポジトリは上書きされません
- 解析結果は `analysis_results` ディレクトリに保存されます 