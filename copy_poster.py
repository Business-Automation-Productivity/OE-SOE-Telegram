import json
import os
import sys

import telebot

TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')                  # destinasi
SOURCE_CHAT_ID = os.getenv('SOURCE_CHAT_ID')    # tempat poster asal (Hub Test)

if not TOKEN or not CHAT_ID or not SOURCE_CHAT_ID:
    sys.exit("FATAL: TELEGRAM_TOKEN / CHAT_ID / SOURCE_CHAT_ID tak diset")

bot = telebot.TeleBot(TOKEN)

def list_posts():
    ups = bot.get_updates(timeout=1, allowed_updates=["channel_post"])
    if not ups:
        print("Tiada channel_post dalam 24 jam. Hantar/forward mesej ke Hub Test semula, kemudian run lagi.")
        return
    for u in ups:
        m = u.channel_post
        kind = "video" if m.video else m.content_type
        dur = m.video.duration if m.video else "-"
        print(f"chat={m.chat.id} message_id={m.message_id} jenis={kind} tempoh={dur}s")

def main():
    target = sys.argv[1].strip().upper() if len(sys.argv) > 1 else ""
    if target == "LIST":
        list_posts()
        return
    with open("posters.json") as f:
        posters = json.load(f)
    if target not in posters:
        sys.exit(f"FATAL: '{target}' tiada dalam posters.json: {list(posters)}")
    msg_id = int(posters[target])
    if msg_id <= 0:
        sys.exit(f"FATAL: message_id untuk {target} belum diisi")
    try:
        r = bot.copy_message(CHAT_ID, SOURCE_CHAT_ID, msg_id)
        print(f"SUCCESS: {target} (mesej {msg_id}) disalin ke chat ...{str(CHAT_ID)[-4:]}, mesej baru {r.message_id}")
    except Exception as e:
        sys.exit(f"FATAL: {type(e).__name__}: {e}")

if __name__ == "__main__":
    main()
