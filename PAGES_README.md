# 画面ファイルの確認方法

## 現在の構成

- `app.py`：Flaskを起動し、各ページを表示する中心ファイル
- `templates/`：TOPを含む9ページ
- `static/css/common.css`：ヘッダー、フッター、ボタン、フォームなどの共通CSS
- `static/css/style.css`：検索、プロフィール、チャットなどのページ固有CSS
- `static/css/top.css`：既存TOPページのCSS
- `static/images/`、`static/icons/`：画像素材

## 最初に確認するページ

`FLASK_README.md` の手順でFlaskを起動し、ブラウザで `http://127.0.0.1:5000` を開きます。

## 今は動かないもの

フォーム送信、ログイン、検索、チャット送信などは見た目だけです。Flaskへ組み込む段階で機能を追加します。

## TOPページについて

既存TOPの見た目を引き継ぎ、ナビゲーションから各ページへ移動できるようにしています。
デザインや文章を修正するときは `templates/index.html` と `static/css/top.css` を編集します。

元の `tamago-top-page/` は比較用に残しています。Flaskで表示される正本は `templates/index.html` です。
