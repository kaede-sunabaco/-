# Flaskでの起動方法

## 1. 必要なライブラリを入れる

PowerShellまたはVS Codeのターミナルで、リポジトリのフォルダを開いて次を実行します。

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
py -m pip install -r requirements.txt
```

## 2. アプリを起動する

```powershell
py app.py
```

画面に表示された `http://127.0.0.1:5000` をブラウザで開きます。

## 現在できること

- TOPを含む9ページの表示
- ページ間の移動
- スマホ幅に応じた表示切り替え

## まだできないこと

- 会員登録、ログイン
- データベースへの保存
- 検索
- チャット送信
- ステータス更新

まず画面をすべて表示できる状態を作り、その後に機能を1つずつ追加します。
