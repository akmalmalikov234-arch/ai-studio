import os
import sqlite3
import secrets
from datetime import datetime, timedelta
from functools import wraps

from flask import (
    Flask, request, redirect, url_for, session,
    render_template_string, flash
)

app = Flask(__name__)

app.secret_key = os.environ.get(
    "SECRET_KEY",
    "change-this-secret-key"
)

DB = "ai_studio.db"

# FAQAT SIZNING EMAIL INGIZNI RENDER ENVIRONMENT'DA BERASIZ
ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL", "").lower().strip()


# =========================
# DATABASE
# =========================

def db():
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    return con


def init_db():
    con = db()

    con.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            plan TEXT DEFAULT 'free',
            videos INTEGER DEFAULT 0,
            images INTEGER DEFAULT 0,
            blocked INTEGER DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    con.execute("""
        CREATE TABLE IF NOT EXISTS plans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            price TEXT DEFAULT '0',
            videos INTEGER DEFAULT 0,
            images INTEGER DEFAULT 0,
            days INTEGER DEFAULT 30,
            active INTEGER DEFAULT 1
        )
    """)

    con.execute("""
        CREATE TABLE IF NOT EXISTS receipts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            text TEXT NOT NULL,
            status TEXT DEFAULT 'pending',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    con.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    """)

    defaults = [
        ("app_name", "AI STUDIO"),
        ("payment_card", ""),
        ("welcome_text", "Professional AI Studio"),
    ]

    for key, value in defaults:
        con.execute(
            "INSERT OR IGNORE INTO settings(key,value) VALUES(?,?)",
            (key, value)
        )

    plans = [
        ("small", "Kichik", "0", 5, 10, 4),
        ("medium", "O‘rta", "0", 30, 60, 30),
        ("large", "Katta", "0", 100, 200, 30),
    ]

    for plan in plans:
        con.execute("""
            INSERT OR IGNORE INTO
            plans(code,name,price,videos,images,days)
            VALUES(?,?,?,?,?,?)
        """, plan)

    con.commit()
    con.close()


init_db()


# =========================
# HELPERS
# =========================

def get_user():
    uid = session.get("user_id")

    if not uid:
        return None

    con = db()
    user = con.execute(
        "SELECT * FROM users WHERE id=?",
        (uid,)
    ).fetchone()
    con.close()

    return user


def admin_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):

        user = get_user()

        if not user:
            return redirect(url_for("login"))

        # ADMIN FAQAT EMAIL ORQALI SERVER TOMONIDA TEKSHIRILADI
        if not ADMIN_EMAIL:
            return "ADMIN_EMAIL Render Environment'da sozlanmagan.", 403

        if user["email"].lower() != ADMIN_EMAIL:
            return "403 — Admin huquqi yo‘q.", 403

        if user["blocked"]:
            return "Account blocked.", 403

        return func(*args, **kwargs)

    return wrapper


# =========================
# DESIGN
# =========================

CSS = """
<style>
*{
    box-sizing:border-box;
}

body{
    margin:0;
    font-family:Inter,Arial,sans-serif;
    background:
      radial-gradient(circle at 20% 10%,#33206b 0,transparent 35%),
      radial-gradient(circle at 90% 20%,#075985 0,transparent 30%),
      #070711;
    color:white;
    min-height:100vh;
}

nav{
    display:flex;
    justify-content:space-between;
    align-items:center;
    padding:18px 6%;
    border-bottom:1px solid rgba(255,255,255,.1);
    backdrop-filter:blur(20px);
}

.logo{
    font-size:25px;
    font-weight:900;
}

.logo span{
    color:#8b5cf6;
}

.container{
    width:min(1150px,92%);
    margin:40px auto;
}

.hero{
    text-align:center;
    padding:70px 20px;
}

.hero h1{
    font-size:clamp(42px,8vw,82px);
    margin:0;
    background:linear-gradient(90deg,#fff,#a78bfa,#38bdf8);
    -webkit-background-clip:text;
    color:transparent;
}

.hero p{
    color:#aaa;
    font-size:18px;
}

.grid{
    display:grid;
    grid-template-columns:repeat(auto-fit,minmax(230px,1fr));
    gap:20px;
}

.card{
    background:rgba(255,255,255,.07);
    border:1px solid rgba(255,255,255,.1);
    border-radius:25px;
    padding:25px;
    backdrop-filter:blur(20px);
    box-shadow:0 20px 60px rgba(0,0,0,.25);
}

.card h2{
    margin-top:0;
}

button,.btn{
    border:0;
    border-radius:14px;
    padding:13px 20px;
    background:linear-gradient(90deg,#7c3aed,#2563eb);
    color:white;
    font-weight:800;
    cursor:pointer;
    text-decoration:none;
    display:inline-block;
}

input,textarea,select{
    width:100%;
    padding:14px;
    margin:8px 0 15px;
    border-radius:13px;
    border:1px solid #333;
    background:#11111c;
    color:white;
}

table{
    width:100%;
    border-collapse:collapse;
}

td,th{
    padding:13px;
    border-bottom:1px solid rgba(255,255,255,.1);
    text-align:left;
}

.badge{
    padding:5px 10px;
    border-radius:20px;
    background:#312e81;
}

.danger{
    color:#fb7185;
}

.success{
    color:#4ade80;
}

@media(max-width:600px){
    nav{
        padding:15px;
    }

    .container{
        width:94%;
        margin:20px auto;
    }

    .hero{
        padding:45px 10px;
    }
}
</style>
"""


# =========================
# HOME
# =========================

@app.route("/")
def home():

    return render_template_string(
        CSS + """
        <nav>
            <div class="logo">AI <span>STUDIO</span></div>
            <a class="btn" href="/login">Kirish</a>
        </nav>

        <div class="hero container">
            <h1>AI STUDIO</h1>
            <p>
                Chat. Image. Video. Everything in one professional AI platform.
            </p>

            <br>

            <a class="btn" href="/login">
                Boshlash →
            </a>
        </div>

        <div class="container grid">

            <div class="card">
                <h2>🤖 AI Chat</h2>
                <p>AI bilan suhbatlashish.</p>
            </div>

            <div class="card">
                <h2>🖼️ AI Image</h2>
                <p>Prompt asosida rasm yaratish.</p>
            </div>

            <div class="card">
                <h2>🎬 AI Video</h2>
                <p>Prompt asosida video yaratish.</p>
            </div>

            <div class="card">
                <h2>👑 Admin</h2>
                <p>Platformani egasi boshqaradi.</p>
            </div>

        </div>
        """
    )


# =========================
# LOGIN
# =========================

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()

        if not name or not email:
            flash("Ism va email kerak.")
            return redirect(url_for("login"))

        con = db()

        user = con.execute(
            "SELECT * FROM users WHERE email=?",
            (email,)
        ).fetchone()

        if not user:

            con.execute("""
                INSERT INTO users(name,email)
                VALUES(?,?)
            """, (name, email))

            con.commit()

            user = con.execute(
                "SELECT * FROM users WHERE email=?",
                (email,)
            ).fetchone()

        con.close()

        if user["blocked"]:
            return "Sizning profilingiz bloklangan.", 403

        session["user_id"] = user["id"]

        return redirect(url_for("dashboard"))

    return render_template_string(
        CSS + """
        <div class="container" style="max-width:500px">

            <div class="card">

                <h1>AI STUDIO</h1>

                <p>Kirish</p>

                <form method="POST">

                    <input
                        name="name"
                        placeholder="Ismingiz"
                        required
                    >

                    <input
                        name="email"
                        type="email"
                        placeholder="Email"
                        required
                    >

                    <button type="submit">
                        Kirish
                    </button>

                </form>

            </div>

        </div>
        """
    )


# =========================
# LOGOUT
# =========================

@app.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("home"))


# =========================
# DASHBOARD
# =========================

@app.route("/dashboard")
def dashboard():

    user = get_user()

    if not user:
        return redirect(url_for("login"))

    con = db()

    plans = con.execute(
        "SELECT * FROM plans WHERE active=1"
    ).fetchall()

    con.close()

    return render_template_string(
        CSS + """
        <nav>
            <div class="logo">AI <span>STUDIO</span></div>

            <div>
                {{user["name"]}}
                |
                <a href="/logout">Chiqish</a>
            </div>
        </nav>

        <div class="container">

            <h1>Salom, {{user["name"]}} 👋</h1>

            <div class="grid">

                <div class="card">
                    <h2>🤖 AI Chat</h2>
                    <p>Savollarga AI javob beradi.</p>
                    <a class="btn" href="/chat">Ochish</a>
                </div>

                <div class="card">
                    <h2>🖼️ AI Image</h2>
                    <p>Rasm yaratish.</p>
                    <a class="btn" href="/image">Ochish</a>
                </div>

                <div class="card">
                    <h2>🎬 AI Video</h2>
                    <p>Video yaratish.</p>
                    <a class="btn" href="/video">Ochish</a>
                </div>

                <div class="card">
                    <h2>💳 Obuna</h2>
                    <p>O‘zingizga mos tarifni tanlang.</p>
                    <a class="btn" href="/plans">Ko‘rish</a>
                </div>

                <div class="card">
                    <h2>🧾 Chek</h2>
                    <p>To‘lov chekini yuborish.</p>
                    <a class="btn" href="/receipt">Yuborish</a>
                </div>

            </div>

        </div>
        """,
        user=user,
        plans=plans
    )


# =========================
# PLANS
# =========================

@app.route("/plans")
def plans():

    user = get_user()

    if not user:
        return redirect(url_for("login"))

    con = db()
    plans = con.execute(
        "SELECT * FROM plans WHERE active=1"
    ).fetchall()
    con.close()

    return render_template_string(
        CSS + """
        <div class="container">

            <h1>💎 Obunalar</h1>

            <div class="grid">

            {% for p in plans %}

                <div class="card">

                    <h2>{{p["name"]}}</h2>

                    <h1>{{p["price"]}}</h1>

                    <p>🎬 {{p["videos"]}} video</p>
                    <p>🖼️ {{p["images"]}} rasm</p>
                    <p>📅 {{p["days"]}} kun</p>

                    <a class="btn"
                       href="/receipt?plan={{p['code']}}">
                       Obuna olish
                    </a>

                </div>

            {% endfor %}

            </div>

        </div>
        """,
        plans=plans
    )


# =========================
# RECEIPT
# =========================

@app.route("/receipt", methods=["GET", "POST"])
def receipt():

    user = get_user()

    if not user:
        return redirect(url_for("login"))

    con = db()

    card = con.execute(
        "SELECT value FROM settings WHERE key='payment_card'"
    ).fetchone()

    card_number = card["value"] if card else ""

    if request.method == "POST":

        text = request.form.get("receipt", "").strip()

        if not text:
            con.close()
            return "Chek ma'lumotini kiriting.", 400

        con.execute("""
            INSERT INTO receipts(user_id,text)
            VALUES(?,?)
        """, (user["id"], text))

        con.commit()
        con.close()

        return "Chek yuborildi. Admin tekshiradi."

    con.close()

    return render_template_string(
        CSS + """
        <div class="container">

            <div class="card">

                <h1>🧾 To‘lov</h1>

                <p>Karta:</p>

                <h2>{{card}}</h2>

                <form method="POST">

                    <textarea
                        name="receipt"
                        rows="6"
                        placeholder="Chek ma'lumotini shu yerga yuboring..."
                        required></textarea>

                    <button>
                        Chek yuborish
                    </button>

                </form>

            </div>

        </div>
        """,
        card=card_number
    )


# =========================
# CHAT
# =========================

@app.route("/chat", methods=["GET", "POST"])
def chat():

    user = get_user()

    if not user:
        return redirect(url_for("login"))

    answer = None

    if request.method == "POST":

        question = request.form.get("question", "").strip()

        # Bu joyga keyinchalik haqiqiy AI model provider ulanadi.
        answer = (
            "AI engine hali ulanmagan. "
            "Bu joy ataylab soxta javob bermaydi."
        )

    return render_template_string(
        CSS + """
        <div class="container">

            <div class="card">

                <h1>🤖 AI CHAT</h1>

                <form method="POST">

                    <textarea
                        name="question"
                        rows="6"
                        placeholder="Savolingiz..."
                        required></textarea>

                    <button>
                        Yuborish
                    </button>

                </form>

                {% if answer %}

                <div class="card">
                    {{answer}}
                </div>

                {% endif %}

            </div>

        </div>
        """,
        answer=answer
    )


# =========================
# IMAGE
# =========================

@app.route("/image")
def image():

    user = get_user()

    if not user:
        return redirect(url_for("login"))

    return render_template_string(
        CSS + """
        <div class="container">

            <div class="card">

                <h1>🖼️ AI IMAGE</h1>

                <form>

                    <textarea
                        rows="6"
                        placeholder="Rasm uchun prompt..."></textarea>

                    <button>
                        Rasm yaratish
                    </button>

                </form>

                <p class="danger">
                    AI image engine hali ulanmagan.
                </p>

            </div>

        </div>
        """
    )


# =========================
# VIDEO
# =========================

@app.route("/video")
def video():

    user = get_user()

    if not user:
        return redirect(url_for("login"))

    return render_template_string(
        CSS + """
        <div class="container">

            <div class="card">

                <h1>🎬 AI VIDEO</h1>

                <form>

                    <textarea
                        rows="6"
                        placeholder="Video prompt..."></textarea>

                    <button>
                        Video yaratish
                    </button>

                </form>

                <p class="danger">
                    AI video engine hali ulanmagan.
                </p>

            </div>

        </div>
        """
    )


# =========================
# ADMIN PANEL
# =========================

@app.route("/admin")
@admin_required
def admin():

    con = db()

    users = con.execute(
        "SELECT * FROM users ORDER BY id DESC"
    ).fetchall()

    receipts = con.execute("""
        SELECT receipts.*, users.name, users.email
        FROM receipts
        JOIN users ON users.id = receipts.user_id
        ORDER BY receipts.id DESC
    """).fetchall()

    plans = con.execute(
        "SELECT * FROM plans"
    ).fetchall()

    settings = con.execute(
        "SELECT * FROM settings"
    ).fetchall()

    con.close()

    return render_template_string(
        CSS + """
        <nav>
            <div class="logo">AI <span>ADMIN</span></div>
            <a href="/dashboard">User panel</a>
        </nav>

        <div class="container">

            <h1>👑 Admin Panel</h1>

            <div class="grid">

                <div class="card">
                    <h2>👥 Users</h2>
                    <h1>{{users|length}}</h1>
                </div>

                <div class="card">
                    <h2>🧾 Receipts</h2>
                    <h1>{{receipts|length}}</h1>
                </div>

                <div class="card">
                    <h2>💎 Plans</h2>
                    <h1>{{plans|length}}</h1>
                </div>

            </div>

            <br>

            <div class="card">

                <h2>👥 Foydalanuvchilar</h2>

                <table>

                    <tr>
                        <th>ID</th>
                        <th>Ism</th>
                        <th>Email</th>
                        <th>Plan</th>
                        <th>Video</th>
                        <th>Status</th>
                    </tr>

                    {% for u in users %}

                    <tr>

                        <td>{{u["id"]}}</td>
                        <td>{{u["name"]}}</td>
                        <td>{{u["email"]}}</td>
                        <td>{{u["plan"]}}</td>
                        <td>{{u["videos"]}}</td>

                        <td>
                            {% if u["blocked"] %}
                                <span class="danger">BLOCKED</span>
                            {% else %}
                                <span class="success">ACTIVE</span>
                            {% endif %}
                        </td>

                    </tr>

                    {% endfor %}

                </table>

            </div>

            <br>

            <div class="card">

                <h2>🧾 Cheklar</h2>

                {% for r in receipts %}

                    <p>
                        <b>{{r["name"]}}</b>
                        — {{r["email"]}}
                    </p>

                    <p>{{r["text"]}}</p>

                    <hr>

                {% endfor %}

            </div>

            <br>

            <div class="card">

                <h2>💎 Obunalar</h2>

                {% for p in plans %}

                    <p>
                        <b>{{p["name"]}}</b>
                        —
                        {{p["price"]}}
                        —
                        {{p["videos"]}} video
                        —
                        {{p["images"]}} rasm
                    </p>

                {% endfor %}

            </div>

            <br>

            <div class="card">

                <h2>⚙️ Sozlamalar</h2>

                <p>
                    Karta raqami va boshqa sozlamalar
                    serverdagi admin konfiguratsiyasi orqali
                    boshqariladi.
                </p>

            </div>

        </div>
        """,
        users=users,
        receipts=receipts,
        plans=plans,
        settings=settings
    )


# =========================
# HEALTH CHECK
# =========================

@app.route("/health")
def health():

    return {
        "status": "ok",
        "app": "AI STUDIO"
    }


# =========================
# RENDER PORT
# =========================

if __name__ == "__main__":

    port = int(os.environ.get("PORT", 10000))

    app.run(
        host="0.0.0.0",
        port=port,
        debug=False
    )
