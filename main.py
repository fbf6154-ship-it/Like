import os
import telebot
from telebot.types import ReactionTypeEmoji
from flask import Flask
from threading import Thread

# --- Render এবং UptimeRobot এর জন্য ওয়েব সার্ভার ---
app = Flask(__name__)

@app.route('/')
def home():
    return "All 7 Reaction Bots are running 24/7!"

def run_web():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run_web)
    t.start()

# --- আপনার ৬-৭টি বটের টোকেন লিস্ট ---
# এগুলো আপনি সরাসরি Render এর Environment Variables-এও দিতে পারেন 
# অথবা নিচের কোটেশনের ভেতরেও সরাসরি টোকেন বসিয়ে দিতে পারেন:
BOT_TOKENS = [
    os.environ.get('BOT_TOKEN_1', 'আপনার_১ম_বট_টোকেন'),
    os.environ.get('BOT_TOKEN_2', 'আপনার_২য়_বট_টোকেন'),
    os.environ.get('BOT_TOKEN_3', 'আপনার_৩য়_বট_টোকেন'),
    os.environ.get('BOT_TOKEN_4', 'আপনার_৪র্থ_বট_টোকেন'),
    os.environ.get('BOT_TOKEN_5', 'আপনার_৫ম_বট_টোকেন'),
    os.environ.get('BOT_TOKEN_6', 'আপনার_৬ষ্ঠ_বট_টোকেন'),
    os.environ.get('BOT_TOKEN_7', 'আপনার_৭ম_বট_টোকেন'),
]

# বটগুলো যে যে রিঅ্যাক্টগুলো দেবে (৭টি আলাদা ইমোজি)
REACTION_EMOJIS = ["👍", "❤️", "🔥", "🎉", "👏", "😍", "🤩"]

# সক্রিয় বটগুলোর অবজেক্ট তৈরি
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

# প্রথম বট পোস্ট শুনবে (Listener)
main_listener = active_bots[0]

@main_listener.channel_post_handler(func=lambda message: True)
def auto_react_to_post(message):
    print(f"New post detected in channel: {message.chat.title} (ID: {message.chat.id})")
    
    # সব কয়টি বট একযোগে আলাদা আলাদা রিঅ্যাক্ট দেবে
    for index, current_bot in enumerate(active_bots):
        try:
            emoji = REACTION_EMOJIS[index % len(REACTION_EMOJIS)]
            current_bot.set_message_reaction(
                chat_id=message.chat.id,
                message_id=message.message_id,
                reaction=[ReactionTypeEmoji(emoji=emoji)],
                is_big=False
            )
            print(f"Bot {index + 1} reacted with: {emoji}")
        except Exception as e:
            print(f"Bot {index + 1} failed: {e}")

if __name__ == '__main__':
    keep_alive()
    print("Multi-React System Active...")
    main_listener.infinity_polling()
