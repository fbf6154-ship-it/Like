import os
import time
import random
import telebot
from telebot.types import ReactionTypeEmoji
from flask import Flask
from threading import Thread

# --- Render এবং UptimeRobot এর জন্য ওয়েব সার্ভার ---
app = Flask(__name__)

@app.route('/')
def home():
    return "7-Bot 1s Delay System is Running 24/7!"

def run_web():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    Thread(target=run_web).start()

# --- ৭টি বটের টোকেন লিস্ট ---
BOT_TOKENS = [
    os.environ.get('BOT_TOKEN_1', 'আপনার_১ম_টোকেন'),
    os.environ.get('BOT_TOKEN_2', 'আপনার_২য়_টোকেন'),
    os.environ.get('BOT_TOKEN_3', 'আপনার_৩য়_টোকেন'),
    os.environ.get('BOT_TOKEN_4', 'আপনার_৪র্থ_টোকেন'),
    os.environ.get('BOT_TOKEN_5', 'আপনার_৫ম_টোকেন'),
    os.environ.get('BOT_TOKEN_6', 'আপনার_৬ষ্ঠ_টোকেন'),
    os.environ.get('BOT_TOKEN_7', 'আপনার_৭ম_টোকেন'),
]

# জনপ্রিয় ইমোজির তালিকা
EMOJI_POOL = ["👍", "❤️", "🔥", "🎉", "👏", "😍", "🤩", "⭐", "🥰"]

# সক্রিয় বটগুলোর লিস্ট তৈরি
active_bots = []
for token in BOT_TOKENS:
    if token and "আপনার_" not in token:
        try:
            active_bots.append(telebot.TeleBot(token))
        except Exception as e:
            print(f"Error loading bot token: {e}")

if not active_bots:
    print("কোনো ভ্যালিড বট টোকেন পাওয়া যায়নি!")
    exit(1)

main_listener = active_bots[0]

def react_one_by_one(chat_id, message_id):
    # সব কয়টি বট ক্রমান্বয়ে রিঅ্যাক্ট দেবে
    for index, current_bot in enumerate(active_bots):
        try:
            # র‍্যান্ডমলি একটি ইমোজি নির্বাচন
            chosen_emoji = random.choice(EMOJI_POOL)
            
            # রিঅ্যাকশন প্রদান
            current_bot.set_message_reaction(
                chat_id=chat_id,
                message_id=message_id,
                reaction=[ReactionTypeEmoji(emoji=chosen_emoji)],
                is_big=False
            )
            print(f"Bot {index + 1} reacted: {chosen_emoji}")
            
            # প্রতি রিঅ্যাকশনের মাঝে ঠিক ১ সেকেন্ড বিরতি
            time.sleep(1.0)
            
        except Exception as e:
            print(f"Bot {index + 1} error: {e}")

@main_listener.channel_post_handler(func=lambda message: True)
def auto_react_handler(message):
    print(f"New post in channel (ID: {message.chat.id}). Starting reactions...")
    # ব্যাকগ্রাউন্ড থ্রেডে ১ সেকেন্ড পর পর রিঅ্যাকশন চালু করা
    Thread(target=react_one_by_one, args=(message.chat.id, message.message_id)).start()

if __name__ == '__main__':
    keep_alive()
    print("Sequential Multi-Bot React System Started...")
    main_listener.infinity_polling()
