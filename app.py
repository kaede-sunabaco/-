"""たまごの巣立ち - Flaskの最小構成。

現段階では全ページを表示・移動できることを優先しています。
会員登録、ログイン、検索、チャットなどの本格的な処理は後から追加します。
"""

from pathlib import Path

from flask import Flask, render_template, send_from_directory


app = Flask(__name__)


# TOPページ
@app.get("/")
@app.get("/tamago-top-page/index.html")
def index():
    return render_template("index.html")


# ログイン・新規登録
@app.get("/login")
@app.get("/login.html")
def login():
    return render_template("login.html")


@app.get("/register")
@app.get("/register.html")
def register():
    return render_template("register.html")


# 制作者検索・プロフィール
@app.get("/creators")
@app.get("/creators.html")
def creators():
    return render_template("creators.html")


@app.get("/creator-detail")
@app.get("/creator-detail.html")
def creator_detail():
    return render_template("creator-detail.html")


# マイページ・チャット・相談依頼・ステータス
@app.get("/mypage")
@app.get("/mypage.html")
def mypage():
    return render_template("mypage.html")


@app.get("/chat")
@app.get("/chat.html")
def chat():
    return render_template("chat.html")


@app.get("/request")
@app.get("/request.html")
def request_page():
    return render_template("request.html")


@app.get("/status")
@app.get("/status.html")
def status():
    return render_template("status.html")


# 静的HTML時代のCSSパスも使えるようにする互換ルートです。
# 全ページをurl_for()へ変更したら削除できます。
@app.get("/css/<path:filename>")
def legacy_page_css(filename):
    css_directory = Path(app.static_folder) / "css"
    return send_from_directory(css_directory, filename)


@app.get("/style.css")
def legacy_top_css():
    css_directory = Path(app.static_folder) / "css"
    return send_from_directory(css_directory, "top.css")


if __name__ == "__main__":
    app.run(debug=True)
