
import os
import secrets
from datetime import datetime, timezone
from functools import wraps

from flask import Flask, request, redirect, session, render_template_string, url_for
from supabase import create_client

app = Flask(__name__)
app.secret_key = os.environ["FLASK_SECRET_KEY"]

db = create_client(
    os.environ["SUPABASE_URL"],
    os.environ["SUPABASE_SERVICE_ROLE_KEY"]
)

ADMIN_ID = os.environ["ADMIN_ID"]
ADMIN_PASSWORD = os.environ["ADMIN_PASSWORD"]

DEFAULT = {
    "title": "My Telegram Bot",
    "username": "@my_bot",
    "description": "Welcome! Tap below to start.",
    "start_url": "https://t.me/",
    "pfp": "",
    "bg": "#101820",
    "accent": "#229ED9"
}

def settings():
    r = db.table("landing_settings").select("value").eq(
        "key", "main"
    ).execute()
    return {**DEFAULT, **(r.data[0]["value"] if r.data else {})}

def save_settings(s):
    db.table("landing_settings").upsert({
        "key": "main", "value": s
    }).execute()

def admin_only(fn):
    @wraps(fn)
    def wrapped(*a, **kw):
        if not session.get("admin"):
            return redirect("/admin/login")
        return fn(*a, **kw)
    return wrapped

PAGE = """
<!doctype html><html><head>
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{{s.title}}</title>
<style>
*{box-sizing:border-box}body{margin:0;min-height:100vh;
display:grid;place-items:center;padding:20px;background:{{s.bg}};
color:white;font-family:Arial,sans-serif}
.card{width:min(100%,390px);text-align:center;padding:30px 22px;
border-radius:24px;background:#ffffff0b;border:1px solid #ffffff20}
img{width:112px;height:112px;border-radius:50%;object-fit:cover;
border:3px solid #ffffff30;margin-bottom:16px}
h1{font-size:25px;margin:5px}.user{color:#aabac7;margin:10px}
.desc{white-space:pre-wrap;line-height:1.5;margin:24px 0}
.start{display:block;padding:16px;border-radius:12px;
background:{{s.accent}};color:white;text-decoration:none;font-weight:bold}
.admin{position:fixed;right:12px;bottom:12px;color:#8294a4;font-size:12px}
</style></head><body><main class="card">
{% if s.pfp %}<img src="{{s.pfp}}" alt="Profile">{% endif %}
<h1>{{s.title}}</h1><div class="user">{{s.username}}</div>
<div class="desc">{{s.description}}</div>
<a class="start" href="{{s.start_url}}" id="start">START BOT ↗</a>
</main><a class="admin" href="/admin/login">Admin</a>
<script>
document.getElementById("start").addEventListener("click",()=>{
fetch("/click",{method:"POST",keepalive:true});
});
</script></body></html>
"""

@app.get("/")
def home():
    s = settings()
    vid = request.cookies.get("visitor_id") or secrets.token_urlsafe(24)
    db.table("landing_visitors").upsert({
        "visitor_id": vid,
        "first_seen": datetime.now(timezone.utc).isoformat()
    }, on_conflict="visitor_id", ignore_duplicates=True).execute()
    from flask import make_response
    response = make_response(render_template_string(PAGE, s=s))
    if not request.cookies.get("visitor_id"):
        response.set_cookie("visitor_id", vid, max_age=31536000,
                            httponly=True, secure=True, samesite="Lax")
    return response

@app.post("/click")
def click():
    vid = request.cookies.get("visitor_id")
    if vid:
        db.table("landing_clicks").upsert({
            "visitor_id": vid,
            "clicked_at": datetime.now(timezone.utc).isoformat()
        }, on_conflict="visitor_id", ignore_duplicates=True).execute()
    return "", 204

LOGIN = """
<h2>Admin login</h2>
<form method="post">
<input name="id" placeholder="Admin ID" required>
<input name="password" type="password" placeholder="Password" required>
<button>Login</button></form>
"""

@app.route("/admin/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        if secrets.compare_digest(request.form.get("id",""), ADMIN_ID) and \
           secrets.compare_digest(request.form.get("password",""), ADMIN_PASSWORD):
            session["admin"] = True
            return redirect("/admin")
        return "Wrong ID or password", 401
    return render_template_string(LOGIN)

DASH = """
<h1>Landing Admin</h1><p>Unique visitors: {{visitors}}</p>
<p>Unique Start clicks: {{clicks}}</p>
<form method="post" action="/admin/save">
{% for k,label in fields %}
<label>{{label}}</label><br>
<input name="{{k}}" value="{{s[k]}}" style="width:95%;padding:10px"><br><br>
{% endfor %}
<label>Description</label><br>
<textarea name="description" style="width:95%;height:90px">{{s.description}}</textarea><br>
<button>Save changes</button></form>
<form method="post" action="/admin/reset"
onsubmit="return confirm('Reset all stats?')">
<button>Reset statistics</button></form>
<a href="/admin/logout">Logout</a> | <a href="/">View page</a>
"""

@app.get("/admin")
@admin_only
def dashboard():
    s = settings()
    visitors = db.table("landing_visitors").select(
        "visitor_id", count="exact"
    ).execute().count or 0
    clicks = db.table("landing_clicks").select(
        "visitor_id", count="exact"
    ).execute().count or 0
    fields = [
        ("title","Page title"), ("username","Username"),
        ("start_url","Start Bot URL"), ("pfp","Profile picture URL"),
        ("bg","Background color, e.g. #101820"),
        ("accent","Button color, e.g. #229ED9")
    ]
    return render_template_string(
        DASH, s=s, visitors=visitors, clicks=clicks, fields=fields
    )

@app.post("/admin/save")
@admin_only
def save():
    s = settings()
    for k in ("title","username","description","start_url","pfp","bg","accent"):
        s[k] = request.form.get(k, s.get(k,"")).strip()
    if not s["start_url"].startswith(("https://","http://")):
        return "Start URL must begin with https:// or http://", 400
    save_settings(s)
    return redirect("/admin")

@app.post("/admin/reset")
@admin_only
def reset():
    db.table("landing_clicks").delete().neq("visitor_id","").execute()
    db.table("landing_visitors").delete().neq("visitor_id","").execute()
    return redirect("/admin")

@app.get("/admin/logout")
def logout():
    session.clear()
    return redirect("/admin/login")

@app.get("/health")
def health():
    return {"ok": True}
