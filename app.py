
from flask import Flask, redirect, render_template_string
from urllib.parse import urlparse

app = Flask(__name__)

# ==================================================
# EDIT YOUR PAGE HERE
# ==================================================

TITLE = "𝘼𝘿𝙐𝙇𝙏 𝙑𝙄𝘿𝙀𝙊𝙎 😍"
USERNAME = "@adultvid12k_bot"
DESCRIPTION = (
    "𝗦𝗧𝗔𝗥𝗧 𝗕𝗢𝗧 𝗔𝗡𝗗 𝗪𝗔𝗧𝗖𝗛 𝗙𝗥𝗘𝗘 𝗗𝗘𝗠𝗢 ❤️\n"
    "100% 𝗧𝗥𝗨𝗦𝗧𝗘𝗗 𝗕𝗢𝗧 🔥"
)

# Colours: "#000000" = black, "#ffffff" = white
BG_COLOR = "#000000"
TEXT_COLOR = "#ffffff"
BUTTON_COLOR = "#229ED9"
BUTTON_TEXT_COLOR = "#ffffff"

# Imgbb: use the DIRECT image URL, usually ending in .jpg/.png/.webp
PROFILE_IMAGE = "https://ibb.co/Zb15CT
BACKGROUND_IMAGE = "https://ibb.co/tT69L0hD"

TELEGRAM_URL = "https://t.me/adultvid12k_bot"
DOWNLOAD_URL = "https://example.com/download"

# Optional: change to a different heading or footer
FOOTER = "Powered by Telegram"


def valid_url(url, allowed_hosts=None):
    try:
        parsed = urlparse(url)
        if parsed.scheme != "https" or not parsed.hostname:
            return False
        if allowed_hosts and parsed.hostname.lower() not in allowed_hosts:
            return False
        return True
    except Exception:
        return False


def safe_image(url):
    if not url or not valid_url(url):
        return ""
    host = urlparse(url).hostname.lower()
    if host == "ibb.co" or host.endswith(".ibb.co"):
        return url
    return url


def safe_link(url):
    return url if valid_url(url) else "https://t.me/"


PAGE = """
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="theme-color" content="{{ bg_color }}">
<title>{{ title }}</title>
<style>
:root {
  --bg: {{ bg_color }};
  --text: {{ text_color }};
  --button: {{ button_color }};
  --button-text: {{ button_text_color }};
}
* { box-sizing: border-box; }
html { min-height: 100%; }
body {
  margin: 0;
  min-height: 100vh;
  min-height: 100dvh;
  padding: 24px 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  color: var(--text);
  background-color: var(--bg);
  {% if background_image %}
  background-image: linear-gradient(#0006, #0008), url("{{ background_image }}");
  background-size: cover;
  background-position: center;
  background-attachment: fixed;
  {% endif %}
}
.card {
  width: 100%;
  max-width: 400px;
  padding: 28px 22px;
  text-align: center;
  border: 1px solid #ffffff25;
  border-radius: 24px;
  background: color-mix(in srgb, var(--bg) 78%, transparent);
  backdrop-filter: blur(12px);
  overflow-wrap: anywhere;
}
.avatar {
  display: block;
  width: 104px;
  height: 104px;
  margin: 0 auto 16px;
  border-radius: 50%;
  object-fit: cover;
  border: 3px solid var(--button);
  background: #27313a;
}
h1 { font-size: clamp(23px, 6vw, 30px); margin: 8px 0; }
.username { opacity: .8; margin-bottom: 16px; }
.description { line-height: 1.65; margin: 0 0 22px; }
.btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  min-height: 50px;
  padding: 14px 18px;
  margin-top: 12px;
  border-radius: 13px;
  background: var(--button);
  color: var(--button-text);
  font-size: 16px;
  font-weight: 700;
  text-decoration: none;
  transition: filter .15s ease, transform .15s ease;
}
.btn:hover { filter: brightness(1.08); }
.btn:active { transform: scale(.98); }
.footer { margin-top: 22px; font-size: 12px; opacity: .7; }
@media (max-width: 360px) {
  .card { padding: 24px 16px; }
  .avatar { width: 88px; height: 88px; }
}
@media (prefers-reduced-motion: reduce) {
  .btn { transition: none; }
}
</style>
</head>
<body>
<main class="card">
  {% if profile_image %}
  <img class="avatar" src="{{ profile_image }}" alt="Profile picture">
  {% else %}
  <div class="avatar" style="display:grid;place-items:center;font-size:38px">✦</div>
  {% endif %}
  <h1>{{ title }}</h1>
  <div class="username">{{ username }}</div>
  <p class="description">{{ description }}</p>

  <a class="btn" href="{{ telegram_url }}" target="_blank" rel="noopener noreferrer">
    ✈️ Open Telegram
  </a>
  <a class="btn" href="{{ download_url }}" target="_blank" rel="noopener noreferrer">
    ⬇️ Download
  </a>

  <div class="footer">{{ footer }}</div>
</main>
</body>
</html>
"""


@app.route("/")
def home():
    return render_template_string(
        PAGE,
        title=TITLE,
        username=USERNAME,
        description=DESCRIPTION,
        bg_color=BG_COLOR,
        text_color=TEXT_COLOR,
        button_color=BUTTON_COLOR,
        button_text_color=BUTTON_TEXT_COLOR,
        profile_image=safe_image(PROFILE_IMAGE),
        background_image=safe_image(BACKGROUND_IMAGE),
        telegram_url=safe_link(TELEGRAM_URL),
        download_url=safe_link(DOWNLOAD_URL),
        footer=FOOTER,
    )


@app.route("/health")
def health():
    return {"ok": True}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
