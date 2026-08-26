import os
import telebot
import sys

TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID_THC = os.getenv('CHAT_ID_THC')
bot = telebot.TeleBot(TOKEN)

def find_specific_video(target_name):
    target_name = target_name.lower()
    for root, dirs, files in os.walk("."):
        for file in files:
            if file.lower().endswith(".mp4") and target_name in file.lower():
                return os.path.join(root, file)
    return None

def main():
    target = sys.argv[1] if len(sys.argv) > 1 else ""
    video_path = find_specific_video(target)
    
    if not video_path:
        print(f"ERROR: No MP4 found for '{target}'")
        return

    try:
        with open(video_path, 'rb') as video:
            bot.send_video(CHAT_ID, video, caption=f" ")
            # bot.send_video(CHAT_ID, video, caption=f"Testing: {target}")
        print(f"SUCCESS: {target} sent!")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
