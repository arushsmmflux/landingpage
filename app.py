from flask import Flask, render_template_string, jsonify, abort
import re

app = Flask(__name__)

# ==========================================
# EDITABLE SETTINGS (Change your config here)
# ==========================================
PAGE_TITLE = "Arush Bot"
USERNAME = "@arushdev"
DESCRIPTION = "𝗦𝗧𝗔𝗥𝗧 𝗕𝗢𝗧 𝗔𝗡𝗗 𝗪𝗔𝗧𝗖𝗛 𝗙𝗥𝗘𝗘 𝗗𝗘𝗠𝗢 ❤️\n100% 𝗧𝗥𝗨𝗦𝗧𝗘𝗗 𝗕𝗢𝗧 🔥"

# Colors
BG_COLOR = "#000000"
TEXT_COLOR = "#ffffff"
BUTTON_COLOR = "#229ED9"
BUTTON_TEXT_COLOR = "#ffffff"

# Images (IMPORTANT: Replace these with your actual Imgbb DIRECT image URLs ending in .jpg/.png)
# How to get: Open https://ibb.co/Zb15CT or https://ibb.co/tT69L0hD, right-click the image, 
# and select "Copy image address". Paste the direct link inside the quotes below.
PROFILE_PIC_URL = "https://i.ibb.co/placeholder-profile.jpg"  # <-- Paste direct profile image URL here
BACKGROUND_IMAGE_URL = "https://i.ibb.co/placeholder-bg.jpg"   # <-- Paste direct background image URL here

# Telegram Destination
TELEGRAM_BOT_URL = "https://t.me/arushdev"  # Must be a valid https://t.me/... link

# Footer Text
FOOTER_TEXT = "Powered by Telegram"


def is_valid_telegram_url(url):
    """Validates that the URL is a secure, official Telegram link."""
    pattern = r"^https://t\.me/[a-zA-Z0-9_]{5,}$"
    return bool(re.match(pattern, url))


# HTML Template embedded cleanly inside app.py
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ page_title }}</title>
    <style>
        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }
        body {
            background-color: {{ bg_color }};
            color: {{ text_color }};
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            background-image: url('{{ bg_image_url }}');
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            padding: 20px;
        }
        .container {
            width: 100%;
            max-width: 420px;
            background: rgba(0, 0, 0, 0.45);
            backdrop-filter: blur(8px);
            -webkit-backdrop-filter: blur(8px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 24px;
            padding: 35px 25px;
            text-align: center;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
            margin-top: -40px; /* Positioned slightly above vertical center */
        }
        .profile-container {
            width: 110px;
            height: 110px;
            margin: 0 auto 20px auto;
            border-radius: 50%;
            overflow: hidden;
            border: 3px solid rgba(255, 255, 255, 0.8);
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
        }
        .profile-pic {
            width: 100%;
            height: 100%;
            object-fit: cover;
        }
        h1 {
            font-size: 24px;
            font-weight: 700;
            margin-bottom: 5px;
        }
        .username {
            font-size: 15px;
            opacity: 0.8;
            margin-bottom: 20px;
            font-weight: 500;
        }
        .description {
            font-size: 15px;
            line-height: 1.5;
            white-space: pre-line;
            margin-bottom: 30px;
            opacity: 0.95;
            padding: 0 10px;
        }
        .btn {
            display: block;
            width: 100%;
            background-color: {{ button_color }};
            color: {{ button_text_color }};
            text-decoration: none;
            padding: 15px 20px;
            font-size: 16px;
            font-weight: 600;
            border-radius: 14px;
            text-align: center;
            transition: transform 0.2s ease, opacity 0.2s ease;
            box-shadow: 0 4px 12px rgba(34, 158, 217, 0.4);
        }
        .btn:hover {
            opacity: 0.9;
            transform: translateY(-2px);
        }
        .btn:active {
            transform: translateY(0);
        }
        footer {
            margin-top: 25px;
            font-size: 13px;
            opacity: 0.6;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="profile-container">
            <img src="{{ profile_pic_url }}" alt="{{ page_title }} Profile Picture" class="profile-pic">
        </div>
        <h1>{{ page_title }}</h1>
        <div class="username">{{ username }}</div>
        <div class="description">{{ description }}</div>
        <a href="{{ telegram_bot_url }}" class="btn" target="_blank" rel="noopener noreferrer">START BOT</a>
        <footer>{{ footer_text }}</footer>
    </div>
</body>
</html>
"""


@app.route("/")
def index():
    if not is_valid_telegram_url(TELEGRAM_BOT_URL):
        abort(400, description="Invalid Telegram destination configuration.")
    
    return render_template_string(
        HTML_TEMPLATE,
        page_title=PAGE_TITLE,
        username=USERNAME,
        description=DESCRIPTION,
        bg_color=BG_COLOR,
        text_color=TEXT_COLOR,
        button_color=BUTTON_COLOR,
        button_text_color=BUTTON_TEXT_COLOR,
        profile_pic_url=PROFILE_PIC_URL,
        bg_image_url=BACKGROUND_IMAGE_URL,
        telegram_bot_url=TELEGRAM_BOT_URL,
        footer_text=FOOTER_TEXT
    )


@app.route("/health")
def health():
    return jsonify({"status": "healthy", "service": "telegram-landing-page"})


if __name__ == "__main__":
    app.run(debug=True)
