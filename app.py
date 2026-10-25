import os, json, uuid, re
from urllib.parse import urlparse
from flask import Flask, request, render_template_string, redirect, abort, send_from_directory, jsonify
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 8 * 1024 * 1024
ADMIN_KEY = os.getenv('ADMIN_KEY', '')
DATA_FILE = '/tmp/telegram_landing_data.json'
UPLOAD_FOLDER = '/tmp/telegram_landing_uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

DEFAULTS = {
    'bot_name': os.getenv('BOT_NAME', 'My Telegram Bot'),
    'bot_username': os.getenv('BOT_USERNAME', '@your_bot'),
    'redirect_url': os.getenv('TELEGRAM_URL', 'https://t.me/your_bot'),
    'sub_text_1': os.getenv('SUB_TEXT_1', 'START THE BOT AND EXPLORE THE DEMO ❤️'),
    'sub_text_2': os.getenv('SUB_TEXT_2', '100% TRUSTED BOT 🔥'),
    'profile_pic': os.getenv('PROFILE_IMAGE_URL', ''),
    'background_url': os.getenv('BACKGROUND_IMAGE_URL', ''),
    'button_color': os.getenv('BUTTON_COLOR', '#0ea5e9'),
}

def load_data():
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data if isinstance(data, dict) else {}
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return {}

def save_data(data):
    tmp = DATA_FILE + '.tmp'
    with open(tmp, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    os.replace(tmp, DATA_FILE)

def valid_telegram_url(value):
    try:
        p = urlparse((value or '').strip())
        return p.scheme == 'https' and p.netloc.lower() in {'t.me', 'www.t.me', 'telegram.me', 'www.telegram.me'} and bool(p.path.strip('/'))
    except Exception:
        return False

def safe_slug(value):
    value = (value or '').strip().lower()
    value = re.sub(r'[^a-z0-9_-]+', '-', value)
    return re.sub(r'-{2,}', '-', value).strip('-')[:48]

def authorized():
    return bool(ADMIN_KEY) and (request.args.get('admin', '') == ADMIN_KEY or request.form.get('admin', '') == ADMIN_KEY)

LANDING_HTML = r'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{{ data.bot_name }}</title><style>
*{box-sizing:border-box}body{margin:0;min-height:100vh;padding:22px;display:flex;align-items:center;justify-content:center;color:#fff;font-family:system-ui,-apple-system,Segoe UI,sans-serif;background:#050505;{% if data.background_url %}background-image:url("{{ data.background_url }}");background-size:cover;background-position:center;background-repeat:no-repeat;{% endif %}}body:before{content:"";position:fixed;inset:0;background:#0003;pointer-events:none}.card{position:relative;width:min(100%,390px);margin-top:-4vh;text-align:center;padding:32px 22px;border-radius:22px;background:rgba(10,10,10,.9);border:1px solid #ffffff25;box-shadow:0 20px 60px #0008}.avatar{width:100px;height:100px;margin:0 auto 18px;border-radius:50%;overflow:hidden;display:grid;place-items:center;background:#202020;border:3px solid #ffffff35}.avatar img{width:100%;height:100%;object-fit:cover}h1{margin:0 0 6px;font-size:25px;overflow-wrap:anywhere}.username{color:#cbd5e1;margin-bottom:24px}.description,.trust{line-height:1.5;overflow-wrap:anywhere}.description{margin:0 0 10px}.trust{margin:0 0 26px}.start{display:block;width:100%;padding:15px 18px;border-radius:12px;background:{{ data.button_color|tojson }};color:white;text-decoration:none;font-weight:800;letter-spacing:.6px}.footer{margin-top:20px;color:#94a3b8;font-size:12px}
</style></head><body><main class="card"><div class="avatar">{% if data.profile_pic %}<img src="{{ data.profile_pic }}" alt="Profile image">{% else %}<span>🤖</span>{% endif %}</div><h1>{{ data.bot_name }}</h1><div class="username">{{ data.bot_username }}</div><p class="description">{{ data.sub_text_1 }}</p><p class="trust">{{ data.sub_text_2 }}</p><a class="start" href="{{ data.redirect_url }}" target="_blank" rel="noopener noreferrer">START BOT</a><div class="footer">Powered by Telegram</div></main></body></html>'''

ADMIN_HTML = r'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Admin panel</title><style>
*{box-sizing:border-box}body{margin:0;background:#080d18;color:#f8fafc;font-family:system-ui,sans-serif;padding:20px}.wrap{max-width:850px;margin:auto}.box{background:#111c2e;padding:20px;border:1px solid #ffffff18;border-radius:14px;margin:16px 0}input{display:block;width:100%;padding:12px;margin:7px 0 14px;border:1px solid #334155;border-radius:7px;background:#0b1220;color:white}label{font-size:14px;color:#cbd5e1}button,.btn{display:inline-block;padding:11px 14px;border:0;border-radius:7px;background:#0284c7;color:white;text-decoration:none;font-weight:700;cursor:pointer}.danger{background:#b91c1c}.muted{color:#94a3b8;font-size:13px}table{width:100%;border-collapse:collapse}th,td{text-align:left;padding:10px;border-bottom:1px solid #334155;overflow-wrap:anywhere}a{color:#38bdf8}.actions{display:flex;gap:8px;flex-wrap:wrap}
</style></head><body><div class="wrap"><h1>Telegram Landing Admin</h1><p class="muted">Vercel /tmp storage is temporary; use persistent storage for reliable saved links.</p>
{% if not is_auth %}<div class="box"><h2>Admin login</h2><form method="get"><label>Admin key</label><input type="password" name="admin" required><button>Open admin panel</button></form></div>{% else %}
<div class="box"><h2>{{ 'Edit link' if edit_slug else 'Create a link' }}</h2><form method="post" enctype="multipart/form-data"><input type="hidden" name="admin" value="{{ admin_key }}"><input type="hidden" name="old_slug" value="{{ edit_slug or '' }}"><label>Slug</label><input name="slug" required value="{{ edit_slug or '' }}" placeholder="my-bot"><label>Bot name</label><input name="bot_name" required value="{{ current.bot_name }}"><label>Bot username</label><input name="bot_username" value="{{ current.bot_username }}"><label>Telegram URL (https://t.me/your_bot)</label><input type="url" name="redirect_url" required value="{{ current.redirect_url }}"><label>Description line 1</label><input name="sub_text_1" value="{{ current.sub_text_1 }}"><label>Description line 2</label><input name="sub_text_2" value="{{ current.sub_text_2 }}"><label>Profile image URL (optional)</label><input type="url" name="profile_pic" value="{{ current.profile_pic if current.profile_pic and not current.profile_pic.startswith('/uploads/') else '' }}"><label>Or upload profile image (max 8 MB)</label><input type="file" name="profile_file" accept="image/*"><label>Background image URL (optional)</label><input type="url" name="background_url" value="{{ current.background_url }}"><label>Button color hex</label><input name="button_color" value="{{ current.button_color }}"><div class="actions"><button>Save link</button><a class="btn" href="/?admin={{ admin_key }}">Clear form</a></div></form></div>
<div class="box"><h2>Saved links</h2>{% if bots %}<table><tr><th>Slug</th><th>Bot</th><th>Actions</th></tr>{% for slug,item in bots.items() %}<tr><td><a href="/{{ slug }}" target="_blank">/{{ slug }}</a></td><td>{{ item.bot_name }}</td><td><div class="actions"><a class="btn" href="/?admin={{ admin_key }}&edit={{ slug }}">Edit</a><form method="post" onsubmit="return confirm('Delete this link?')"><input type="hidden" name="admin" value="{{ admin_key }}"><input type="hidden" name="action" value="delete"><input type="hidden" name="slug" value="{{ slug }}"><button class="danger">Delete</button></form></div></td></tr>{% endfor %}</table>{% else %}<p>No links saved yet.</p>{% endif %}</div>{% endif %}</div></body></html>'''

@app.get('/health')
def health():
    return jsonify(status='ok'), 200

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'GET' and not request.args.get('admin'):
        return render_template_string(LANDING_HTML, data=DEFAULTS)
    if not ADMIN_KEY:
        return 'Admin panel disabled: set ADMIN_KEY in Vercel Environment Variables.', 503
    is_auth = authorized()
    if not is_auth:
        return render_template_string(ADMIN_HTML, is_auth=False, admin_key='', bots={}, edit_slug=None, current=DEFAULTS)
    bots = load_data()
    if request.method == 'POST':
        slug = safe_slug(request.form.get('slug', ''))
        if request.form.get('action') == 'delete':
            old = bots.pop(slug, None)
            if old and old.get('profile_pic', '').startswith('/uploads/'):
                try: os.remove(os.path.join(UPLOAD_FOLDER, os.path.basename(old['profile_pic'])))
                except OSError: pass
            save_data(bots)
            return redirect('/?admin=' + ADMIN_KEY)
        if not slug:
            return 'Please enter a valid slug.', 400
        redirect_url = request.form.get('redirect_url', '').strip()
        if not valid_telegram_url(redirect_url):
            return 'Telegram URL must be a valid https://t.me/... URL.', 400
        old_slug = safe_slug(request.form.get('old_slug', ''))
        if slug in bots and slug != old_slug:
            return 'That slug is already in use. Choose another.', 400
        profile_pic = request.form.get('profile_pic', '').strip()
        if not profile_pic and old_slug in bots:
