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
    return "All-Media 7-Bot Random Reaction System is Active 24/7!"

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

# সব ধরনের মিডিয়া ফরম্যাটের লিস্ট (টেক্সট, ছবি, স্টিকার, ভিডিও ইত্যাদি)
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
            print(f"Token Error: {e}")

if not active_bots:
    print("কোনো ভ্যালিড বট টোকেন পাওয়া যায়নি!")
    exit(1)

main_listener = active_bots[0]

def generate_natural_reactions():
    """বাস্তবসম্মত বিভিন্ন উল্টাপাল্টা/র‍্যান্ডম প্যাটার্ন তৈরি করার ফাংশন"""
    emojis = TARGET_EMOJIS.copy()
    random.shuffle(emojis)

    possible_patterns = [
        [1, 1, 1, 1, 1, 1, 1],  # ৭টিই আলাদা
        [2, 1, 1, 1, 1, 1],     # একটিতে ২টি, বাকিগুলো ১টি করে
        [3, 1, 1, 1, 1],        # একটিতে ৩টি, বাকিগুলো ১টি করে
        [2, 2, 1, 1, 1],        # দুইটিতে ২টি করে, বাকিগুলো ১টি করে
        [3, 2, 1, 1],           # একটিতে ৩টি, একটিতে ২টি, বাকিগুলো ১টি করে
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

    # ৭টি বট ১ সেকেন্ড পরপর রিঅ্যাক্ট প্রদান করবে
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

# এখানে সব ধরনের কন্টেন্ট টাইপ (All Content Types) অ্যাড করা হলো
@main_listener.channel_post_handler(content_types=ALL_MEDIA_TYPES)
def auto_react_all_media(message):
    print(f"New post detected! Type: {message.content_type} (ID: {message.message_id})")
    # সাথে সাথে ব্যাকগ্রাউন্ড থ্রেডে রিঅ্যাক্ট শুরু হবে
    Thread(target=execute_smart_reactions, args=(message.chat.id, message.message_id)).start()

if __name__ == '__main__':
    keep_alive()
    print("All-Media Reaction Bot System is Live...")
    main_listener.infinity_polling()
