
import os
import secrets
from functools import wraps
from flask import (
    Flask, request, redirect, url_for, session,
    render_template_string, make_response
)
from supabase import create_client

# =============== CONFIG ===============
SUPABASE_URL = "https://dmbgkpkkfsdfkppdawzt.supabase.co"
SUPABASE_SERVICE_ROLE_KEY = "sb_publishable_y18CGzuVHmZXfCCYOJKQkA_iwvb5TDI"
ADMIN_ID = "arushdev"
ADMIN_PASSWORD = "arush300"
FLASK_SECRET_KEY = secrets.token_hex(32)

app = Flask(__name__)
app.secret_key = FLASK_SECRET_KEY

if SUPABASE_SERVICE_ROLE_KEY == "PASTE_YOUR_SUPABASE_SECRET_KEY":
    db = None
else:
    db = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

DEFAULT_SETTINGS = {
    "title": "Arush Bot",
    "username": "@arushdev",
    "description": "Welcome! Tap below to start.",
    "start_url": "https://t.me/",
    "pfp": "",
    "bg": "#101820",
    "accent": "#229ED9",
}

PAGE = """
<!doctype html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{{ s.title }}</title>
<style>
*{box-sizing:border-box}
body{margin:0;background:{{s.bg}};color:white;font-family:Arial,sans-serif;
display:grid;place-items:center;min-height:100vh;padding:20px}
.card{width:100%;max-width:390px;text-align:center;padding:30px 22px;
border:1px solid #ffffff20;border-radius:24px;background:#ffffff0a}
.avatar{width:100px;height:100px;border-radius:50%;object-fit:cover;
background:#263746;margin-bottom:14px}
h1{margin:8px 0;font-size:27px}
.username{color:#a9c5d5;margin-bottom:18px}
p{line-height:1.6;color:#e0e8ed;overflow-wrap:anywhere}
a,.btn{display:block;width:100%;padding:15px;margin-top:12px;
border-radius:12px;border:0;background:{{s.accent}};color:white;
text-decoration:none;font-size:16px;font-weight:bold;cursor:pointer}
.small{font-size:12px;color:#91a2ae;margin-top:22px}
input,textarea{width:100%;padding:12px;margin:6px 0 14px;border-radius:8px;
border:1px solid #44515c;background:#111b24;color:white}
label{display:block;text-align:left;font-size:14px}
</style>
</head>
<body>
<div class="card">
{% if s.pfp %}<img class="avatar" src="{{s.pfp}}" alt="Profile">{% else %}
<div class="avatar" style="display:inline-grid;place-items:center;font-size:38px">✦</div>
{% endif %}
<h1>{{s.title}}</h1>
<div class="username">{{s.username}}</div>
<p>{{s.description}}</p>
<a href="/click">START BOT ↗</a>
<div class="small">Welcome</div>
</div>
</body>
</html>
"""

LOGIN_PAGE = """
<!doctype html><html><head><meta name="viewport" content="width=device-width,initial-scale=1">
<style>body{background:#101820;color:white;font-family:Arial;max-width:420px;margin:60px auto;padding:20px}
input,button{width:100%;padding:13px;margin:8px 0;box-sizing:border-box}
</style></head><body><h2>Admin Login</h2>
<form method="post">
<input name="admin_id" placeholder="Admin ID" required>
<input name="password" type="password" placeholder="Password" required>
<button>Login</button></form></body></html>
"""

ADMIN_PAGE = """
<!doctype html><html><head><meta name="viewport" content="width=device-width,initial-scale=1">
<style>
body{background:#101820;color:white;font-family:Arial;max-width:650px;margin:30px auto;padding:20px}
input,textarea{width:100%;padding:12px;margin:6px 0 14px;box-sizing:border-box}
label{display:block}button,a{padding:12px;margin:5px 5px 5px 0;display:inline-block}
input,textarea{background:#182632;color:white;border:1px solid #44515c;border-radius:7px}
</style></head><body>
<h2>Admin Panel</h2>
<p>Unique visitors: {{visitors}} | Unique clickers: {{clicks}}</p>
<form method="post" action="/admin/save">
{% for key,label in fields %}
<label>{{label}}</label>
{% if key == 'description' %}
<textarea name="{{key}}" rows="4">{{s[key]}}</textarea>
{% else %}
<input name="{{key}}" value="{{s[key]}}" {% if key in ['bg','accent'] %}type="color"{% endif %}>
{% endif %}
{% endfor %}
<button type="submit">Save Settings</button>
</form>
<p><a href="/">View Page</a><a href="/admin/logout">Logout</a></p>
</body></html>
"""

def get_settings():
    if db is None:
        return DEFAULT_SETTINGS.copy()
    try:
        result = db.table("landing_settings").select("value").eq(
            "key", "main"
        ).limit(1).execute()
        if result.data:
            return {**DEFAULT_SETTINGS, **result.data[0]["value"]}
    except Exception:
        app.logger.exception("Could not load settings")
    return DEFAULT_SETTINGS.copy()

def save_settings(settings):
    if db is None:
        return False
    db.table("landing_settings").upsert(
        {"key": "main", "value": settings}
    ).execute()
    return True

def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not session.get("is_admin"):
            return redirect(url_for("admin_login"))
        return fn(*args, **kwargs)
    return wrapper

def record_unique(table, visitor_id):
    if db is None:
        return
    try:
        db.table(table).upsert(
            {"visitor_id": visitor_id},
            on_conflict="visitor_id",
            ignore_duplicates=True
        ).execute()
    except Exception:
        app.logger.exception("Could not record visitor")

def get_count(table):
    if db is None:
        return 0
    try:
        result = db.table(table).select(
            "visitor_id", count="exact"
        ).execute()
        return result.count or 0
    except Exception:
        app.logger.exception("Could not read stats")
        return 0

@app.route("/")
def home():
    s = get_settings()
    response = make_response(render_template_string(PAGE, s=s))
    visitor_id = request.cookies.get("visitor_id")
    if not visitor_id:
        visitor_id = secrets.token_urlsafe(24)
        response.set_cookie(
            "visitor_id", visitor_id,
            max_age=60*60*24*365,
            httponly=True, samesite="Lax", secure=request.is_secure
        )
    record_unique("landing_visitors", visitor_id)
    return response

@app.route("/click")
def click():
    s = get_settings()
    visitor_id = request.cookies.get("visitor_id")
    if visitor_id:
        record_unique("landing_clicks", visitor_id)
    destination = s.get("start_url", "https://t.me/")
    if not destination.startswith(("https://t.me/", "https://telegram.me/")):
        destination = "https://t.me/"
    return redirect(destination)

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        if (
            secrets.compare_digest(request.form.get("admin_id", ""), ADMIN_ID)
            and secrets.compare_digest(request.form.get("password", ""), ADMIN_PASSWORD)
        ):
            session.clear()
            session["is_admin"] = True
            return redirect(url_for("admin"))
        return "Invalid login", 401
    return LOGIN_PAGE

@app.route("/admin")
@admin_required
def admin():
    fields = [
        ("title", "Page title"),
        ("username", "Username"),
        ("description", "Description"),
        ("start_url", "Telegram start URL"),
        ("pfp", "Public profile image URL"),
        ("bg", "Background colour"),
        ("accent", "Button colour"),
    ]
    return render_template_string(
        ADMIN_PAGE, s=get_settings(), fields=fields,
        visitors=get_count("landing_visitors"),
        clicks=get_count("landing_clicks")
    )

@app.route("/admin/save", methods=["POST"])
@admin_required
def admin_save():
    old = get_settings()
    for key in DEFAULT_SETTINGS:
        value = request.form.get(key, old[key]).strip()
        if key in ("title", "username", "description"):
            old[key] = value[:2000]
        elif key == "start_url":
            if value.startswith(("https://t.me/", "https://telegram.me/")):
                old[key] = value
        elif key == "pfp":
            if not value or value.startswith("https://"):
                old[key] = value
        elif key in ("bg", "accent"):
            if len(value) == 7 and value.startswith("#"):
                old[key] = value
    if not save_settings(old):
        return "Set the Supabase secret key in app.py first.", 503
    return redirect(url_for("admin"))

@app.route("/admin/logout")
def admin_logout():
    session.clear()
    return redirect(url_for("admin_login"))

@app.route("/health")
def health():
    return {"ok": True, "database_configured": db is not None}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "5000")))
