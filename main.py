import os
import time
import random
import telebot
from telebot.types import ReactionTypeEmoji
from flask import Flask
from threading import Thread

# --- Render ও UptimeRobot-এর জন্য ওয়েব সার্ভার ---
app = Flask(__name__)

@app.route('/')
def home():
    return "Randomized Multi-React Bot is running 24/7!"

def run_web():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    Thread(target=run_web).start()

# --- আপনার বটের টোকেন লিস্ট ---
BOT_TOKENS = [
    os.environ.get('BOT_TOKEN_1', 'আপনার_১ম_টোকেন'),
    os.environ.get('BOT_TOKEN_2', 'আপনার_২য়_টোকেন'),
    os.environ.get('BOT_TOKEN_3', 'আপনার_৩য়_টোকেন'),
    os.environ.get('BOT_TOKEN_4', 'আপনার_৪র্থ_টোকেন'),
    os.environ.get('BOT_TOKEN_5', 'আপনার_৫ম_টোকেন'),
    os.environ.get('BOT_TOKEN_6', 'আপনার_৬ষ্ঠ_টোকেন'),
    os.environ.get('BOT_TOKEN_7', 'আপনার_৭ম_টোকেন'),
]

# যে যে ইমোজিগুলো দিয়ে রিঅ্যাক্ট করাতে চান
EMOJI_POOL = ["👍", "❤️", "🔥", "🎉", "👏", "😍", "🤩", "⭐", "🥰"]

# সক্রিয় বটগুলোর তালিকা তৈরি
active_bots = []
for token in BOT_TOKENS:
    if token and "আপনার_" not in token:
        try:
            active_bots.append(telebot.TeleBot(token))
        except Exception as e:
            print(f"Error loading bot: {e}")

if not active_bots:
    print("কোনো ভ্যালিড টোকেন পাওয়া যায়নি!")
    exit(1)

main_listener = active_bots[0]

def react_worker(chat_id, message_id):
    # কতগুলো বট এই পোস্টে রিঅ্যাক্ট দেবে তা র‍্যান্ডমলি ঠিক করা (৩ থেকে মোট বট সংখ্যা পর্যন্ত)
    min_bots = min(2, len(active_bots))
    num_bots_to_react = random.randint(min_bots, len(active_bots))
    
    # র‍্যান্ডমলি বটগুলোকে বাছাই করা
    selected_bots = random.sample(active_bots, num_bots_to_react)
    
    for b in selected_bots:
        try:
            # মানুষের মতো ন্যাচারাল দেখানোর জন্য ১ থেকে ৩ সেকেন্ড বিরতি
            time.sleep(random.uniform(0.8, 2.5))
            
            # র‍্যান্ডম একটি ইমোজি নির্বাচন (এতে একাধিক বট একই ইমোজি দিতে পারবে)
            chosen_emoji = random.choice(EMOJI_POOL)
            
            b.set_message_reaction(
                chat_id=chat_id,
                message_id=message_id,
                reaction=[ReactionTypeEmoji(emoji=chosen_emoji)],
                is_big=False
            )
        except Exception as e:
            print(f"Reaction error: {e}")

@main_listener.channel_post_handler(func=lambda message: True)
def auto_react_handler(message):
    print(f"New post in channel: {message.chat.id}")
    # মূল লুপ যাতে আটকে না যায় তাই ব্যাকগ্রাউন্ড থ্রেডে রিঅ্যাক্ট পাঠানো
    Thread(target=react_worker, args=(message.chat.id, message.message_id)).start()

if __name__ == '__main__':
    keep_alive()
    print("Realistic Natural Multi-Bot started...")
    main_listener.infinity_polling()
