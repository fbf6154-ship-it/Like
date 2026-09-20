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
    return "Ultra-Stable 7-Bot All-Media Reaction System is Live 24/7!"

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

# সব ধরনের পোস্ট ফরম্যাট (লেখা, ছবি, ভিডিও, স্টিকার ইত্যাদি)
ALL_MEDIA_TYPES = [
    'text', 'photo', 'video', 'document', 'audio', 'voice',
    'sticker', 'animation', 'poll', 'video_note', 'contact',
    'location', 'venue', 'dice'
]

# সক্রিয় বটগুলোর লিস্ট তৈরি
active_bots = []
for token in BOT_TOKENS:
    if token and "আপনার_" not in token:
        try:
            active_bots.append(telebot.TeleBot(token))
        except Exception as e:
            print(f"Token Load Error: {e}")

if not active_bots:
    print("কোনো ভ্যালিড বট টোকেন পাওয়া যায়নি!")
    exit(1)

main_listener = active_bots[0]

def generate_natural_reactions():
    """বাস্তবসম্মত বিভিন্ন উল্টাপাল্টা/র‍্যান্ডম প্যাটার্ন তৈরি করার ফাংশন"""
    emojis = TARGET_EMOJIS.copy()
    random.shuffle(emojis)

    # বাস্তবসম্মত কম্বিনেশন
    possible_patterns = [
        [1, 1, 1, 1, 1, 1, 1],  # ৭টিই আলাদা
        [2, 1, 1, 1, 1, 1],     # একটিতে ২টি, বাকিগুলো ১টি
        [3, 1, 1, 1, 1],        # একটিতে ৩টি, বাকিগুলো ১টি
        [2, 2, 1, 1, 1],        # দুইটিতে ২টি করে, বাকিগুলো ১টি
        [3, 2, 1, 1],           # একটিতে ৩টি, একটিতে ২টি, বাকি ২টি ১টি
        [2, 2, 2, 1]            # তিনটিতে ২টি করে, বাকি একটি ১টি
    ]

    chosen_pattern = random.choice(possible_patterns)
    reaction_plan = []
    
    for count, emoji in zip(chosen_pattern, emojis):
        reaction_plan.extend([emoji] * count)

    random.shuffle(reaction_plan)
    return reaction_plan

def execute_smart_reactions(chat_id, message_id):
    reaction_plan = generate_natural_reactions()
    print(f"Reaction Plan for post {message_id}: {reaction_plan}")

    # ৭টি বট ক্রমান্বয়ে ঠিক ১ সেকেন্ড বিরতিতে রিঅ্যাক্ট দেবে
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
            
            # ঠিক ১ সেকেন্ড গ্যাপ
            time.sleep(1.0)
            
        except Exception as e:
            print(f"Bot {index + 1} Error: {e}")

# সব ধরনের কন্টেন্টে রিঅ্যাক্ট ট্রিগার
@main_listener.channel_post_handler(content_types=ALL_MEDIA_TYPES)
def auto_react_all_media(message):
    print(f"New post detected! Type: {message.content_type} (ID: {message.message_id})")
    Thread(target=execute_smart_reactions, args=(message.chat.id, message.message_id)).start()

if __name__ == '__main__':
    keep_alive()
    print("Initializing Multi-Bot System...")
    
    # Error 409 Conflict দূর করার জন্য আগের পেন্ডিং রিকোয়েস্ট ক্লিয়ার
    try:
        main_listener.remove_webhook(drop_pending_updates=True)
    except Exception:
        pass
    
    time.sleep(1.5)  # পূর্বের সেশন ক্লোজ হওয়ার জন্য সংক্ষিপ্ত বিরতি
    
    print("Bot is successfully running and waiting for channel posts...")
    main_listener.infinity_polling(skip_pending=True, timeout=20)
