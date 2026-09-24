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
    return "Universal Channel & Group 7-Bot Reaction System is Live 24/7!"

def run_web():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    Thread(target=run_web).start()

# --- আপনার দেওয়া ৭টি বটের টোকেন সরাসরি যুক্ত করা হয়েছে ---
BOT_TOKENS = [
    "8913713708:AAFOQ-G40SAELmLXcetXTSKtLs44wsO6YqY",
    "8095265015:AAE3MXODkX2x3WMLV3hDOrPFUaQiPwDr6Xs",
    "8710440598:AAHrTG58EKcwn-bmzBE2AujP12c04OWcIrk",
    "8556244521:AAH5yB2xP1lwnEGBtepFYIeipMq4nmBQ9I4",
    "8849045895:AAHuZREx1u4zRtY-1QKxHzi1bGmIK7OcbcE",
    "8924590959:AAHMwPLAyeWAZQwLH0iwR6MqIJ3hf24k6QM",
    "8888167810:AAFsObbkPLGWFb3YQ44cHrL6YwmhcEC0R60"
]

# আপনার দেওয়া নির্দিষ্ট ৭টি ইমোজি
TARGET_EMOJIS = ["❤️", "👍", "🔥", "👏", "🎉", "😍", "⚡"]

# সব ধরনের কন্টেন্ট টাইপ (লেখা, ছবি, স্টিকার, ভিডিও ইত্যাদি)
ALL_MEDIA_TYPES = [
    'text', 'photo', 'video', 'document', 'audio', 'voice',
    'sticker', 'animation', 'poll', 'video_note', 'contact',
    'location', 'venue', 'dice'
]

# সক্রিয় বটগুলোর লিস্ট তৈরি
active_bots = []
for token in BOT_TOKENS:
    if token.strip():
        try:
            active_bots.append(telebot.TeleBot(token.strip()))
        except Exception as e:
            print(f"Token Load Error: {e}")

if not active_bots:
    print("কোনো ভ্যালিড বট টোকেন পাওয়া যায়নি!")
    exit(1)

main_listener = active_bots[0]

def generate_natural_reactions():
    """ন্যাচারাল র‍্যান্ডম প্যাটার্ন তৈরি করার ফাংশন"""
    emojis = TARGET_EMOJIS.copy()
    random.shuffle(emojis)

    possible_patterns = [
        [1, 1, 1, 1, 1, 1, 1],  # ৭টিই আলাদা আলাদা
        [2, 1, 1, 1, 1, 1],     # একটিতে ২টি, বাকিগুলো ১টি করে
        [3, 1, 1, 1, 1],        # একটিতে ৩টি, বাকিগুলো ১টি করে
        [2, 2, 1, 1, 1],        # দুইটিতে ২টি করে, বাকিগুলো ১টি করে
        [3, 2, 1, 1],           # একটিতে ৩টি, একটিতে ২টি, বাকি ২টি ১টি করে
        [2, 2, 2, 1]            # তিনটিতে ২টি করে, বাকি একটি ১টি
    ]

    chosen_pattern = random.choice(possible_patterns)
    reaction_plan = []
    
    for count, emoji in zip(chosen_pattern, emojis):
        reaction_plan.extend([emoji] * count)

    random.shuffle(reaction_plan)
    return reaction_plan

def execute_smart_reactions(chat_id, message_id, chat_type):
    reaction_plan = generate_natural_reactions()
    print(f"Reacting to [{chat_type}] | Message ID: {message_id} | Plan: {reaction_plan}")

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

# ১. যেকোনো চ্যানেলের পোস্টে রিঅ্যাক্ট দেওয়ার হ্যান্ডলার
@main_listener.channel_post_handler(content_types=ALL_MEDIA_TYPES)
def handle_all_channels(message):
    print(f"New Channel Post detected! (Channel: {message.chat.title})")
    Thread(target=execute_smart_reactions, args=(message.chat.id, message.message_id, "Channel")).start()

# ২. যেকোনো গ্রুপের মেসেজে রিঅ্যাক্ট দেওয়ার হ্যান্ডলার
@main_listener.message_handler(content_types=ALL_MEDIA_TYPES, func=lambda m: m.chat.type in ['group', 'supergroup'])
def handle_all_groups(message):
    print(f"New Group Message detected! (Group: {message.chat.title})")
    Thread(target=execute_smart_reactions, args=(message.chat.id, message.message_id, "Group")).start()

if __name__ == '__main__':
    keep_alive()
    print("Universal Multi-Bot Reaction System Initializing...")
    
    # Error 409 Conflict দূর করার ব্যবস্থা
    try:
        main_listener.remove_webhook(drop_pending_updates=True)
    except Exception:
        pass
    
    time.sleep(1.5)
    print("Bot is successfully running for ALL Channels and Groups!")
    main_listener.infinity_polling(skip_pending=True, timeout=20)
