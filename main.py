import os
import time
import random
import telebot
from telebot.types import ReactionTypeEmoji
from flask import Flask
from threading import Thread

# --- Render এবং UptimeRobot-এর জন্য ওয়েব সার্ভার ---
app = Flask(__name__)

@app.route('/')
def home():
    return "Ultra-Realistic 7-Bot Random Reaction System is Live!"

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

# আপনার দেওয়া নির্দিষ্ট ৭টি ইমোজির তালিকা
TARGET_EMOJIS = ["❤️", "👍", "🔥", "👏", "🎉", "😍", "⚡"]

# সক্রিয় বটগুলোর লিস্ট তৈরি
active_bots = []
for token in BOT_TOKENS:
    if token and "আপনার_" not in token:
        try:
            active_bots.append(telebot.TeleBot(token))
        except Exception as e:
            print(f"Token Error: {e}")

if not active_bots:
    print("কোনো ভ্যালিড বট টোকেন পাওয়া যায়নি!")
    exit(1)

main_listener = active_bots[0]

def generate_natural_reactions():
    """বাস্তবসম্মত বিভিন্ন উল্টাপাল্টা/র‍্যান্ডম প্যাটার্ন তৈরি করার ফাংশন"""
    emojis = TARGET_EMOJIS.copy()
    random.shuffle(emojis)

    # ৭টি রিঅ্যাক্টের বিভিন্ন বাস্তবসম্মত কম্বিনেশন
    possible_patterns = [
        [1, 1, 1, 1, 1, 1, 1],  # ৭টিই আলাদা আলাদা (প্রত্যেকটি ১টি করে)
        [2, 1, 1, 1, 1, 1],     # একটি ইমোজি ২টি, বাকি ৫টি ১টি করে
        [3, 1, 1, 1, 1],        # একটি ইমোজি ৩টি, বাকি ৪টি ১টি করে
        [2, 2, 1, 1, 1],        # দুইটি ইমোজি ২টি করে, বাকি ৩টি ১টি করে
        [3, 2, 1, 1],           # একটি ৩টি, একটি ২টি, বাকি ২টি ১টি করে
        [2, 2, 2, 1]            # তিনটি ইমোজি ২টি করে, বাকি একটি ১টি
    ]

    chosen_pattern = random.choice(possible_patterns)
    reaction_plan = []
    
    for count, emoji in zip(chosen_pattern, emojis):
        reaction_plan.extend([emoji] * count)

    # ক্রমান্বয়ে যাতে এলোমেলোভাবে পড়ে তার জন্য আবার শাফল করা
    random.shuffle(reaction_plan)
    return reaction_plan

def execute_smart_reactions(chat_id, message_id):
    # প্রতি পোস্টের জন্য নতুন র‍্যান্ডম প্যাটার্ন তৈরি
    reaction_plan = generate_natural_reactions()
    print(f"Post {message_id} Reaction Plan: {reaction_plan}")

    # ৭টি বট ১ সেকেন্ড বিরতিতে একটি একটি করে রিঅ্যাক্ট দেবে
    for index, current_bot in enumerate(active_bots):
        try:
            emoji_to_send = reaction_plan[index]
            
            current_bot.set_message_reaction(
                chat_id=chat_id,
                message_id=message_id,
                reaction=[ReactionTypeEmoji(emoji=emoji_to_send)],
                is_big=False
            )
            print(f"[{index + 1}/7] Reacted: {emoji_to_send}")
            
            # ঠিক ১ সেকেন্ড পর পরবর্তী বটের রিঅ্যাক্ট
            time.sleep(1.0)
            
        except Exception as e:
            print(f"Bot {index + 1} Error: {e}")

@main_listener.channel_post_handler(func=lambda message: True)
def auto_react_trigger(message):
    print(f"New post detected (ID: {message.message_id}). Starting smart reactions...")
    # সাথে সাথে রিঅ্যাকশন প্রসেস ব্যাকগ্রাউন্ডে চালু হবে
    Thread(target=execute_smart_reactions, args=(message.chat.id, message.message_id)).start()

if __name__ == '__main__':
    keep_alive()
    print("Ultra-Realistic Multi-Bot Started...")
    main_listener.infinity_polling()
