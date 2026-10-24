import json
import os
import subprocess
import sys

import telebot

TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')

if not TOKEN or not CHAT_ID:
    sys.exit("FATAL: TELEGRAM_TOKEN / CHAT_ID tak diset")

bot = telebot.TeleBot(TOKEN)
MAX_BYTES = 50 * 1024 * 1024

def find_specific_video(target_name):
    target_name = target_name.lower()
    hits = []
    for root, dirs, files in os.walk("."):
        dirs[:] = [d for d in dirs if not d.startswith(".")]
        for file in files:
            if file.lower().endswith(".mp4") and target_name in file.lower():
                hits.append(os.path.join(root, file))
    return sorted(hits)

def video_info(path):
    try:
        out = subprocess.check_output(
            ["ffprobe", "-v", "error", "-select_streams", "v:0",
             "-show_entries", "stream=width,height:format=duration",
             "-of", "json", path], text=True)
        d = json.loads(out)
        s = d["streams"][0]
        return int(s["width"]), int(s["height"]), int(float(d["format"]["duration"]))
    except Exception as e:
        print(f"WARN: ffprobe gagal ({e}), hantar tanpa dimensi")
        return None, None, None

def main():
    target = sys.argv[1].strip() if len(sys.argv) > 1 else ""
    if not target:
        sys.exit("FATAL: beri nama poster, cth: python bot2.py POSTER_A")

    hits = find_specific_video(target)
    if len(hits) != 1:
        sys.exit(f"FATAL: '{target}' padan {len(hits)} fail: {hits}")

    video_path = hits[0]
    size = os.path.getsize(video_path)
    if size > MAX_BYTES:
        sys.exit(f"FATAL: {video_path} {size/1e6:.1f}MB, melebihi had 50MB")

    w, h, dur = video_info(video_path)
    print(f"INFO: {video_path} {w}x{h} {dur}s {size/1e6:.1f}MB")
    try:
        with open(video_path, 'rb') as video:
            bot.send_video(CHAT_ID, video, width=w, height=h, duration=dur,
                           supports_streaming=True, timeout=120)
        print(f"SUCCESS: {video_path} ({size/1e6:.1f}MB) sent")
    except Exception as e:
        sys.exit(f"FATAL: {type(e).__name__}: {e}")

if __name__ == "__main__":
    main()
