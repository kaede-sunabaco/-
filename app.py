"""たまごの巣立ち - 卒業制作向けの最小Flaskアプリ。

画面確認だけでなく、発表で一連の流れを見せられるように、SQLiteを使った
会員登録・ログイン・依頼作成・案件管理・チャット送信を実装しています。
"""

from functools import wraps
from pathlib import Path
import os
import sqlite3

from flask import (
    Flask,
    flash,
    g,
    redirect,
    render_template,
    request,
    send_from_directory,
    session,
    url_for,
)
from werkzeug.security import check_password_hash, generate_password_hash


BASE_DIR = Path(__file__).resolve().parent

# どの起動方法でも templates / static を見つけられるよう、場所を明示します。
app = Flask(
    __name__,
    template_folder=str(BASE_DIR / "templates"),
    static_folder=str(BASE_DIR / "static"),
)
app.config["SECRET_KEY"] = os.environ.get(
    "SECRET_KEY", "tamago-graduation-project-development-key"
)

DATABASE = Path(app.instance_path) / "tamago.db"
ALLOWED_STATUSES = ("相談中", "制作中", "完了", "キャンセル")
STATUS_PROGRESS = {"相談中": 20, "制作中": 60, "完了": 100, "キャンセル": 0}


def get_db():
    """リクエスト中に共用するSQLite接続を返します。"""
    if "db" not in g:
        Path(app.instance_path).mkdir(parents=True, exist_ok=True)
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


@app.teardown_appcontext
def close_db(_error=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    """必要なテーブルがなければ初回起動時に作成します。"""
    db = get_db()
    db.executescript(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL CHECK (role IN ('client', 'creator')),
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            category TEXT,
            budget TEXT,
            deadline TEXT,
            is_small_project INTEGER NOT NULL DEFAULT 0,
            status TEXT NOT NULL DEFAULT '相談中',
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            request_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            body TEXT NOT NULL,
            is_reply INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (request_id) REFERENCES requests (id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        );
        """
    )
    db.commit()


@app.before_request
def load_logged_in_user():
    user_id = session.get("user_id")
    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            "SELECT id, name, email, role FROM users WHERE id = ?", (user_id,)
        ).fetchone()


def login_required(view):
    @wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            flash("このページを利用するにはログインしてください。", "error")
            return redirect(url_for("login"))
        return view(**kwargs)

    return wrapped_view


# TOPページ
@app.get("/")
@app.get("/index.html")
@app.get("/tamago-top-page/index.html")
def index():
    return render_template("index.html")


# ログイン・新規登録
@app.route("/login", methods=("GET", "POST"))
@app.route("/login.html", methods=("GET", "POST"))
def login():
    if g.user is not None:
        return redirect(url_for("mypage"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        user = get_db().execute(
            "SELECT * FROM users WHERE email = ?", (email,)
        ).fetchone()

        if user is None or not check_password_hash(user["password_hash"], password):
            flash("メールアドレスまたはパスワードが違います。", "error")
        else:
            session.clear()
            session["user_id"] = user["id"]
            flash("ログインしました。", "success")
            return redirect(url_for("mypage"))

    return render_template("login.html")


@app.route("/register", methods=("GET", "POST"))
@app.route("/register.html", methods=("GET", "POST"))
def register():
    if request.method == "POST":
        role = request.form.get("role", "client")
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        agreement = request.form.get("agreement")
        error = None

        if role not in ("client", "creator"):
            error = "利用目的を選択してください。"
        elif not name or not email or not password:
            error = "必須項目をすべて入力してください。"
        elif len(password) < 8:
            error = "パスワードは8文字以上で入力してください。"
        elif not agreement:
            error = "利用規約への同意が必要です。"

        if error is None:
            db = get_db()
            try:
                cursor = db.execute(
                    "INSERT INTO users (name, email, password_hash, role) VALUES (?, ?, ?, ?)",
                    (name, email, generate_password_hash(password), role),
                )
                db.commit()
            except sqlite3.IntegrityError:
                error = "このメールアドレスはすでに登録されています。"
            else:
                session.clear()
                session["user_id"] = cursor.lastrowid
                flash("会員登録が完了しました。", "success")
                return redirect(url_for("mypage"))

        flash(error, "error")

    return render_template("register.html")


@app.get("/logout")
def logout():
    session.clear()
    flash("ログアウトしました。", "success")
    return redirect(url_for("login"))


# 制作者検索・プロフィール
@app.get("/creators")
@app.get("/creators.html")
def creators():
    return render_template("creators.html")


@app.get("/creator-detail")
@app.get("/creator-detail.html")
def creator_detail():
    return render_template("creator-detail.html")


# マイページ
@app.get("/mypage")
@app.get("/mypage.html")
@login_required
def mypage():
    rows = get_db().execute(
        "SELECT status, COUNT(*) AS count FROM requests WHERE user_id = ? GROUP BY status",
        (g.user["id"],),
    ).fetchall()
    counts = {status: 0 for status in ALLOWED_STATUSES}
    counts.update({row["status"]: row["count"] for row in rows})
    return render_template("mypage.html", counts=counts)


# 相談・依頼作成
@app.route("/request", methods=("GET", "POST"))
@app.route("/request.html", methods=("GET", "POST"))
@login_required
def request_page():
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        if not title or not description:
            flash("タイトルと相談・依頼内容を入力してください。", "error")
        else:
            db = get_db()
            cursor = db.execute(
                """
                INSERT INTO requests
                    (user_id, title, description, category, budget, deadline, is_small_project)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    g.user["id"],
                    title,
                    description,
                    request.form.get("category", ""),
                    request.form.get("budget", ""),
                    request.form.get("deadline", ""),
                    1 if request.form.get("is_small_project") else 0,
                ),
            )
            request_id = cursor.lastrowid
            db.execute(
                """
                INSERT INTO messages (request_id, user_id, body, is_reply)
                VALUES (?, ?, ?, 1)
                """,
                (
                    request_id,
                    g.user["id"],
                    "ご相談ありがとうございます。内容を確認し、チャットで一緒に整理していきましょう！",
                ),
            )
            db.commit()
            flash("相談・依頼を登録しました。", "success")
            return redirect(url_for("status"))

    return render_template("request.html")


# 案件ステータス管理
@app.route("/status", methods=("GET", "POST"))
@app.route("/status.html", methods=("GET", "POST"))
@login_required
def status():
    db = get_db()
    if request.method == "POST":
        request_id = request.form.get("request_id", type=int)
        new_status = request.form.get("status", "")
        if request_id and new_status in ALLOWED_STATUSES:
            db.execute(
                "UPDATE requests SET status = ? WHERE id = ? AND user_id = ?",
                (new_status, request_id, g.user["id"]),
            )
            db.commit()
            flash("案件ステータスを更新しました。", "success")
        else:
            flash("ステータスを更新できませんでした。", "error")
        return redirect(url_for("status"))

    rows = db.execute(
        "SELECT * FROM requests WHERE user_id = ? ORDER BY id DESC", (g.user["id"],)
    ).fetchall()
    projects = [
        {**dict(row), "progress": STATUS_PROGRESS.get(row["status"], 0)} for row in rows
    ]
    return render_template(
        "status.html", projects=projects, allowed_statuses=ALLOWED_STATUSES
    )


# チャット
@app.route("/chat", methods=("GET", "POST"))
@app.route("/chat.html", methods=("GET", "POST"))
@login_required
def chat():
    db = get_db()
    request_id = request.values.get("request_id", type=int)
    if request_id is None:
        latest = db.execute(
            "SELECT id FROM requests WHERE user_id = ? ORDER BY id DESC LIMIT 1",
            (g.user["id"],),
        ).fetchone()
        request_id = latest["id"] if latest else None

    project = None
    if request_id is not None:
        project = db.execute(
            "SELECT * FROM requests WHERE id = ? AND user_id = ?",
            (request_id, g.user["id"]),
        ).fetchone()

    if project is None:
        flash("先に相談・依頼を作成してください。", "error")
        return redirect(url_for("request_page"))

    if request.method == "POST":
        body = request.form.get("message", "").strip()
        if body:
            db.execute(
                "INSERT INTO messages (request_id, user_id, body) VALUES (?, ?, ?)",
                (project["id"], g.user["id"], body),
            )
            db.commit()
        else:
            flash("メッセージを入力してください。", "error")
        return redirect(url_for("chat", request_id=project["id"]))

    messages = db.execute(
        "SELECT * FROM messages WHERE request_id = ? ORDER BY id", (project["id"],)
    ).fetchall()
    return render_template("chat.html", project=project, messages=messages)


# 静的HTML時代のCSSパスも使えるようにする互換ルートです。
@app.get("/css/<path:filename>")
def legacy_page_css(filename):
    css_directory = Path(app.static_folder) / "css"
    return send_from_directory(css_directory, filename)


@app.get("/style.css")
def legacy_top_css():
    css_directory = Path(app.static_folder) / "css"
    return send_from_directory(css_directory, "top.css")


with app.app_context():
    init_db()


if __name__ == "__main__":
    app.run(debug=True)
