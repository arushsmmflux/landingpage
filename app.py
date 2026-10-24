
from flask import Flask, render_template_string
from urllib.parse import urlparse

app = Flask(__name__)

# ==========================================
# EDIT YOUR PAGE HERE
# ==========================================

TITLE = "𝘼𝘿𝙐𝙇𝙏 𝙑𝙄𝘿𝙀𝙊𝙎 😍"
USERNAME = "@adultvid12k_bot"

DESCRIPTION = (
    "𝗦𝗧𝗔𝗥𝗧 𝗕𝗢𝗧 𝗔𝗡𝗗 𝗪𝗔𝗧𝗖𝗛 𝗙𝗥𝗘𝗘 𝗗𝗘𝗠𝗢 ❤️\n"
    "100% 𝗧𝗥𝗨𝗦𝗧𝗘𝗗 𝗕𝗢𝗧 🔥"
)

# Colours
BG_COLOR = "#000000"
TEXT_COLOR = "#ffffff"
BUTTON_COLOR = "#229ED9"
BUTTON_TEXT_COLOR = "#ffffff"

# Paste Imgbb DIRECT image URLs here
BACKGROUND_IMAGE = "https://ibb.co/tT69L0hD"
PROFILE_IMAGE = "https://ibb.co/Zb15CT"

# Telegram button
TELEGRAM_URL = "https://t.me/adultvid12k_bot"

FOOTER = "Powered by Telegram"


# ==========================================
# PAGE DESIGN
# ==========================================

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

* {
    box-sizing: border-box;
}

html {
    min-height: 100%;
}

body {
    margin: 0;
    min-height: 100vh;
    min-height: 100dvh;
    padding: 22px 15px;
    display: flex;
    align-items: flex-start;
    justify-content: center;
    font-family: Arial, Helvetica, sans-serif;
    background-color: var(--bg);
    {% if background_image %}
    background-image: url("{{ background_image }}");
    background-size: cover;
    background-position: center center;
    background-repeat: no-repeat;
    background-attachment: fixed;
    {% endif %}
    color: var(--text);
}

.card {
    width: 100%;
    max-width: 410px;
    margin-top: 5vh;
    padding: 28px 22px;
    border: 1px solid #ffffff25;
    border-radius: 24px;
    text-align: center;
    background: #101820d9;
    overflow-wrap: anywhere;
}

.profile {
    width: 108px;
    height: 108px;
    display: block;
    object-fit: cover;
    border-radius: 50%;
    margin: 0 auto 17px;
    border: 3px solid var(--button);
    background: #222;
}

h1 {
    font-size: clamp(24px, 6vw, 31px);
    margin: 8px 0;
}

.username {
    opacity: .8;
    margin-bottom: 18px;
}

.description {
    white-space: pre-line;
    overflow-wrap: anywhere;
    line-height: 1.8;
    margin: 0 0 24px;
    font-size: 15px;
}

.btn {
    display: flex;
    justify-content: center;
    align-items: center;
    width: 100%;
    min-height: 50px;
    padding: 14px 16px;
    margin-top: 12px;
    border-radius: 13px;
    background: var(--button);
    color: var(--button-text);
    text-decoration: none;
    font-size: 16px;
    font-weight: bold;
}

.btn:hover {
    filter: brightness(1.1);
}

.footer {
    margin-top: 23px;
    font-size: 12px;
    opacity: .7;
}

@media (max-width: 360px) {
    .card {
        padding: 23px 16px;
    }

    .profile {
        width: 90px;
        height: 90px;
    }
}
</style>
</head>

<body>
<main class="card">

    {% if profile_image %}
    <img class="profile" src="{{ profile_image }}" alt="Profile picture">
    {% else %}
    <div class="profile" style="display:grid;place-items:center;font-size:38px">✦</div>
    {% endif %}

    <h1>{{ title }}</h1>
    <div class="username">{{ username }}</div>
    <p class="description">{{ description }}</p>

    <a class="btn" href="{{ telegram_url }}"
       target="_blank" rel="noopener noreferrer">
        ✈️ OPEN TELEGRAM
    </a>

    <div class="footer">{{ footer }}</div>

</main>
</body>
</html>
"""


def valid_https_url(value):
    try:
        parsed = urlparse(value)
        return parsed.scheme == "https" and bool(parsed.hostname)
    except Exception:
        return False


def safe_image(value):
    if value and valid_https_url(value):
        return value
    return ""


def safe_telegram_url(value):
    if value and valid_https_url(value):
        host = (urlparse(value).hostname or "").lower()
        if host in ("t.me", "www.t.me", "telegram.me", "www.telegram.me"):
            return value
    return "https://t.me/"


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
        background_image=safe_image(BACKGROUND_IMAGE),
        profile_image=safe_image(PROFILE_IMAGE),
        telegram_url=safe_telegram_url(TELEGRAM_URL),
        footer=FOOTER,
    )


@app.route("/health")
def health():
    return {"ok": True}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
